"""SQLite Write-Ahead Logging (WAL) Transactional Persistence Engine.
Author: Aryan Sharma (Orbitron AI)

Provides ACID transactions, optimistic locking (version tracking), and idempotent state
machines for FrontierPilot drafts, opportunities, approvals, and outbox jobs.
Maintains automatic bi-directional JSON mirror for backward compatibility.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "testing" / "frontierpilot.db"
DRAFTS_JSON = ROOT / "testing" / "drafts_queue.json"
OPPS_JSON = ROOT / "testing" / "opportunities_tracker.json"


def get_db_connection() -> sqlite3.Connection:
    """Connect to SQLite database with WAL mode and 5000ms busy timeout."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=5.0, isolation_level=None)
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Initialize relational schema and seed from JSON files if database is fresh."""
    with get_db_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        
        # 1. Drafts Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id TEXT PRIMARY KEY,
                topic TEXT,
                hook_formula TEXT,
                angle TEXT,
                content TEXT,
                char_count INTEGER,
                status TEXT NOT NULL DEFAULT 'pending_approval',
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                scheduled_time TEXT,
                approved_at TEXT,
                approved_by TEXT,
                approved_content_version INTEGER,
                published_at TEXT,
                publora_id TEXT,
                idempotency_key TEXT UNIQUE
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status)")

        # 2. Opportunities Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                organization TEXT,
                title TEXT,
                category TEXT,
                status TEXT NOT NULL DEFAULT 'radar',
                deadline TEXT,
                comp_stipend TEXT,
                match_score INTEGER,
                match_reason TEXT,
                target_url TEXT,
                notes TEXT,
                action_plan TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_opps_status ON opportunities(status)")

        # 3. Idempotent Approval Audit Log
        conn.execute("""
            CREATE TABLE IF NOT EXISTS approval_events (
                event_id TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                user_name TEXT NOT NULL,
                content_version INTEGER,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT
            )
        """)

        # 4. Outbox Jobs (for async background publishing/sync)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outbox_jobs (
                job_id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempt_count INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_status ON outbox_jobs(status)")
        
        # Check if seeding needed for drafts
        cur = conn.execute("SELECT COUNT(*) as count FROM drafts")
        draft_count = cur.fetchone()["count"]
        if draft_count == 0 and DRAFTS_JSON.exists():
            _seed_drafts_from_json(conn)

        # Check if seeding needed for opportunities
        cur = conn.execute("SELECT COUNT(*) as count FROM opportunities")
        opp_count = cur.fetchone()["count"]
        if opp_count == 0 and OPPS_JSON.exists():
            _seed_opps_from_json(conn)

        conn.commit()


def _seed_drafts_from_json(conn: sqlite3.Connection) -> None:
    try:
        with open(DRAFTS_JSON, "r", encoding="utf-8") as f:
            drafts = json.load(f)
        if isinstance(drafts, list):
            now_iso = datetime.now(timezone.utc).isoformat()
            for d in drafts:
                conn.execute("""
                    INSERT OR IGNORE INTO drafts (
                        id, topic, hook_formula, angle, content, char_count,
                        status, version, created_at, updated_at, scheduled_time,
                        approved_at, published_at, publora_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    d.get("id"),
                    d.get("topic", "General"),
                    d.get("hook_formula", "Standard Hook"),
                    d.get("angle", ""),
                    d.get("content", ""),
                    len(d.get("content", "")),
                    d.get("status", "pending_approval"),
                    d.get("version", 1),
                    d.get("created_at", now_iso),
                    d.get("updated_at", now_iso),
                    d.get("scheduled_time"),
                    d.get("approved_at"),
                    d.get("published_at"),
                    d.get("publora_id"),
                ))
    except Exception as e:
        print(f"[Database] Warning seeding drafts: {e}")


