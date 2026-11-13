"""Tests for Dossier Unified Integration Bridge."""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from lib.dossier_integrator import DossierIntegrator, ARYAN_PROFILE


class TestDossierIntegrator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.integrator = DossierIntegrator()
        self.integrator.opps_path = self.temp_dir / "opportunities_test.json"
        self.integrator.staging_dir = self.temp_dir / "exports"
        self.integrator.staging_dir.mkdir(parents=True, exist_ok=True)

        self.sample_opps = [
            {
                "id": "opp_test_1",
                "title": "AI Systems Fellow",
                "organization": "OpenAI Residency",
                "category": "Fellowship",
                "deadline": "Rolling",
                "stipend": "$15,000/mo",
                "status": "Active",
                "url": "https://openai.com/careers",
                "match_reason": "High synergy with systems evaluation.",
                "tags": ["AI", "Systems"]
            }
        ]
        self.integrator.save_opportunities(self.sample_opps)

    def test_load_and_save_opportunities(self):
        loaded = self.integrator.load_opportunities()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["title"], "AI Systems Fellow")
        self.assertEqual(loaded[0]["organization"], "OpenAI Residency")

    def test_profile_integrity(self):
        self.assertEqual(ARYAN_PROFILE["name"], "Aryan Sharma")
        self.assertIn("Python", ARYAN_PROFILE["skills"]["languages"])
        self.assertIn("LLM Evaluation", ARYAN_PROFILE["skills"]["ai_ml"])

    def test_sync_to_google_sheets_staged(self):
        res = self.integrator.sync_to_google_sheets(self.sample_opps)
        self.assertTrue(res.get("success"))
        self.assertIn(res.get("mode"), ("staged_csv", "live_api"))

        csv_file = self.integrator.staging_dir / "google_sheets_pipeline.csv"
        self.assertTrue(csv_file.exists())
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.assertGreaterEqual(len(reader), 2)
            self.assertEqual(reader[0][0], "ID")
            self.assertEqual(reader[0][1], "Organization")
            self.assertEqual(reader[1][1], "OpenAI Residency")

    def test_sync_resumes_to_google_drive(self):
        res = self.integrator.sync_resumes_to_google_drive()
        self.assertTrue(res.get("success"))
        manifest_file = self.integrator.staging_dir / "google_drive_manifest.json"
        self.assertTrue(manifest_file.exists())
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertIsInstance(manifest, list)

    def test_sync_to_notion_staged(self):
        res = self.integrator.sync_to_notion(self.sample_opps)
        self.assertTrue(res.get("success"))
        self.assertIn(res.get("mode"), ("staged_csv", "live_notion_api"))

        csv_file = self.integrator.staging_dir / "notion_database_pipeline.csv"
        self.assertTrue(csv_file.exists())
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertGreaterEqual(len(reader), 1)
            self.assertEqual(reader[0]["Organization"], "OpenAI Residency")

    def test_scan_gmail_updates_format(self):
        res = self.integrator.scan_gmail_for_updates()
        self.assertTrue(res.get("success"))
        self.assertIn("mode", res)

    @patch("requests.post")
    def test_run_full_dossier_sync(self, mock_post):
        mock_post.return_value.status_code = 200
        summary = self.integrator.run_full_dossier_sync()
        self.assertIn("total_tracked_opportunities", summary)
        self.assertIn("google_sheets", summary)
        self.assertIn("google_drive", summary)
        self.assertIn("notion", summary)
        self.assertIn("gmail", summary)
        self.assertIn("gemini", summary)


if __name__ == "__main__":
    unittest.main()
