"""Drafts queue storage layer for LinkedIn automation.

Stores drafts in testing/drafts_queue.json so that drafts persist across
pipeline runs, Slack approvals, and scheduling.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
QUEUE_FILE = ROOT / "testing" / "drafts_queue.json"


def _read_queue() -> list[dict[str, Any]]:
    if not QUEUE_FILE.exists():
        return []
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _write_queue(drafts: list[dict[str, Any]]) -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(drafts, f, indent=2, ensure_ascii=False)


def create_draft(
    content: str,
    *,
    topic: str = "General",
    hook_formula: str = "Standard Hook",
    angle: str = "",
    status: str = "pending_approval",
    scheduled_time: Optional[str] = None,
) -> dict[str, Any]:
    """Create and store a new draft with deduplication guard."""
    clean_content = content.strip()
    norm_content = " ".join(clean_content.split()[:25]).lower()
    drafts = _read_queue()

    # Prevent creating duplicate drafts with the same opening
    if norm_content:
        for existing in drafts:
            existing_norm = " ".join(existing.get("content", "").split()[:25]).lower()
            if norm_content == existing_norm:
                return existing

    draft_id = f"post_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    draft = {
        "id": draft_id,
        "topic": topic,
        "hook_formula": hook_formula,
        "angle": angle,
        "content": clean_content,
        "char_count": len(clean_content),
        "status": status,
        "created_at": now_iso,
        "scheduled_time": scheduled_time,
        "published_at": None,
        "publora_id": None,
    }

    drafts = _read_queue()
    drafts.insert(0, draft)
    _write_queue(drafts)
    return draft


def get_draft(draft_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a draft by ID."""
    drafts = _read_queue()
    for d in drafts:
        if d.get("id") == draft_id:
            return d
    return None


def list_drafts(status: Optional[str] = None) -> list[dict[str, Any]]:
    """List drafts, optionally filtered by status."""
    drafts = _read_queue()
    if status:
        return [d for d in drafts if d.get("status") == status]
    return drafts


def update_draft_status(
    draft_id: str,
    status: str,
    **kwargs: Any,
) -> Optional[dict[str, Any]]:
    """Update draft status and optional extra metadata."""
    drafts = _read_queue()
    updated = None
    for d in drafts:
        if d.get("id") == draft_id:
            d["status"] = status
            d.update(kwargs)
            updated = d
            break
    if updated:
        _write_queue(drafts)
    return updated
