#!/usr/bin/env python3
"""Check or wait for LinkedIn channel connection in Publora.

Detects when the user connects their LinkedIn account in the Publora dashboard
and automatically saves LINKEDIN_PLATFORM_ID to .env.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib._env import load_env
from lib.publora_client import PubloraClient

load_env()
ENV_FILE = ROOT / ".env"


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


def check_connection(auto_save: bool = True):
    try:
        client = PubloraClient()
        channels = client.list_platform_connections()
    except Exception as e:
        print(f"Error communicating with Publora: {e}")
        return None

    linkedin_channels = [
        c for c in channels
        if str(c.get("platformId", "")).startswith("linkedin-") or c.get("platform") == "linkedin"
    ]

    if not linkedin_channels:
        return None

    first = linkedin_channels[0]
    pid = first.get("platformId")
    name = first.get("platformUsername") or first.get("name") or "Your LinkedIn Profile"

    if auto_save and pid:
        update_env_variable("LINKEDIN_PLATFORM_ID", pid)
        print(f"🎉 Connected to LinkedIn: {name} (ID: {pid})")
        print("✅ Saved LINKEDIN_PLATFORM_ID to .env. Live publishing is now ENABLED!")

    return first


if __name__ == "__main__":
    found = check_connection()
    if not found:
        print("ℹ️ No LinkedIn channel connected yet in your Publora dashboard.")
        print("👉 Go to: https://app.publora.com/channels")
        print("👉 Click 'Add Channel' -> 'LinkedIn' and click Authorize.")
        print("Run this script again after connecting to activate live publishing.")
        sys.exit(1)
