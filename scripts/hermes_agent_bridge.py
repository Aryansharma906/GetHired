#!/usr/bin/env python3
"""
FrontierPilot 2.0 — Hermes Agent Autonomous Bridge CLI & SDK
Allows Hermes Agent (Nous Research) to interact with the 24/7 Netlify platform,
dispatch tasks, inspect skills, and trigger redeployments.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

DEFAULT_BASE_URL = os.getenv("FRONTIERPILOT_URL", "https://frontierpilot-studio.netlify.app")
DEFAULT_API_KEY = os.getenv("HERMES_API_KEY", "hermes_live_frontierpilot_autonomy_9956")

def make_request(path, method="GET", data=None, api_key=None):
    url = f"{DEFAULT_BASE_URL.rstrip('/')}{path}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "HermesAgent/1.0"
    }
    if api_key or DEFAULT_API_KEY:
        headers["Authorization"] = f"Bearer {api_key or DEFAULT_API_KEY}"
        headers["X-Hermes-Key"] = api_key or DEFAULT_API_KEY

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return {"error": f"HTTP {e.code}", "detail": json.loads(err_body)}
        except Exception:
            return {"error": f"HTTP {e.code}", "detail": err_body}
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Hermes Agent Autonomous Bridge CLI")
    parser.add_argument("--status", action="store_true", help="Check Hermes bridge & 24/7 cloud platform health")
    parser.add_argument("--skills", action="store_true", help="List registered skills and tool schemas")
    parser.add_argument("--draft", metavar="TOPIC", help="Dispatch a LinkedIn post draft task to Gemini & Slack")
    parser.add_argument("--alert", metavar="MSG", help="Send an autonomous alert to Aryan's Slack channel")
    parser.add_argument("--redeploy", action="store_true", help="Request an automated Netlify redeploy")
    args = parser.parse_args()

    if args.status:
        print("🔍 Checking FrontierPilot 2.0 & Hermes Agent cloud health...")
        res = make_request("/api/hermes/status")
        print(json.dumps(res, indent=2))
        return

    if args.skills:
        print("🛠 Fetching registered skills for Hermes tool-use...")
        res = make_request("/api/hermes/skills")
        print(json.dumps(res, indent=2))
        return

    if args.draft:
        print(f"🤖 Dispatching post drafting task: '{args.draft}'...")
        res = make_request("/api/hermes/dispatch", method="POST", data={
            "action": "draft_post",
            "params": {"topic": args.draft}
        })
        print(json.dumps(res, indent=2))
        return

    if args.alert:
        print(f"📣 Sending alert to Slack: '{args.alert}'...")
        res = make_request("/api/hermes/dispatch", method="POST", data={
            "action": "slack_alert",
            "params": {"message": args.alert}
        })
        print(json.dumps(res, indent=2))
        return

    if args.redeploy:
        print("🚀 Registering redeploy request...")
        res = make_request("/api/hermes/redeploy", method="POST")
        print(json.dumps(res, indent=2))
        return

    parser.print_help()

if __name__ == "__main__":
    main()
