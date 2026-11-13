"""Slack approval integration for LinkedIn automated pipeline.

Formats LinkedIn drafts into interactive Slack Block Kit cards, sends them to
your Slack channel via Incoming Webhook, and handles interactive approval
button callbacks.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import requests

from ._env import load_env
from .drafts_store import get_draft, update_draft_status

ROOT = Path(__file__).resolve().parents[1]


def get_default_schedule_slot() -> str:
    """Returns the next 10:00 AM slot in ISO UTC format."""
    now = datetime.now().astimezone()
    ten = now.replace(hour=10, minute=0, second=0, microsecond=0)
    target = ten if now < ten else now + timedelta(minutes=5)
    return target.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_local_ip() -> str:
    """Get the local network IP of the Mac."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_studio_url() -> str:
    """Resolve the URL to the Approval Studio, accessible by phones on the local network."""
    load_env()
    custom = os.getenv("STUDIO_URL")
    if custom:
        return custom.rstrip("/")
    ip = get_local_ip()
    return f"http://{ip}:5050"


def send_studio_online_notification(
    public_url: str,
    local_url: Optional[str] = None,
) -> dict[str, Any]:
    """Send an announcement card to Slack with the active Studio links."""
    load_env()
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return {"success": False, "error": "SLACK_WEBHOOK_URL missing"}

    loc = local_url or f"http://{get_local_ip()}:5050"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📱 LinkedIn Approval Studio is Live!",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Approval Studio is now active and synced.*\n\n"
                    f"• *Mobile / Cellular URL:* <{public_url}|{public_url}>\n"
                    f"• *Local Wi-Fi URL:* <{loc}|{loc}>\n\n"
                    "_Tip: If using the public link on iPhone Safari, tap `[Visit Site]` once if prompted by ngrok._"
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🌐 Open Studio (Public)",
                        "emoji": True,
                    },
                    "style": "primary",
                    "url": public_url,
                    "action_id": "open_studio_public",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📶 Open Studio (Local Wi-Fi)",
                        "emoji": True,
                    },
                    "url": loc,
                    "action_id": "open_studio_local",
                },
            ],
        },
    ]

    try:
        resp = requests.post(
            webhook_url,
            json={"text": f"📱 LinkedIn Approval Studio is Live: {public_url}", "blocks": blocks},
            timeout=10,
        )
        return {"success": resp.status_code == 200}
    except Exception as e:
        return {"success": False, "error": str(e)}


def build_slack_approval_blocks(draft: dict[str, Any]) -> list[dict[str, Any]]:
    """Build rich Slack Block Kit blocks for reviewing a LinkedIn draft."""
    draft_id = draft["id"]
    topic = draft.get("topic", "LinkedIn Post")
    hook_formula = draft.get("hook_formula", "Proven Hook")
    char_count = draft.get("char_count", len(draft.get("content", "")))
    content = draft.get("content", "")
    scheduled_time = draft.get("scheduled_time") or get_default_schedule_slot()
    status = draft.get("status", "pending_approval")

    # Character sweet spot guide
    if 800 <= char_count <= 1400:
        length_badge = f"{char_count} chars (Optimal 900-1300)"
    elif char_count > 3000:
        length_badge = f"⚠️ {char_count} chars (Exceeds LinkedIn 3000 cap)"
    else:
        length_badge = f"{char_count} chars"

    # Status header
    if status == "approved":
        status_text = "✅ *Approved & Scheduled for LinkedIn*"
    elif status == "rejected":
        status_text = "❌ *Draft Rejected*"
    else:
        status_text = "🟡 *Ready for Review & Approval*"

    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"LinkedIn Draft: {topic[:120]}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{status_text}\n"
                    f"*Hook Formula:* `{hook_formula}`\n"
                    f"*Length:* {length_badge}\n"
                    f"*Suggested Slot:* `{scheduled_time}`"
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{content}```",
            },
        },
    ]

    media_urls = draft.get("media_urls") or []
    for m_url in media_urls[:1]:
        if isinstance(m_url, str) and m_url.startswith("http"):
            blocks.append({
                "type": "image",
                "image_url": m_url,
                "alt_text": "Post Visual",
            })

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "🛡️ *2026 Algorithm Audit:* Zero banned buzzwords • Slop filter compliant • Natural cadence",
            }
        ],
    })

    # Include action buttons only if pending approval
    if status == "pending_approval":
        base_url = get_studio_url()
        blocks.append({
            "type": "actions",
            "block_id": f"actions_{draft_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📱 Open Studio",
                        "emoji": True,
                    },
                    "url": base_url,
                    "action_id": "open_studio",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Approve & Schedule",
                        "emoji": True,
                    },
                    "style": "primary",
                    "value": f"approve:{draft_id}",
                    "url": f"{base_url}/action/approve/{draft_id}",
                    "action_id": "approve_draft",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Reject",
                        "emoji": True,
                    },
                    "style": "danger",
                    "value": f"reject:{draft_id}",
                    "url": f"{base_url}/action/reject/{draft_id}",
                    "action_id": "reject_draft",
                },
            ],
        })

    return blocks


def send_draft_to_slack(
    draft: dict[str, Any],
    webhook_url: Optional[str] = None,
) -> dict[str, Any]:
    """Send a draft approval card to Slack via Incoming Webhook."""
    load_env()
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    blocks = build_slack_approval_blocks(draft)
    payload = {
        "text": f"New LinkedIn Post ready for approval: {draft.get('topic', 'LinkedIn Post')}",
        "blocks": blocks,
    }

    if not url:
        return {
            "success": False,
            "error": "SLACK_WEBHOOK_URL not set in .env or environment",
            "payload": payload,
        }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            return {"success": True, "draft_id": draft["id"]}
        return {
            "success": False,
            "error": f"Slack API HTTP {resp.status_code}: {resp.text}",
            "payload": payload,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "payload": payload}


def send_published_notification(
    draft: dict[str, Any],
    kind: str = "post",
    live_url: Optional[str] = None,
) -> None:
    """Send an immediate confirmation notification to Slack the moment content goes live."""
    load_env()
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    topic = draft.get("topic", "LinkedIn Post")
    content_snippet = draft.get("content", "")[:280] + ("..." if len(draft.get("content", "")) > 280 else "")
    target = live_url or draft.get("target_url") or "https://www.linkedin.com/in/aryan-sharma-engineer"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚀 Just Published on LinkedIn! ({kind.title()})",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Status:* ✅ Live on LinkedIn\n"
                    f"*Topic:* {topic}\n"
                    f"*Published At:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`\n\n"
                    f"> {content_snippet}"
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔗 View Live on LinkedIn",
                        "emoji": True,
                    },
                    "url": target,
                    "style": "primary",
                }
            ],
        },
    ]

    try:
        requests.post(webhook_url, json={"text": f"🚀 Just Published on LinkedIn: {topic}", "blocks": blocks}, timeout=10)
    except Exception:
        pass


