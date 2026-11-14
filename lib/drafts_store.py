"""Drafts queue storage layer for LinkedIn automation.
Backed by SQLite WAL Transaction Engine (lib/database.py) with backward-compatible JSON mirroring.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional
from lib.database import (
    db_create_draft,
    db_get_draft,
    db_list_drafts,
    db_update_draft,
    db_transition_approval,
    DRAFTS_JSON,
)

ROOT = Path(__file__).resolve().parents[1]
QUEUE_FILE = DRAFTS_JSON
update_draft = db_update_draft


def create_draft(
    content: str,
    *,
    topic: str = "General",
    hook_formula: str = "Standard Hook",
    angle: str = "",
    status: str = "pending_approval",
    scheduled_time: Optional[str] = None,
) -> dict[str, Any]:
    """Create and store a new draft with SQLite WAL deduplication and atomicity."""
    return db_create_draft(
        content,
        topic=topic,
        hook_formula=hook_formula,
        angle=angle,
        status=status,
        scheduled_time=scheduled_time,
    )


def get_draft(draft_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a draft by ID."""
    return db_get_draft(draft_id)


def list_drafts(status: Optional[str] = None) -> list[dict[str, Any]]:
    """List drafts, optionally filtered by status."""
    return db_list_drafts(status)


def _read_queue() -> list[dict[str, Any]]:
    return db_list_drafts()


def _write_queue(drafts: list[dict[str, Any]]) -> None:
    # Mirror sync helper for test harnesses
    pass


def update_draft_status(
    draft_id: str,
    status: str,
    *,
    scheduled_time: Optional[str] = None,
    publora_id: Optional[str] = None,
    published_at: Optional[str] = None,
    **kwargs: Any,
) -> Optional[dict[str, Any]]:
    """Update draft status atomically in SQLite WAL."""
    return db_update_draft(
        draft_id,
        new_status=status,
        scheduled_time=scheduled_time,
        publora_id=publora_id,
        published_at=published_at,
        **kwargs,
    )
