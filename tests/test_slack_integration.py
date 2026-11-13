"""Tests for Slack approval workflow and drafts queue."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import lib.drafts_store
from lib.drafts_store import (
    create_draft,
    get_draft,
    list_drafts,
    update_draft_status,
)
from lib.slack_approver import (
    build_slack_approval_blocks,
    process_slack_action,
)


TEMP_TEST_FILE = Path(tempfile.mktemp(suffix=".json"))
ORIG_QUEUE_FILE = lib.drafts_store.QUEUE_FILE


def setUpModule():
    lib.drafts_store.QUEUE_FILE = TEMP_TEST_FILE


def tearDownModule():
    lib.drafts_store.QUEUE_FILE = ORIG_QUEUE_FILE
    if TEMP_TEST_FILE.exists():
        TEMP_TEST_FILE.unlink()


class TestDraftsStore(unittest.TestCase):
    def test_create_and_retrieve_draft(self):
        draft = create_draft(
            content="This is a test post about AI and distribution.",
            topic="Test Distribution",
            hook_formula="F01",
        )
        self.assertIn("id", draft)
        self.assertEqual(draft["topic"], "Test Distribution")
        self.assertEqual(draft["status"], "pending_approval")

        fetched = get_draft(draft["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["content"], draft["content"])

    def test_update_draft_status(self):
        draft = create_draft(
            content="Another test post.",
            topic="Test Status",
        )
        updated = update_draft_status(draft["id"], "approved", approved_by="Aryan")
        self.assertIsNotNone(updated)
        self.assertEqual(updated["status"], "approved")
        self.assertEqual(updated["approved_by"], "Aryan")


class TestSlackApprover(unittest.TestCase):
    def test_build_slack_approval_blocks(self):
        draft = create_draft(
            content="Short test post content.",
            topic="Block Test",
            hook_formula="F02 Obituary",
        )
        blocks = build_slack_approval_blocks(draft)
        self.assertIsInstance(blocks, list)
        self.assertGreater(len(blocks), 3)

        # Verify Header and Actions blocks exist
        block_types = [b.get("type") for b in blocks]
        self.assertIn("header", block_types)
        self.assertIn("actions", block_types)
        self.assertIn("section", block_types)

    def test_process_reject_action(self):
        draft = create_draft(
            content="Post to reject.",
            topic="Reject Topic",
        )
        res = process_slack_action(f"reject:{draft['id']}", user_name="Aryan")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("action"), "rejected")
        updated = get_draft(draft["id"])
        self.assertEqual(updated["status"], "rejected")

    @patch("lib.active_backend", return_value="manual")
    def test_process_approve_action_manual(self, _mock_backend):
        draft = create_draft(
            content="Post to approve.",
            topic="Approve Topic",
        )
        res = process_slack_action(f"approve:{draft['id']}", user_name="Aryan")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("action"), "approved")
        updated = get_draft(draft["id"])
        self.assertEqual(updated["status"], "approved")


if __name__ == "__main__":
    unittest.main()
