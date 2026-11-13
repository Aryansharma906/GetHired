#!/usr/bin/env python3
"""Generate a Vaibhav Sisinty + Engineer hybrid post on AI Privacy Rights."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib._env import load_env
from lib.drafts_store import create_draft
from lib.gemini_generator import generate_post_with_gemini
from lib.slack_approver import send_draft_to_slack

load_env()

PROMPT = """You are ghostwriting for Aryan Sharma, a software engineer with the viral growth-storytelling voice of Vaibhav Sisinty.

Write a long-form, high-engagement LinkedIn post on:
TOPIC: Privacy rights in the AI digital era.

STYLE & VOICE GUIDELINES (Vaibhav Sisinty + Senior Engineer):
- Opening: Startling hook in the first 2 lines that creates an irresistible curiosity gap before the 'see more' fold.
- Format: Short, punchy 1-2 sentence lines with white space. Scannable on mobile.
- The Core Reality: Most people think privacy is 'Incognito mode, strong passwords, and cookie banners'. In the AI era, that is a total illusion.
- The Technical Truth: Break down what actually happens behind the scenes:
  1. Your prompt isn't just an API call—it gets vectorized into 1,536-dimensional embeddings that map your intent, psychology, and private habits.
  2. RAG pipelines and context caches retain your operational context across sessions.
  3. Model distillation and fine-tuning: Once your proprietary code or private thoughts enter the training corpus, no 'Delete Account' button can mathematically unlearn them from model weights.
- The Verdict: We are trading the illusion of free intelligence for permanent cognitive surveillance.
- Strong Takeaway: 2 rules every builder and user must follow today.
- Ending: A provocative, debate-sparking question (never a lazy 'What do you think?').

CRITICAL CONSTRAINTS:
- 0 banned buzzwords: NEVER use leverage, utilize, streamline, robust, seamless, delve, navigate, unlock, harness, landscape, ecosystem, paradigm.
- Em dashes (—) capped at 1 max.
- Length: between 1,200 and 1,600 characters.

Return ONLY JSON:
{
  "topic": "Privacy Rights in the AI Digital Era",
  "hook_formula": "F04 Time-Anchor Confession + Curiosity Gap",
  "angle": "The Latent Space Privacy Illusion",
  "content": "The full post text"
}
"""

def main():
    print("✨ Generating post with Google Gemini (gemini-3.6-flash)...")
    res = generate_post_with_gemini(PROMPT)

    if not res:
        print("Fallback to handcrafted authentic post...")
        content = (
            "We spent 15 years obsessing over cookie banners and 16-character passwords.\n\n"
            "Last week, an engineer showed me an internal LLM session log.\n"
            "In 4 minutes, I realized that modern privacy is completely dead.\n\n"
            "Most people still think privacy in 2026 means:\n"
            "- Turning on Incognito mode\n"
            "- Using 2-factor authentication\n"
            "- Clicking 'Reject all cookies'\n\n"
            "That was Web2 privacy.\n"
            "In the AI era, none of that protects you.\n\n"
            "Here is the engineering truth nobody tells you about AI products:\n\n"
            "1. Your prompts are vectorized, not just stored.\n"
            "When you paste a messy problem, your text is converted into 1,536-dimensional math. "
            "It doesn't just record your words. It encodes your intent, your cognitive weaknesses, and your unwritten habits.\n\n"
            "2. 'Deleting your data' is a mathematical fiction.\n"
            "When an LLM trains or fine-tunes on your data, your private context becomes part of billions of floating-point weights. "
            "There is no 'DELETE FROM table WHERE user_id = me' in deep learning. You cannot surgically unlearn a concept from a neural net.\n\n"
            "3. The real currency isn't your email. It's your thought process.\n"
            "Every draft you ask an agent to polish reveals how you reason, how you negotiate, and where your code breaks.\n\n"
            "We aren't paying for AI tools with \$20 monthly subscriptions.\n"
            "We are paying with our cognitive blueprints.\n\n"
            "If you build software: stop sending raw customer context to third-party endpoints without local anonymization.\n"
            "If you use AI: treat every prompt as if it will be read aloud at your next board meeting.\n\n"
            "Are we already too late to reclaim digital privacy, or is local on-device AI our only way out?"
        )
        res = {
            "topic": "The Illusion of Privacy in the AI Digital Era",
            "hook_formula": "F04 Time-Anchor Confession + Contrast",
            "angle": "Vaibhav Sisinty + Engineer Hybrid",
            "content": content
        }

    print(f"\n--- Post Generated ({len(res['content'])} chars) ---")
    print(res["content"])

    draft = create_draft(
        content=res["content"],
        topic=res["topic"],
        hook_formula=res["hook_formula"],
        angle=res["angle"],
    )

    print("\n🚀 Sending approval card to your Slack channel...")
    slack_res = send_draft_to_slack(draft)
    print("Slack delivery:", slack_res)
    print("\n👉 Check Slack or your iPhone Studio to review and approve!")


if __name__ == "__main__":
    main()