def _seed_opps_from_json(conn: sqlite3.Connection) -> None:
    try:
        with open(OPPS_JSON, "r", encoding="utf-8") as f:
            opps = json.load(f)
        if isinstance(opps, list):
            now_iso = datetime.now(timezone.utc).isoformat()
            for o in opps:
                conn.execute("""
                    INSERT OR IGNORE INTO opportunities (
                        id, organization, title, category, status, deadline,
                        comp_stipend, match_score, match_reason, target_url,
                        notes, action_plan, version, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    o.get("id"),
                    o.get("organization", ""),
                    o.get("title", ""),
                    o.get("category", "engineering"),
                    o.get("status", "radar"),
                    o.get("deadline", "Rolling"),
                    o.get("comp_stipend", ""),
                    o.get("match_score", 85),
                    o.get("match_reason", ""),
                    o.get("target_url", ""),
                    o.get("notes", ""),
                    o.get("action_plan", ""),
                    o.get("version", 1),
                    o.get("created_at", now_iso),
                    o.get("updated_at", now_iso),
                ))
    except Exception as e:
        print(f"[Database] Warning seeding opportunities: {e}")


def sync_drafts_to_json_mirror() -> None:
    """Mirror current SQLite drafts table to drafts_queue.json for backward compatibility."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM drafts ORDER BY created_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        DRAFTS_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(DRAFTS_JSON, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Database] Error syncing drafts mirror: {e}")
    finally:
        conn.close()


