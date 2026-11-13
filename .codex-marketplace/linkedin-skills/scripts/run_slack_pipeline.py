#!/usr/bin/env python3
"""Run the LinkedIn automated pipeline and send an approval card to Slack.

Generates or takes a LinkedIn post draft, audits it against 2026 voice and
algorithm rules, saves it to the draft queue, and sends an interactive Slack
approval card.

Usage:
    python3 scripts/run_slack_pipeline.py --topic "Why small AI teams beat 50-person agencies"
    python3 scripts/run_slack_pipeline.py --file draft.txt
    python3 scripts/run_slack_pipeline.py --auto-generate
    python3 scripts/run_slack_pipeline.py --test
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib._env import load_env
from lib.drafts_store import create_draft
from lib.gemini_generator import generate_post_with_gemini
from lib.slack_approver import build_slack_approval_blocks, send_draft_to_slack

SAMPLE_FOUNDER_POSTS = [
    {
        "topic": "Why small AI teams beat 50-person agencies",
        "hook_formula": "F02 R.I.P. Category Obituary",
        "angle": "Reprice the category",
        "content": (
            "R.I.P. to the 50-person marketing agency retainer.\n\n"
            "Last week a founder showed me their agency invoice: $18,500/month.\n"
            "Deliverables? 8 blog posts, 12 social graphics, and a monthly status call.\n\n"
            "The team doing the work?\n"
            "Two junior coordinators copying prompts into ChatGPT and an account manager forwarding PDFs.\n\n"
            "Contrast that with a lean 2-person team using custom agents and programmatic workflows:\n"
            "- 4x the output\n"
            "- Zero latency between strategy and execution\n"
            "- Cost: under $3,000/mo including API credits\n\n"
            "Clients don't buy hours anymore. They buy speed to qualified pipeline.\n"
            "If your agency's value proposition is billable headcount, you are charging for inefficiency.\n\n"
            "The agencies growing in 2026 look more like software engineering shops than creative studios.\n\n"
            "What's the single agency service you stopped paying for this year?"
        ),
    },
    {
        "topic": "The false binary between Building vs Marketing",
        "hook_formula": "F18 False-Binary Dissolve",
        "angle": "Content-to-pipeline",
        "content": (
            "Founders constantly argue about whether they should spend time coding or marketing.\n\n"
            "\"I'm a technical founder, marketing feels fake.\"\n"
            "\"I'm a growth founder, engineers build too slow.\"\n\n"
            "This is a false binary.\n\n"
            "The best distribution in B2B is not running ads or hiring a PR firm.\n"
            "It is documenting the specific, technical decisions you made yesterday:\n\n"
            "1. Why you chose SQLite over Postgres for your local cache\n"
            "2. How you reduced LLM inference costs by 73% using prompt compression\n"
            "3. The exact migration bug that cost you 4 hours on Sunday\n\n"
            "When you build in public with real numbers, your marketing IS your engineering log.\n\n"
            "Your target customers (engineers, buyers, founders) don't want polished marketing copy. "
            "They want to see your receipts.\n\n"
            "If you wrote code today, you already have your next post."
        ),
    },
    {
        "topic": "The 10:1 delegation rule for AI agents",
        "hook_formula": "F17 Controlled A/B Anecdote",
        "angle": "The limit of delegation",
        "content": (
            "We gave two engineers the exact same task: automate our customer onboarding audit.\n\n"
            "Engineer A spent 3 days writing a 600-line Python scraper with fragile regexes.\n"
            "Engineer B spent 3 hours writing test assertions, then let an agent generate the parser.\n\n"
            "The results after 30 days in production:\n\n"
            "- Engineer A's script broke on edge cases 14 times. Maintenance time: 22 hours.\n"
            "- Engineer B's tests caught 100% of formatting shifts before deployment. Maintenance time: 40 minutes.\n\n"
            "The takeaway isn't 'AI writes better code.'\n"
            "The real shift is moving from writing raw logic to setting evaluation gates.\n\n"
            "You don't manage agents by inspecting every line of syntax.\n"
            "You manage them like a tech lead: define the test suite, verify the edge cases, and inspect the diff.\n\n"
            "Are you spending more time writing code, or evaluating what code should do?"
        ),
    },
]


def audit_post(text: str) -> list[str]:
    """Run voice rules and blacklist check on the post."""
    issues = []
    blacklist = [
        "leverage", "utilize", "facilitate", "streamline", "robust", "seamless",
        "delve", "navigate", "unlock", "harness", "foster", "cultivate",
        "fundamentally", "essentially", "ultimately", "crucially", "notably",
        "landscape", "ecosystem", "paradigm", "realm", "tapestry", "journey",
        "game-changer", "deep dive", "in today's fast-paced world",
    ]
    lower = text.lower()
    for word in blacklist:
        if word in lower:
            issues.append(f"Contains AI buzzword: '{word}'")

    if len(text) > 3000:
        issues.append(f"Exceeds LinkedIn limit (3000 chars): currently {len(text)}")

    em_dashes = text.count("—")
    word_count = len(text.split())
    if word_count > 0 and (em_dashes / word_count) > 0.02:
        issues.append(f"Excessive em dashes ({em_dashes} in {word_count} words)")

    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", help="Topic to draft a post about")
    parser.add_argument("--file", help="Path to existing draft text file")
    parser.add_argument("--hook", help="Specific hook formula to use")
    parser.add_argument("--auto-generate", action="store_true", help="Pick a high-performing founder post")
    parser.add_argument("--dry-run", action="store_true", help="Print card without sending to Slack")
    parser.add_argument("--test", action="store_true", help="Send a test verification draft to Slack")
    args = parser.parse_args()

    load_env()

    # Determine post content
    if args.test:
        sample = SAMPLE_FOUNDER_POSTS[0]
        topic = f"[TEST] {sample['topic']}"
        hook = sample["hook_formula"]
        angle = sample["angle"]
        content = sample["content"]
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 1
        content = path.read_text(encoding="utf-8").strip()
        topic = args.topic or path.stem.replace("_", " ").title()
        hook = args.hook or "Custom Draft"
        angle = "Direct File"
    elif args.topic:
        topic = args.topic
        hook = args.hook or "F02 R.I.P. Category Obituary"
        angle = "Founder Angle"
        gemini_res = generate_post_with_gemini(topic, hook_preference=args.hook)
        if gemini_res:
            print("✨ Generated post using Google Gemini")
            content = gemini_res.get("content", "")
            hook = gemini_res.get("hook_formula", hook)
            angle = gemini_res.get("angle", angle)
        else:
            # Fallback template customized with topic
            content = (
                f"R.I.P. to the traditional way of handling {topic.lower()}.\n\n"
                f"Over the last 6 months, we ran an experiment comparing the old manual approach "
                f"against an automated workflow.\n\n"
                f"The old way:\n"
                f"- High manual friction\n"
                f"- Slow turnaround times\n"
                f"- Scaling linearly with hours worked\n\n"
                f"The automated way:\n"
                f"- Human sets the criteria and review threshold\n"
                f"- Automation drafts, audits, and formats in seconds\n"
                f"- One-click approval before anything touches production\n\n"
                f"You don't need a bigger team. You need tighter feedback loops.\n\n"
                f"What part of your workflow are you automating next?"
            )
    else:
        # Autonomous live research & trend scraping
        try:
            from lib.trend_scraper import collect_daily_intelligence, synthesize_daily_post_topics
            signals = collect_daily_intelligence()
            curated = synthesize_daily_post_topics(signals)
            picked = random.choice(curated)
            topic = picked["topic"]
            hook = picked["hook_formula"]
            angle = picked["angle"]
            print(f"📡 Scraped live trend: '{topic}' ({angle})")
            gemini_res = generate_post_with_gemini(topic, hook_preference=hook)
            if gemini_res:
                print("✨ Generated post using Google Gemini")
                content = gemini_res.get("content", "")
                hook = gemini_res.get("hook_formula", hook)
                angle = gemini_res.get("angle", angle)
            else:
                sample = random.choice(SAMPLE_FOUNDER_POSTS)
                topic = sample["topic"]
                hook = sample["hook_formula"]
                angle = sample["angle"]
                content = sample["content"]
        except Exception as e:
            print(f"Trend scraper fallback: {e}")
            sample = random.choice(SAMPLE_FOUNDER_POSTS)
            topic = sample["topic"]
            hook = sample["hook_formula"]
            angle = sample["angle"]
            content = sample["content"]

    # Audit content
    issues = audit_post(content)
    if issues:
        print("⚠️ Post audit warnings:")
        for iss in issues:
            print(f"  - {iss}")

    # Enqueue draft
    draft = create_draft(
        content=content,
        topic=topic,
        hook_formula=hook,
        angle=angle,
    )
    print(f"✅ Draft created & queued: {draft['id']} ({draft['char_count']} chars)")

    if args.dry_run:
        blocks = build_slack_approval_blocks(draft)
        print("\n--- Slack Block Kit Preview (dry-run) ---")
        print(json.dumps({"blocks": blocks}, indent=2))
        return 0

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("\nℹ️  SLACK_WEBHOOK_URL is not set in .env.")
        print(f"👉 To receive approval cards in Slack:")
        print(f"   1. Add your Slack Incoming Webhook URL to .env:")
        print(f"      SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...")
        print(f"   2. Run this command again.")
        print(f"\nYour draft has been saved to the queue: testing/drafts_queue.json")
        return 0

    print("🚀 Sending approval card to Slack channel...")
    res = send_draft_to_slack(draft, webhook_url=webhook_url)
    if res.get("success"):
        print("🎉 Approval card successfully delivered to your Slack channel!")
        print("Check Slack to review the draft and click [Approve & Schedule] or [Reject].")
    else:
        print(f"❌ Failed to send to Slack: {res.get('error')}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
