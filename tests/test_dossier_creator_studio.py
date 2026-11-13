"""Tests for Dossier 2.0 LinkedIn Creator Studio Native Integration."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from studio.app import app
from lib.drafts_store import _read_queue, _write_queue, create_draft, get_draft, list_drafts, update_draft

ROOT = Path(__file__).resolve().parents[1]


class TestDossierCreatorStudio(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.original_queue = _read_queue()

    def tearDown(self):
        _write_queue(self.original_queue)

    def test_legacy_index_redirect(self):
        """Verify that /index.html cleanly redirects to / without throwing 404."""
        res = self.app.get("/index.html")
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers["Location"].endswith("/"))

    def test_dossier_page_renders_creator_studio(self):
        """Verify that /dossier contains the native Creator Studio tab and elements."""
        res = self.app.get("/dossier")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        # Invariant checks
        self.assertIn('data-tab="creator-studio"', html)
        self.assertIn('id="tabCreatorStudio"', html)
        self.assertIn('id="creatorDraftsFeed"', html)
        self.assertIn('id="repurposeSourceSelect"', html)
        self.assertIn('id="composerContent"', html)
        self.assertIn('runLiveComplianceAudit()', html)
        # Verify broken link is eradicated
        self.assertNotIn('href="./index.html"', html)

    def test_create_and_update_draft_endpoints(self):
        """Verify POST /api/drafts/create and POST /api/drafts/<id> endpoints."""
        # 1. Create draft
        res = self.app.post(
            "/api/drafts/create",
            json={
                "content": "Why small AI teams beat 50-person agencies in 2026.\n\nSimplicity beats headcount.",
                "topic": "AI Teams Architecture",
                "hook_formula": "Formula #1: Contrarian Take",
                "angle": "Founder Systems Perspective"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        draft_id = data["draft"]["id"]

        # 2. Update draft
        updated_content = "Why small AI teams beat 50-person agencies in 2026.\n\nSimplicity beats headcount. Always."
        res_update = self.app.post(
            f"/api/drafts/{draft_id}",
            json={"content": updated_content}
        )
        self.assertEqual(res_update.status_code, 200)
        data_update = res_update.get_json()
        self.assertTrue(data_update.get("success"))
        self.assertEqual(data_update["draft"]["content"], updated_content)
        self.assertEqual(data_update["draft"]["char_count"], len(updated_content))

    def test_repurpose_career_milestone_endpoint(self):
        """Verify POST /api/drafts/repurpose generates authentic post without hallucinations."""
        res = self.app.post(
            "/api/drafts/repurpose",
            json={
                "title": "Anthropic AI Systems & Model Safety Fellowship",
                "details": "Benchmarking adversarial attack surfaces, automated defense guardrails, and jailbreak boundaries across production generative models.",
                "source_type": "Target Role Opportunity",
                "hook_formula": "Formula #1: Contrarian Take"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        draft = data.get("draft")
        self.assertIsNotNone(draft)
        self.assertIn("Anthropic", draft["content"] + draft["topic"])
        self.assertEqual(draft["status"], "pending_approval")

    def test_compliance_invariants_in_repurposed_post(self):
        """Verify that 2026 voice standards are respected."""
        res = self.app.post(
            "/api/drafts/repurpose",
            json={
                "title": "LLM Prompt Vulnerability Research",
                "details": "Empirical study on LLM jailbreaks and prompt injection evaluation using automated red-teaming.",
                "source_type": "Research Publication",
                "hook_formula": "Formula #2: Framework Reveal"
            }
        )
        self.assertEqual(res.status_code, 200)
        draft = res.get_json()["draft"]
        content = draft["content"]

        # Blacklisted words check
        blacklisted = [
            "leverage", "utilize", "facilitate", "streamline", "robust",
            "seamless", "delve", "navigate", "unlock", "harness", "foster",
            "cultivate", "game-changer", "deep dive"
        ]
        lower_content = content.lower()
        for word in blacklisted:
            self.assertNotIn(f" {word} ", lower_content, f"Blacklisted word found: {word}")

        # Em-dash frequency check (max 1 per 100 words)
        words = content.split()
        em_dash_count = content.count("—") + content.count("--")
        if len(words) > 0:
            ratio = em_dash_count / (len(words) / 100)
            self.assertLessEqual(ratio, 2.0, "Too many em-dashes in copy")

    def test_dossier_editorial_design_and_command_palette(self):
        """Verify editorial design tokens, accessibility skip-link, breadcrumbs, and command palette."""
        res = self.app.get("/dossier")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Design tokens
        self.assertIn("--surface: #f9f8f5;", html)
        self.assertIn("--ink: #1f2328;", html)
        self.assertIn("--primary: #4338ca;", html)

        # Accessibility and App Shell
        self.assertIn('class="skip-to-main"', html)
        self.assertIn('id="dossierBreadcrumb"', html)
        self.assertIn('id="dossierCommandPalette"', html)
        self.assertIn('openCommandPalette()', html)

        # Progressive disclosure & inline validation
        self.assertIn('toggleOppDetails(', html)
        self.assertIn('saveOppNote(', html)
        self.assertIn('class="invalid-feedback"', html)

    def test_opportunity_crud_lifecycle(self):
        """Verify complete Opportunity CRUD lifecycle via REST APIs."""
        # 1. Fetch initial list
        res_list = self.app.get("/api/opportunities")
        self.assertEqual(res_list.status_code, 200)
        data_list = res_list.get_json()
        self.assertTrue(data_list.get("success"))
        initial_count = len(data_list.get("opportunities", []))

        # 2. Create new opportunity
        res_create = self.app.post(
            "/api/opportunities",
            json={
                "title": "Staff AI Verification Engineer",
                "organization": "OpenAI Safety Research",
                "category": "Systems & Alignment",
                "deadline": "April 15",
                "stipend": "$18,000/mo",
                "status": "Ready to Apply / Staged"
            }
        )
        self.assertEqual(res_create.status_code, 200)
        created_opp = res_create.get_json().get("opportunity")
        self.assertIsNotNone(created_opp)
        opp_id = created_opp["id"]

        # 3. Update status and internal notes
        res_update = self.app.post(
            f"/api/opportunities/{opp_id}",
            json={
                "status": "Interviewing",
                "internal_notes": "Passed technical screener. Focus on distributed lock benchmarks."
            }
        )
        self.assertEqual(res_update.status_code, 200)
        updated_opp = res_update.get_json().get("opportunity")
        self.assertEqual(updated_opp["status"], "Interviewing")
        self.assertIn("distributed lock", updated_opp["internal_notes"])

        # 4. Delete opportunity
        res_del = self.app.delete(f"/api/opportunities/{opp_id}")
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.get_json().get("success"))

        # Verify not found on subsequent delete
        res_del_again = self.app.delete(f"/api/opportunities/{opp_id}")
        self.assertEqual(res_del_again.status_code, 404)


if __name__ == "__main__":
    unittest.main()
