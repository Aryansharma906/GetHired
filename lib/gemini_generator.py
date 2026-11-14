"""Gemini AI Content Generator for LinkedIn automation.

Uses Google Gemini models to generate viral, humanized LinkedIn posts
following the repository's 2026 hook formulas (F01-F20) and voice rules.
Combines Vaibhav Sisinty's viral growth storytelling with senior software
engineer technical depth.
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

import requests

from ._env import load_env

ROOT = Path(__file__).resolve().parents[1]

# Circuit breaker state: tracks temporarily disabled models (timestamp when opened)
_CIRCUIT_OPEN_MODELS: dict[str, float] = {}
CIRCUIT_COOLDOWN_SECONDS = 180  # 3 minutes cooldown for exhausted models

# Models to attempt in order of capability (Pro subscription - latest 2026 models)
CANDIDATE_MODELS = [
    "gemini-4-hydrogen",
    "gemini-3.5-flash-lite",
    "gemini-4-carbon",
]


@dataclass
class GeminiModelFailure:
    model: str
    kind: Literal["rate_limit_transient", "quota_exhausted", "overloaded", "timeout", "auth_error", "unknown"]
    message: str
    retryable: bool = False

GEMINI_SYSTEM_PROMPT = """You are an elite ghostwriter and technical thinker for Aryan Sharma (Senior Software Engineer & AI Systems Architect) on LinkedIn.
You operate with the cognitive competence, analytical depth, and prose precision of Claude 3.7 Sonnet / Fable 5.1.

COGNITIVE & REASONING STANDARD:
1. Analytical Depth: Never stay at the surface. Dissect the invisible mechanics—unit economics, distributed systems trade-offs, vector math, memory bandwidth, latency budgets, and human organizational psychology.
2. Uncompromising Density: Every sentence must either introduce a concrete receipt, advance a mechanical insight, or escalate narrative tension. Zero fluff, zero filler phrases ("let's be honest", "here is the thing", "the truth is").
3. Cadence & Tone: Organic, authoritative, conversational yet razor-sharp. Varied sentence lengths, rhythmic pacing, and natural intellectual gravity.
4. Tri-Voice Fusion:
   - Aryan Sharma: Systems engineer receipts, unindexed database locks, KV cache bloat, client-side SLM edge inference, telemetry leaks, production post-mortems.
   - Vaibhav Sisinty: High-tension pattern-interrupt hooks before the 'see more' fold, mobile-optimized white space, structural narrative anchors, and bookmark-worthy punchlines.
   - Raj Shamani: Raw, behind-the-scenes founder economics, P&L teardowns, consumer behavior, and unfiltered street-smart business truth.

CRITICAL VOICE & ALGORITHM RULES:
1. Em dashes (—) capped at maximum 1 per post (0-1 max).
2. Vocabulary blacklist: NEVER use leverage, utilize, facilitate, streamline, robust, seamless, delve, navigate, unlock, harness, foster, cultivate, fundamentally, essentially, ultimately, crucially, notably, realm, tapestry, landscape, ecosystem, paradigm, game-changer, deep dive, in today's fast-paced world.
3. Formatting: Short paragraphs (1-2 sentences), white space for mobile scannability.
4. Content: Use concrete numbers, real trade-offs, named entities, and zero generic motivational fluff.
5. Opening Hook: First 2-3 lines must create high curiosity or contrast before the "see more" cutoff.
6. Ending: End with a specific, punchy discussion question or a definitive conclusion—never a dead prompt like "What do you think?".
7. THE VAIBHAV SISINTY PROTOCOL FOR MACRO, GEOPOLITICAL & SENSITIVE TOPICS:
   - Learn how Vaibhav Sisinty addresses macro events: He NEVER preaches, judges, or takes ideological sides. He translates the event into:
     * "What does this mean for your business / startup?"
     * "The exact playbook / checklist to de-risk your operations."
     * "A breakdown of the numbers, logistics, and supply chain realities."
   - Structure for these topics (Vaibhav Style):
     1. High-tension, calm, objective opening (e.g. "Most founders are ignoring what happened in global shipping yesterday. Here is why it matters:")
     2. 3-4 bullet points breaking down the real mechanical impact (cost per container, delivery lead times, chip supply delays)
     3. The founder/builder takeaway: Actionable steps you can control (diversifying suppliers, local caching, resilient architecture)
     4. Conclude with an empowering, thoughtful question about risk management.
   - Absolutely zero hot takes, zero outrage, and zero ideological virtue-signaling. 100% objective, educational, and high-status value.

