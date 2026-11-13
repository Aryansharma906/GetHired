#!/usr/bin/env python3
"""Slack interactive webhook server for LinkedIn post approvals.

Listens for button interactions from Slack ([Approve & Schedule], [Reject],
[Alternate Hook]) and updates the post status and Slack message card in real-time.

Usage:
    python3 scripts/slack_listener.py [--port 5050]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from flask import Flask, jsonify, request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.slack_approver import process_slack_action

app = Flask(__name__)


@app.route("/slack/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "linkedin-slack-approver"})


@app.route("/slack/interactions", methods=["POST"])
def slack_interactions():
    """Endpoint for Slack Interactivity request URL."""
    # Slack sends the payload URL-encoded in form parameter 'payload'
    payload_raw = request.form.get("payload")
    if not payload_raw:
        # Fallback if raw JSON body
        payload_json = request.get_json(silent=True) or {}
    else:
        try:
            payload_json = json.loads(payload_raw)
        except Exception:
            payload_json = {}

    actions = payload_json.get("actions", [])
    user_info = payload_json.get("user", {})
    user_name = user_info.get("name") or user_info.get("username") or "Slack User"

    if not actions:
        return jsonify({"text": "No action received"}), 400

    first_action = actions[0]
    action_val = first_action.get("value", "")

    result = process_slack_action(action_val, user_name=user_name)

    if result.get("success") and "blocks" in result:
        # Returning updated blocks replaces the message in Slack with updated status
        return jsonify({
            "replace_original": True,
            "blocks": result["blocks"],
        })

    return jsonify({"text": f"Processed: {result.get('error') or 'OK'}"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5050, help="Port to listen on (default 5050)")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface (default 0.0.0.0)")
    args = parser.parse_args()

    print(f"🚀 Slack Approval Listener running at http://{args.host}:{args.port}")
    print(f"👉 Point your Slack Interactivity URL to: http://<your-host>:{args.port}/slack/interactions")
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