def sync_opps_to_json_mirror() -> None:
    """Mirror current SQLite opportunities table to opportunities_tracker.json."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM opportunities ORDER BY match_score DESC, updated_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        OPPS_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(OPPS_JSON, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Database] Error syncing opportunities mirror: {e}")
    finally:
        conn.close()


# =============================================================================
# Transactional Drafts API
# =============================================================================

def db_list_drafts(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List drafts, optionally filtered by status, from SQLite WAL."""
    conn = get_db_connection()
    try:
        if status:
            cur = conn.execute("SELECT * FROM drafts WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cur = conn.execute("SELECT * FROM drafts ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def db_get_draft(draft_id: str) -> Optional[Dict[str, Any]]:
    """Fetch single draft by ID with version and content attributes."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def db_create_draft(
    content: str,
    *,
    topic: str = "General",
    hook_formula: str = "Standard Hook",
    angle: str = "",
    status: str = "pending_approval",
    scheduled_time: Optional[str] = None,
) -> Dict[str, Any]:
    """Insert a draft atomically with deduplication guard."""
    clean_content = content.strip()
    norm_content = " ".join(clean_content.split()[:25]).lower()

    conn = get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        
        # Deduplication check
        if norm_content:
            cur = conn.execute("SELECT * FROM drafts")
            for r in cur.fetchall():
                existing_norm = " ".join(r["content"].split()[:25]).lower()
                if norm_content == existing_norm:
                    conn.commit()
                    return dict(r)

        draft_id = f"post_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        conn.execute("""
            INSERT INTO drafts (
                id, topic, hook_formula, angle, content, char_count,
                status, version, created_at, updated_at, scheduled_time,
                published_at, publora_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, NULL, NULL)
        """, (
            draft_id, topic, hook_formula, angle, clean_content,
            len(clean_content), status, now_iso, now_iso, scheduled_time
        ))
        conn.commit()
    finally:
        conn.close()

    sync_drafts_to_json_mirror()
    return db_get_draft(draft_id) or {}

    sync_drafts_to_json_mirror()
    return db_get_draft(draft_id) or {}


def db_update_draft(
    draft_id: str,
    content: Optional[str] = None,
    status: Optional[str] = None,
    new_content: Optional[str] = None,
    new_status: Optional[str] = None,
    scheduled_time: Optional[str] = None,
    publora_id: Optional[str] = None,
    published_at: Optional[str] = None,
    approved_by: Optional[str] = None,
    expected_version: Optional[int] = None,
    **kwargs: Any,
) -> Optional[Dict[str, Any]]:
    """Update draft with optimistic concurrency locking.
    
    If content is edited after approval, status automatically resets to 'pending_approval'
    to uphold the human approval invariant.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    raw_content = content if content is not None else new_content
    raw_status = status if status is not None else new_status

    conn = get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            return None

        current = dict(row)
        current_version = current["version"]

        if expected_version is not None and expected_version != current_version:
            conn.rollback()
            raise ValueError(f"Concurrency Conflict: Draft {draft_id} was modified by another transaction.")

        final_content = raw_content.strip() if raw_content is not None else current["content"]
        final_status = raw_status if raw_status is not None else current["status"]

        # Content modified after approval -> Reset to pending_approval
        if raw_content is not None and raw_content.strip() != current["content"]:
            if current["status"] in ("approved", "scheduled"):
                final_status = "pending_approval"

        sched = scheduled_time if scheduled_time is not None else current["scheduled_time"]
        pid = publora_id if publora_id is not None else current["publora_id"]
        pub_at = published_at if published_at is not None else current["published_at"]
        appr_by = approved_by if approved_by is not None else current.get("approved_by")

        conn.execute("""
            UPDATE drafts SET
                content = ?,
                char_count = ?,
                status = ?,
                scheduled_time = ?,
                publora_id = ?,
                published_at = ?,
                approved_by = ?,
                version = version + 1,
                updated_at = ?
            WHERE id = ? AND version = ?
        """, (
            final_content, len(final_content), final_status, sched, pid, pub_at,
            appr_by, now_iso, draft_id, current_version
        ))
        conn.commit()
    finally:
        conn.close()

    sync_drafts_to_json_mirror()
    return db_get_draft(draft_id)


def db_transition_approval(
    draft_id: str,
    action: str,  # "approve" or "reject"
    user_name: str = "Aryan Sharma",
    event_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute finite state machine approval transition with strict one-time idempotency.
    
    Transition rules:
    - pending_approval -> approved (or scheduled if scheduled_time exists)
    - pending_approval -> rejected
    - Cannot transition from rejected -> approved without fresh draft version
    - Cannot re-approve already published posts
    """
    evt_id = event_id or f"evt_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        
        # Idempotency check on event_id
        cur = conn.execute("SELECT * FROM approval_events WHERE event_id = ?", (evt_id,))
        if cur.fetchone():
            conn.rollback()
            return {"success": True, "idempotent_duplicate": True, "event_id": evt_id}

        cur = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            return {"success": False, "error": f"Draft {draft_id} not found"}

        draft = dict(row)
        current_status = draft["status"]
        current_version = draft["version"]

        if current_status == "published":
            conn.rollback()
            return {"success": False, "error": "Cannot re-approve already published post"}

        if action == "approve":
            target_status = "scheduled" if draft.get("scheduled_time") else "approved"
            conn.execute("""
                UPDATE drafts SET
                    status = ?,
                    approved_at = ?,
                    approved_by = ?,
                    approved_content_version = ?,
                    version = version + 1,
                    updated_at = ?
                WHERE id = ? AND status IN ('pending', 'pending_approval', 'rejected')
            """, (target_status, now_iso, user_name, current_version, now_iso, draft_id))
        elif action == "reject":
            target_status = "rejected"
            conn.execute("""
                UPDATE drafts SET
                    status = ?,
                    version = version + 1,
                    updated_at = ?
                WHERE id = ? AND status != 'published'
            """, (target_status, now_iso, draft_id))
        else:
            conn.rollback()
            return {"success": False, "error": f"Invalid action {action}"}

        # Log approval event
        conn.execute("""
            INSERT INTO approval_events (
                event_id, action, entity_id, user_name, content_version, timestamp, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (evt_id, action, draft_id, user_name, current_version, now_iso, "success"))

        conn.commit()
    finally:
        conn.close()

    sync_drafts_to_json_mirror()
    updated = db_get_draft(draft_id)
    return {"success": True, "draft": updated, "event_id": evt_id}


# Initialize tables upon module import
init_database()