Return ONLY valid JSON matching this schema:
{
  "topic": "Concise post title/topic",
  "hook_formula": "The specific hook formula name used (e.g. F02 R.I.P. Category Obituary, F04 Time-Anchor Confession, F18 False-Binary Dissolve)",
  "angle": "Strategic angle used",
  "content": "The complete post text ready for LinkedIn"
}
"""


def _clean_json_text(raw_text: str) -> str:
    """Strip markdown code fence if present."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _scrub_voice_blacklist(text: str) -> str:
    """Post-generation scrubber ensuring strict 2026 voice and anti-slop compliance."""
    replacements = [
        (r"\butilize\b", "use"),
        (r"\butilizes\b", "uses"),
        (r"\butilizing\b", "using"),
        (r"\bleverage\b", "use"),
        (r"\bleverages\b", "uses"),
        (r"\bleveraging\b", "using"),
        (r"\bseamless\b", "frictionless"),
        (r"\bseamlessly\b", "smoothly"),
        (r"\bdelve\b", "dig"),
        (r"\bdelving\b", "digging"),
        (r"\bstreamline\b", "simplify"),
        (r"\bstreamlines\b", "simplifies"),
        (r"\bstreamlined\b", "simplified"),
        (r"\bfoster\b", "build"),
        (r"\bfosters\b", "builds"),
        (r"\bcultivate\b", "grow"),
        (r"\bgame-changer\b", "turning point"),
        (r"\bdeep dive\b", "detailed breakdown"),
        (r"\brobust\b", "resilient"),
        (r"\b(test|evaluation|red-teaming|eval)\s+harness\b", r"\1 suite"),
        (r"\bharness\b", "use"),
        (r"\bfundamentally\b", "at its core"),
        (r"\bessentially\b", "in practice"),
        (r"\bultimately\b", "in the end"),
        (r"\bparadigm\b", "model"),
        (r"\bin today's fast-paced world\b", "today"),
    ]
    scrubbed = text
    for pattern, repl in replacements:
        scrubbed = re.sub(pattern, repl, scrubbed, flags=re.IGNORECASE)
    return scrubbed


def generate_post_with_gemini(
    topic: str,
    *,
    hook_preference: Optional[str] = None,
    style: Optional[str] = None,
    instructions: Optional[str] = None,
    length_preset: str = "long",  # "long" (~1,300-2,000 chars) or "standard" (~900-1,300 chars)
    api_key: Optional[str] = None,
    preferred_model: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Generate a LinkedIn post using Google Gemini API with fallback models."""
    load_env()
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not key:
        return None

    # Construct prompt instructions
    user_instruction = f"Topic / Idea: {topic}\n"
    if hook_preference:
        user_instruction += f"Hook Formula Preference: {hook_preference}\n"
    if style:
        user_instruction += f"Style / Angle Preference: {style}\n"
    if instructions:
        user_instruction += f"Special Instructions / Context: {instructions}\n"

    if length_preset == "long":
        user_instruction += (
            "Target length: 1,300 to 1,900 characters. "
            "Write a thorough, long-form, high-engagement post with multi-point technical breakdown."
        )
    else:
        user_instruction += "Target length: 900 to 1,300 characters. Keep it punchy and focused."

    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    for m in CANDIDATE_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    now = time.time()
    for model_name in models_to_try:
        # Check circuit breaker
        if model_name in _CIRCUIT_OPEN_MODELS:
            if now - _CIRCUIT_OPEN_MODELS[model_name] < CIRCUIT_COOLDOWN_SECONDS:
                continue
            del _CIRCUIT_OPEN_MODELS[model_name]

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": GEMINI_SYSTEM_PROMPT},
                        {"text": user_instruction},
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": "application/json",
            },
        }

        # Bounded attempt loop for transient errors
        for attempt in range(2):
            try:
                resp = requests.post(url, json=payload, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        raw_text = parts[0].get("text", "") if parts else ""
                        cleaned = _clean_json_text(raw_text)
                        parsed = json.loads(cleaned)
                        if isinstance(parsed, dict) and "content" in parsed and parsed["content"].strip():
                            parsed["content"] = _scrub_voice_blacklist(parsed["content"])
                            return parsed

                if resp.status_code == 429:
                    err_msg = resp.text.lower()
                    if "quota" in err_msg or "exhausted" in err_msg:
                        # Daily or allocation quota exhausted: open circuit immediately
                        _CIRCUIT_OPEN_MODELS[model_name] = time.time()
                        break
                    # Transient RPM rate limit: short backoff with jitter on first attempt
                    if attempt == 0:
                        delay = 0.5 + random.uniform(0.1, 0.4)
                        time.sleep(delay)
                        continue
                    break

                if resp.status_code == 503 and attempt == 0:
                    # Model overloaded: brief retry
                    time.sleep(0.5 + random.uniform(0.1, 0.3))
                    continue

                # 404 or other non-retryable status
                break
            except requests.exceptions.Timeout:
                # Socket timeout: do not re-attempt expensive model, break to fallback
                break
            except Exception:
                break

    return None

