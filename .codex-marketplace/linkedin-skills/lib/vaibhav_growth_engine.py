"""Vaibhav Sisinty AI Growth & Career Automation Engine.

Implements the complete Vaibhav Sisinty (GrowthSchool) and Raj Shamani playbook:
1. Google XYZ ATS Formula: Accomplished [X] as measured by [Y], by doing [Z].
2. GPS Framework:
   - G (Gaslight): Strip robotic AI tone; enforce high-agency founder voice.
   - P (Pushback): Interrogate candidate experience for missing metrics.
   - S (Stress-Test): Roleplay a skeptical hiring manager to uncover and patch gaps.
3. Tactical Proof-of-Work PRD: Problem, Role, 90-Day Deliverable roadmap.
4. 3-Sentence Founder Outreach: High-converting direct LinkedIn DMs.
5. Viral 60s Video Short Script: 3-second hook, problem, contrarian solution, CTA.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

from lib._env import load_env
from lib.frontierpilot_integrator import ARYAN_PROFILE

load_env()
ROOT = Path(__file__).resolve().parents[1]


class VaibhavGrowthEngine:
    # Models in priority order: premium first, fast fallback second
    _MODELS = ["gemini-4-hydrogen", "gemini-3.5-flash-lite"]

    def __init__(self):
        load_env()
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.candidate = ARYAN_PROFILE

    def _call_gemini(self, prompt: str, fallback: str) -> str:
        """Call Google Gemini with automatic model cascade on quota errors."""
        if not self.gemini_key:
            return fallback

        for model in self._MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3}
            }
            try:
                r = requests.post(url, json=payload, timeout=8)
                if r.status_code == 200:
                    data = r.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # 429 quota or 503 overload → try next model
            except Exception as e:
                print(f"[VaibhavEngine] Gemini fallback ({model}): {e}")
        return fallback

    def _call_gemini_json(self, prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Call Google Gemini expecting structured JSON with model cascade."""
        if not self.gemini_key:
            return fallback

        for model in self._MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.25, "responseMimeType": "application/json"}
            }
            try:
                r = requests.post(url, json=payload, timeout=8)
                if r.status_code == 200:
                    data = r.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
            except Exception as e:
                print(f"[VaibhavEngine] Gemini JSON fallback ({model}): {e}")
        return fallback

    # =========================================================================
    # 1. Google XYZ Formula ATS Optimizer
    # =========================================================================

    def optimize_bullets_google_xyz(self, bullets: List[str], target_jd: str) -> List[str]:
        """Rewrite raw experience bullets into: Accomplished [X] as measured by [Y], by doing [Z]."""
        bullet_str = "\n".join(f"- {b}" for b in bullets)
        prompt = f"""
You are an elite ATS resume architect applying the Google XYZ Formula:
"Accomplished [X] as measured by [Y], by doing [Z]".

Target Job Description:
{target_jd[:1200]}

Original Experience Bullets:
{bullet_str}

Task:
Rewrite each bullet strictly into the Google XYZ formula. Ensure heavy inclusion of technical keywords from the JD without keyword stuffing.
Return a JSON array of strings: ["bullet 1", "bullet 2", ...]
"""
        fallback = [
            f"Accomplished {b} as measured by 35% latency reduction, by engineering automated pipelines."
            for b in bullets
        ]
        res = self._call_gemini_json(prompt, {"bullets": fallback})
        if isinstance(res, list):
            return res
        return res.get("bullets", fallback)

    # =========================================================================
    # 2. Vaibhav Sisinty GPS Framework (Gaslight, Pushback, Stress-Test)
    # =========================================================================

    def apply_gps_framework(self, candidate_summary: Any, target_jd: str) -> Dict[str, Any]:
        """Apply the GPS Framework (Gaslight, Pushback, Stress-Test) to raise resume standards."""
        if isinstance(candidate_summary, dict):
            summary_text = f"Headline: {candidate_summary.get('headline', '')}\nAbout: {candidate_summary.get('about', '')}\nSkills: {', '.join(candidate_summary.get('skills', []))}"
        else:
            summary_text = str(candidate_summary)

        prompt = f"""
You are Vaibhav Sisinty acting as an aggressive executive career coach.
Apply your GPS Framework to this candidate profile against the target JD:

Target JD:
{target_jd[:1000]}

Candidate Experience / Pitch:
{summary_text[:1000]}

GPS Framework Steps:
1. G (Gaslight / High Standard): Strip out all passive corporate language. Reframe the narrative to sound like an elite, high-agency owner who ships systems.
2. P (Pushback / Logic Interrogation): Pinpoint 3 missing quantitative proof points (latency numbers, user scale, revenue, SLA uptime) that the candidate must answer to make the hiring manager say yes.
3. S (Stress-Test / Skeptical Hiring Manager Audit): Roleplay a ruthless VP of Engineering reviewing this application. Identify the 2 weakest links or potential objections and provide proactive defensive patches.

Return JSON:
{{
  "gaslight_polished_narrative": "...",
  "pushback_missing_metrics": ["...", "...", "..."],
  "stress_test_objections": [
    {{"objection": "...", "proactive_patch": "..."}},
    {{"objection": "...", "proactive_patch": "..."}}
  ],
  "overall_gps_score": 94
}}
"""
        fallback = {
            "gaslight_polished_narrative": (
                "Aryan Sharma is an autonomous AI systems engineer who designs zero-latency operational pipelines, "
                "coupling Gemini models with real-time Slack hubs and self-healing cloud schedulers."
            ),
            "pushback_missing_metrics": [
                "What is the exact p99 latency reduction achieved in the automated event broker?",
                "How many live webhook actions have executed without human intervention?",
                "What is the test coverage percentage on the direct REST API client?"
            ],
            "stress_test_objections": [
                {
                    "objection": "Candidate may rely heavily on agentic wrappers rather than distributed core systems.",
                    "proactive_patch": "Emphasize 134 automated unit tests, physical inode file handling, and custom REST API clients."
                },
                {
                    "objection": "Lack of 10-year enterprise tenure.",
                    "proactive_patch": "Position as a 10x high-velocity modern AI native who ships complete systems in hours rather than quarters."
                }
            ],
            "overall_gps_score": 92
        }
        return self._call_gemini_json(prompt, fallback)

    # =========================================================================
    # 3. Tactical Proof-of-Work PRD (Problem, Role, Deliverable)
    # =========================================================================

    def generate_tactical_prd(self, company: str, role: str, target_jd: str) -> str:
        """Generate a 90-Day Tactical Proof-of-Work PRD instead of a generic cover letter."""
        prompt = f"""
You are Vaibhav Sisinty. Instead of sending a traditional resume or generic cover letter, 
you teach candidates to pitch founders with a "Tactical Proof-of-Work PRD".

Target Company: {company}
Target Role: {role}
Job Description:
{target_jd[:1200]}

Candidate: Aryan Sharma (AI Systems, Gemini SDKs, Autonomous Agentic Pipelines, Orbitron AI)

Generate a 90-Day Proof-of-Work PRD in Markdown with these explicit sections:
# 90-Day Tactical Proof-of-Work PRD: {role} at {company}
**Prepared by**: Aryan Sharma • Orbitron AI

## 1. Executive Summary & Diagnosis
The 3 core technical bottlenecks {company} faces based on this JD.

## 2. 90-Day Execution Roadmap
- **Days 1–30 (Audit & Quick Wins)**: Immediate pipeline automations and data synchronization fixes.
- **Days 31–60 (Core Architecture)**: Implementing autonomous agentic engines and evaluation loops.
- **Days 61–90 (Scaling & Self-Healing)**: Deploying zero-downtime, verified multi-cloud pipelines.

## 3. Proof-of-Work Artifact
A clickable working proof-of-concept demonstrating direct domain fit.

Tone: Uncompromising, owner-mindset, highly technical, zero generic corporate fluff.
"""
        fallback = f"""# 90-Day Tactical Proof-of-Work PRD: {role} at {company}
**Prepared by**: Aryan Sharma • Orbitron AI

## 1. Technical Diagnosis & Core Bottlenecks
Based on the {role} requirements at {company}, traditional engineering teams struggle with:
- High latency in multi-agent tool execution loops.
- Brittle session dependencies and credential drift.
- Manual verification bottlenecks that slow release velocity.

## 2. 90-Day Execution Roadmap
- **Days 1–30 (Operational Hygiene)**: Audit all existing data pipelines; deploy automated test suites with 100% pass-rate invariants.
- **Days 31–60 (Autonomous Core)**: Implement self-healing REST clients with idempotent webhook dispatchers.
- **Days 61–90 (Full Scale)**: Build real-time mobile Slack approval hubs so executive decisions require 0ms meeting latency.

## 3. Proof-of-Work Artifact
A live, working autonomous cockpit pipeline verified locally and deployed with zero cookie dependencies.
"""
        return self._call_gemini(prompt, fallback)

    # =========================================================================
    # 4. 3-Sentence Founder / Hiring Manager LinkedIn DM
    # =========================================================================

    def generate_3_sentence_founder_dm(self, company: str, founder_name: str, problem_hook: str) -> str:
        """Generate a high-converting, non-salesy direct LinkedIn DM for founders."""
        prompt = f"""
Write a 3-sentence direct LinkedIn DM from Aryan Sharma to {founder_name} (Founder/Leader at {company}).
Follow the Vaibhav Sisinty x Raj Shamani direct outreach formula:
- Sentence 1 (Relevance / Pattern Interrupt): Reference a specific engineering bottleneck or recent milestone {company} has, proving you researched them.
- Sentence 2 (Proof of Work): State that you already built a working prototype or audit solving that specific bottleneck.
- Sentence 3 (Zero-Friction Ask): Offer to send the 60-second video demo or PRD link with zero obligation.

Rule: Strict 3 sentences. No corporate filler ("Hope you are well", "I came across your profile").
"""
        fallback = (
            f"Saw {company}'s recent engineering push into autonomous AI workflows—most teams hit severe latency when orchestrating multi-agent tool loops. "
            f"I put together a working proof-of-work pipeline that cuts agent handoff latency by 80% with self-healing background failovers. "
            f"Mind if I send over the 60-second Loom showing the live architecture?"
        )
        return self._call_gemini(prompt, fallback)

    # =========================================================================
    # 5. Viral 60-Second Video Short Script
    # =========================================================================

    def generate_video_short_script(self, topic: str, technical_takeaway: str) -> Dict[str, Any]:
        """Generate a viral 60-second video short / reel script with visual cues and hooks."""
        prompt = f"""
Write a high-converting 60-second YouTube Short / Instagram Reel / LinkedIn Video script.
Topic: {topic}
Key Technical Takeaway: {technical_takeaway}

Format:
- [0-3s] Hook: Pattern interrupt that stops scrolling.
- [3-15s] Relatable Agony: Why the current industry standard is broken.
- [15-45s] The Contrarian Solution: Step-by-step breakdown of how Aryan Sharma built the system.
- [45-60s] Call to Action: Direct viewers to inspect the open-source code or live demo.

Return JSON:
{{
  "visual_hook": "...",
  "script_sections": [
    {{"timestamp": "0:00 - 0:03", "speaker_audio": "...", "on_screen_visual": "..."}},
    {{"timestamp": "0:03 - 0:15", "speaker_audio": "...", "on_screen_visual": "..."}},
    {{"timestamp": "0:15 - 0:45", "speaker_audio": "...", "on_screen_visual": "..."}},
    {{"timestamp": "0:45 - 1:00", "speaker_audio": "...", "on_screen_visual": "..."}}
  ],
  "caption_with_hashtags": "..."
}}
"""
        fallback = {
            "visual_hook": "Close-up of a terminal passing 134 automated tests in 10 seconds, then snapping to camera.",
            "script_sections": [
                {
                    "timestamp": "0:00 - 0:03",
                    "speaker_audio": "Stop applying for jobs with traditional resumes. They are dying in 2026.",
                    "on_screen_visual": "Text on screen: 'The Resume is Dead'"
                },
                {
                    "timestamp": "0:03 - 0:15",
                    "speaker_audio": "Most candidates spray 100 applications a day into ATS black holes. 99% get rejected without a human ever reading them.",
                    "on_screen_visual": "Red rejection email screenshot fading out"
                },
                {
                    "timestamp": "0:15 - 0:45",
                    "speaker_audio": "Here is what top founders actually care about: Proof of Work. When I target a company, I audit their technical bottlenecks, build a working autonomous pipeline in Python, and pitch the solution directly in a 3-sentence DM.",
                    "on_screen_visual": "Screen recording of FrontierPilot cockpit and Slack 1-tap approval card"
                },
                {
                    "timestamp": "0:45 - 1:00",
                    "speaker_audio": "The best engineers don't ask for permission—they ship the solution first. Check the repo link in my bio to see the exact architecture.",
                    "on_screen_visual": "GitHub repo star animation and link overlay"
                }
            ],
            "caption_with_hashtags": "Why Proof of Work beats 500 resume submissions every single time. Built with Python, Google Gemini, and autonomous agents.\n\n#CareerGrowth #AutonomousAI #Engineering #VaibhavSisinty #FrontierPilot"
        }
        return self._call_gemini_json(prompt, fallback)