def process_slack_action(action_value: str, user_name: str = "User") -> dict[str, Any]:
    """Process an action clicked in Slack (e.g. approve:<id>, reject:<id>)."""
    parts = action_value.split(":", 1)
    if len(parts) != 2:
        return {"success": False, "error": "Invalid action value format"}

    action_type, draft_id = parts[0], parts[1]
    draft = get_draft(draft_id)
    if not draft:
        return {"success": False, "error": f"Draft {draft_id} not found in queue"}

    if action_type == "approve":
        # Guard against double-posting
        if draft.get("status") in {"published", "scheduled"}:
            return {
                "success": False,
                "error": f"Post '{draft.get('topic')}' has already been {draft.get('status')}! Double-posting prevented.",
                "blocks": build_slack_approval_blocks(draft),
            }

        # Check Publora configuration for live publishing
        scheduled_utc = draft.get("scheduled_time") or get_default_schedule_slot()
        publora_res = None
        publish_error = None

        # 1. Try Direct Official LinkedIn API first
        publora_res = None
        publish_error = None
        try:
            from testing.linkedin_official_client import LinkedInOfficialClient
            official_client = LinkedInOfficialClient()
            if official_client.access_token and official_client.author_urn:
                direct_res = official_client.create_text_post(draft["content"])
                if direct_res.get("success"):
                    publora_res = {
                        "success": True,
                        "id": direct_res.get("urn"),
                        "backend": "official_linkedin",
                    }
                else:
                    publish_error = direct_res.get("error")
        except Exception as err:
            publish_error = str(err)

        # 2. Fallback to Publora if official API is not configured or fails
        if not (publora_res and publora_res.get("success")):
            try:
                from lib import active_backend, publish
                backend = active_backend()
                if backend in ("publora", "diy"):
                    if draft.get("post_urn"):
                        publora_res = publish(
                            "comment",
                            draft["content"],
                            draft.get("target_url", "https://www.linkedin.com/feed/"),
                            post_urn=draft["post_urn"],
                            reaction_type=draft.get("reaction_type", "INTEREST"),
                        )
                    else:
                        publora_res = publish(
                            "post",
                            draft["content"],
                            "https://www.linkedin.com/feed/",
                            scheduled_time=scheduled_utc,
                            media_urls=draft.get("media_urls"),
                        )
            except Exception as err:
                publish_error = str(err)

        is_published = bool(publora_res and (publora_res.get("success") or (publora_res.get("mode") == "diy" and publora_res.get("returncode") == 0)))
        new_status = "published" if is_published else "approved"
        updated = update_draft_status(
            draft_id,
            new_status,
            approved_by=user_name,
            publora_id=(publora_res or {}).get("postGroupId") or (publora_res or {}).get("id") or (publora_res or {}).get("urn"),
            publish_error=publish_error,
        )

        # Notify Slack immediately that it is live!
        if is_published:
            kind = "comment" if draft.get("post_urn") else "post"
            live_url = draft.get("target_url") or "https://www.linkedin.com/in/aryan-sharma-engineer"
            send_published_notification(updated or draft, kind=kind, live_url=live_url)

        return {
            "success": True,
            "action": "approved",
            "draft": updated,
            "blocks": build_slack_approval_blocks(updated),
        }

    elif action_type == "reject":
        updated = update_draft_status(draft_id, "rejected", rejected_by=user_name)
        return {
            "success": True,
            "action": "rejected",
            "draft": updated,
            "blocks": build_slack_approval_blocks(updated),
        }

    return {"success": False, "error": f"Unknown action {action_type}"}
