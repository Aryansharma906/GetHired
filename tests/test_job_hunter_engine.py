"""Tests for Job Hunter AI Engine (Vaibhav Sisinty & Mayank Joshi workflows)."""
from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from lib.job_hunter_engine import JobHunterEngine


class TestJobHunterEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = JobHunterEngine()
        self.engine.output_dir = self.temp_dir / "bundles"
        self.engine.output_dir.mkdir(parents=True, exist_ok=True)

        self.opp = {
            "id": "opp_test_anthropic",
            "title": "Model Alignment & Red-Teaming Research Fellow",
            "organization": "Anthropic",
            "category": "Fellowship / Research",
            "match_reason": "Published research on prompt injection and red-teaming LLMs.",
            "match_score": 98,
        }

    def test_generate_ats_resume_fallback_structure(self):
        with patch.object(self.engine, "_call_gemini_json", return_value={
            "ats_keywords": ["LLM Alignment", "Red-Teaming", "Python"],
            "professional_summary": "Researcher focused on model safety.",
            "tailored_markdown": "# Aryan Sharma\n## Experience\n- Red-teamed models at Handshake."
        }):
            res = self.engine.generate_ats_resume(self.opp)
            self.assertIn("ats_keywords", res)
            self.assertIn("tailored_markdown", res)
            self.assertIn("Aryan Sharma", res["tailored_markdown"])

    def test_generate_value_cover_letter(self):
        with patch.object(self.engine, "_call_gemini_text", return_value="Dear Anthropic Team, I evaluate LLMs."):
            letter = self.engine.generate_value_cover_letter(self.opp)
            self.assertTrue(len(letter) > 10)
            self.assertIn("Anthropic", letter)

    def test_generate_recruiter_outreach_dm(self):
        with patch.object(self.engine, "_call_gemini_text", return_value="Hi team at Anthropic, loved your work. Benchmarked models at Handshake."):
            dm_data = self.engine.generate_recruiter_outreach_dm(self.opp)
            self.assertIn("linkedin_dm_3_sentences", dm_data)
            self.assertIn("cold_email_subject", dm_data)
            # Check that it includes Aryan's work or Anthropic
            self.assertTrue("Anthropic" in dm_data["linkedin_dm_3_sentences"] or "Handshake" in dm_data["linkedin_dm_3_sentences"])

    def test_generate_proof_of_work_plan(self):
        plan = self.engine.generate_proof_of_work_plan(self.opp)
        self.assertIn("90-Day", plan)
        self.assertIn("Aryan Sharma", plan)

    def test_generate_interview_prep_guide(self):
        prep = self.engine.generate_interview_prep_guide(self.opp)
        self.assertIn("technical_questions", prep)
        self.assertIn("system_design_challenge", prep)
        self.assertIn("behavioral_star_scenarios", prep)
        self.assertTrue(len(prep["technical_questions"]) >= 1)

    def test_create_complete_application_bundle(self):
        bundle = self.engine.create_complete_application_bundle(self.opp)
        self.assertTrue(bundle["success"])
        self.assertTrue(Path(bundle["zip_path"]).exists())
        self.assertTrue(bundle["zip_filename"].endswith(".zip"))

        # Verify ZIP archive contents
        with zipfile.ZipFile(bundle["zip_path"], "r") as z:
            names = z.namelist()
            self.assertTrue(any(n.endswith(".docx") for n in names))
            self.assertTrue(any(n.endswith(".md") for n in names))
            self.assertTrue(any("Recruiter_LinkedIn_Outreach_DM" in n for n in names))
            self.assertTrue(any("NotebookLM_Interview_Prep" in n for n in names))


if __name__ == "__main__":
    unittest.main()
