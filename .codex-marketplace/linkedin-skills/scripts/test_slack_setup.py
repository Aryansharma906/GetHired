#!/usr/bin/env python3
"""Test and verify Slack approval setup for LinkedIn automation.

Usage:
    python3 scripts/test_slack_setup.py
    python3 scripts/test_slack_setup.py --webhook https://hooks.slack.com/services/...
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib._env import load_env
from lib.drafts_store import create_draft
from lib.slack_approver import send_draft_to_slack


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--webhook", help="Slack Incoming Webhook URL")
    args = parser.parse_args()

    load_env()
    webhook_url = args.webhook or os.getenv("SLACK_WEBHOOK_URL")

    print("==================================================")
    print("  LinkedIn Automation Slack Approval Connection   ")
    print("==================================================")

    if not webhook_url:
        print("\n⚠️  No SLACK_WEBHOOK_URL found in .env or arguments.")
        print("\n📋 How to get a Slack Webhook in 2 minutes:")
        print("  1. Go to https://api.slack.com/apps")
        print("  2. Click 'Create New App' -> 'From scratch'")
        print("  3. Name it 'LinkedIn Approvals' and select your workspace")
        print("  4. Click 'Incoming Webhooks' in the sidebar and toggle it ON")
        print("  5. Click 'Add New Webhook to Workspace', pick your channel (e.g. #linkedin or #general)")
        print("  6. Copy the Webhook URL and paste it into your .env file:")
        print("     SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...")
        print("\nAfter adding it, run this script again:")
        print("  python3 scripts/test_slack_setup.py\n")
        return 1

    print(f"\n📡 Found Webhook URL: {webhook_url[:35]}...")
    print("📤 Sending test draft card to your Slack channel...")

    test_draft = create_draft(
        content=(
            "R.I.P. to manual LinkedIn posting workflows.\n\n"
            "This is a live test notification from your LinkedIn automation pipeline!\n\n"
            "When a new post is drafted by the system, it will arrive right here with:\n"
            "- Hook formula breakdown\n"
            "- Character count & 2026 algorithm check\n"
            "- Interactive [Approve & Schedule] and [Reject] buttons\n\n"
            "If you can see this message in Slack, your setup is working perfectly!"
        ),
        topic="LinkedIn Automation Test Setup",
        hook_formula="F02 R.I.P. Category Obituary",
        angle="Automation Setup",
    )

    res = send_draft_to_slack(test_draft, webhook_url=webhook_url)

    if res.get("success"):
        print("\n🎉 SUCCESS! Test card sent to Slack.")
        print("👉 Check your Slack channel to see your interactive approval card.")
        return 0
    else:
        print(f"\n❌ Error sending to Slack: {res.get('error')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
