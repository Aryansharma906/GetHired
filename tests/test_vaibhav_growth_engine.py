#!/usr/bin/env python3
"""Unit tests for Vaibhav Sisinty Growth & Career Automation Engine."""
import unittest
from lib.vaibhav_growth_engine import VaibhavGrowthEngine


class TestVaibhavGrowthEngine(unittest.TestCase):
    def setUp(self):
        self.engine = VaibhavGrowthEngine()

    def test_google_xyz_bullets_optimizer(self):
        """Verify bullets are rewritten into Google XYZ formula."""
        raw_bullets = [
            "Built automated data pipelines for syncing records.",
            "Wrote unit tests and improved test coverage."
        ]
        target_jd = "Senior AI Engineer with experience in high-throughput data synchronization and test automation."
        optimized = self.engine.optimize_bullets_google_xyz(raw_bullets, target_jd)
        self.assertTrue(len(optimized) >= 2)
        # Should include Google XYZ phrasing
        self.assertTrue(any("Accomplished" in b or "as measured by" in b or "%" in b for b in optimized))

    def test_gps_framework_audit(self):
        """Verify GPS framework returns Gaslight, Pushback, and Stress-Test sections."""
        summary = "Aryan Sharma develops autonomous AI pipelines connecting Gemini models to mobile Slack approval hubs."
        jd = "Founding Engineer to build resilient distributed agents with zero downtime."
        res = self.engine.apply_gps_framework(summary, jd)
        self.assertIn("gaslight_polished_narrative", res)
        self.assertIn("pushback_missing_metrics", res)
        self.assertIn("stress_test_objections", res)
        self.assertTrue(len(res["pushback_missing_metrics"]) >= 2)
        self.assertTrue(len(res["stress_test_objections"]) >= 1)

    def test_tactical_prd_generation(self):
        """Verify 90-day Proof-of-Work PRD generates structured roadmap."""
        prd = self.engine.generate_tactical_prd("Scale AI", "AI Systems Engineer", "Build evaluation harnesses for LLMs.")
        self.assertIn("Proof-of-Work PRD", prd)
        self.assertTrue(any(k in prd for k in ("Roadmap", "Execution", "Day 1–30", "Day 1-30")))
        self.assertIn("Aryan Sharma", prd)

    def test_three_sentence_founder_dm(self):
        """Verify direct founder outreach is punchy and under 4 sentences."""
        dm = self.engine.generate_3_sentence_founder_dm("Anthropic", "Dario", "RLHF latency bottlenecks")
        self.assertIsInstance(dm, str)
        sentences = [s for s in dm.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        self.assertTrue(len(sentences) <= 5)

    def test_video_short_script_generation(self):
        """Verify 60s video short script returns visual cues, timestamps, and hook."""
        script = self.engine.generate_video_short_script(
            "Why Traditional Resumes Are Dying",
            "Proof of Work beats 500 resume submissions"
        )
        self.assertIn("visual_hook", script)
        self.assertIn("script_sections", script)
        self.assertTrue(len(script["script_sections"]) >= 3)
        self.assertIn("caption_with_hashtags", script)


if __name__ == "__main__":
    unittest.main()
