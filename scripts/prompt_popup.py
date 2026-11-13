#!/usr/bin/env python3
"""Show a native macOS popup dialog to collect Slack Webhook and Gemini Key securely.

The credentials are saved directly to .env on your machine without being
exposed in chat logs.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"


def run_osascript(apple_script: str) -> str:
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    return res.stdout.strip()


def update_env_variable(key: str, value: str) -> None:
    value = value.strip()
    if not value:
        return

    content = ""
    if ENV_FILE.exists():
        content = ENV_FILE.read_text(encoding="utf-8")

    pattern = rf"^{re.escape(key)}=.*$"
    replacement = f"{key}={value}"

    if re.search(pattern, content, flags=re.MULTILINE):
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    else:
        new_content = (content.rstrip() + f"\n{replacement}\n").lstrip()

    ENV_FILE.write_text(new_content, encoding="utf-8")


def main():
    # 1. Slack Webhook Prompt
    script_slack = (
        'display dialog "Paste your Slack Webhook URL here:\\n(starts with https://hooks.slack.com/services/...)" '
        'default answer "" '
        'with title "LinkedIn Automation — Step 1: Slack Webhook" '
        'buttons {"Cancel", "Save"} default button "Save"'
    )

    out_slack = run_osascript(script_slack)
    if "button returned:Save" not in out_slack:
        print("Canceled by user.")
        return 0

    match = re.search(r"text returned:(.*)", out_slack)
    webhook_url = match.group(1).strip() if match else ""

    if webhook_url:
        update_env_variable("SLACK_WEBHOOK_URL", webhook_url)
        print("✅ Saved SLACK_WEBHOOK_URL securely into .env.")
    else:
        print("⚠️ No Webhook URL entered.")

    # 2. Optional Gemini Key Prompt
    script_gemini = (
        'display dialog "Paste your Gemini API Key (optional):\\n(Leave blank and click Skip if you don\'t have one)" '
        'default answer "" with hidden answer '
        'with title "LinkedIn Automation — Step 2: Gemini AI Key" '
        'buttons {"Skip", "Save"} default button "Skip"'
    )

    out_gemini = run_osascript(script_gemini)
    if "button returned:Save" in out_gemini:
        match_g = re.search(r"text returned:(.*)", out_gemini)
        gemini_key = match_g.group(1).strip() if match_g else ""
        if gemini_key:
            update_env_variable("GEMINI_API_KEY", gemini_key)
            print("✅ Saved GEMINI_API_KEY securely into .env.")

    # 3. Notification
    run_osascript('display notification "Credentials saved to .env!" with title "LinkedIn Automation"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
