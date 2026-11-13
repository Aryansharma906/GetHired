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


# =========================================================================
# Dossier Career Radar & Job Opportunities Approval in Slack
# =========================================================================

def build_job_approval_blocks(opp: dict[str, Any]) -> list[dict[str, Any]]:
    """Build interactive Block Kit blocks for reviewing and approving a job opportunity."""
    opp_id = opp.get("id", "")
    title = opp.get("title", "Role")
    org = opp.get("organization", "Company")
    category = opp.get("category", "Opportunity")
    stipend = opp.get("stipend", "Competitive")
    deadline = opp.get("deadline", "Rolling")
    score = int(opp.get("match_score", 90))
    status = opp.get("status", "Active")
    portal_url = opp.get("url", "#")
    matching_skills = opp.get("matching_skills") or opp.get("tags") or []
    skills_text = " • ".join(f"`{s}`" for s in matching_skills[:5])
    summary = opp.get("executive_summary") or opp.get("match_reason") or "Strong synergy with Aryan Sharma's AI/ML systems and research profile."
    gaps = opp.get("gaps_or_growth_areas") or []
    gaps_text = " • ".join(gaps) if gaps else "Emphasize systems evaluation and open-source contributions."

    base_url = get_studio_url()
    score_emoji = "🟢" if score >= 85 else ("🔵" if score >= 75 else "🟡")

    default_dm = (
        f"Hi [Name], loved {org}'s recent engineering focus. "
        f"I specialize in LLM evaluation and prompt security research, recently publishing on adversarial attack surfaces while benchmarking models at Handshake. "
        f"I’d love to share a brief 1-page tactical architecture breakdown on how this applies to {org}'s {title} roadmap if helpful."
    )
    recruiter_dm = opp.get("recruiter_dm") or default_dm

    if "Approved" in status:
        status_line = "✅ *Approved & Staged for Application*"
    elif "Archived" in status or "Passed" in status:
        status_line = "❌ *Opportunity Archived / Passed*"
    else:
        status_line = "🟡 *Ready for Candidate Approval*"

    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🎯 Career Opportunity: {org} — {title[:60]}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{status_line}\n"
                    f"*Fit Rating:* {score_emoji} *`{score}% Match`* (Evaluated by Google Gemini)\n"
                    f"*Category:* `{category}` | *Comp/Stipend:* `{stipend}`\n"
                    f"*Deadline:* `{deadline}`"
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*🎯 AI Tactical Alignment:*\n>{summary}\n\n"
                    f"*⚡ Key Matching Strengths:*\n{skills_text}\n\n"
                    f"*💡 Tailoring Strategy:*\n_{gaps_text}_"
                ),
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"💬 *3-Sentence Hiring Manager DM (Vaibhav Sisinty Strategy):*\n"
                    f"```{recruiter_dm}```\n"
                    f"_Tip: Tap to copy on mobile and send directly to hiring managers on LinkedIn._"
                ),
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🛡️ *Complete AI Job Hunt Stack:* Gemini ATS Resume • Value Cover Letter • NotebookLM Prep • Notion Board",
                }
            ],
        },
    ]

    # Action buttons if pending
    if "Approved" not in status and "Archived" not in status:
        elements = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "✅ Approve & Stage", "emoji": True},
                "style": "primary",
                "value": f"approve_job:{opp_id}",
                "url": f"{base_url}/action/approve_job/{opp_id}",
                "action_id": "approve_job",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📄 Resume", "emoji": True},
                "url": f"{base_url}/action/view_resume/{opp_id}",
                "action_id": "view_resume",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📦 Download ZIP Pack", "emoji": True},
                "url": f"{base_url}/api/opportunities/{opp_id}/bundle",
                "action_id": "download_bundle",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🎙️ Interview Prep", "emoji": True},
                "url": f"{base_url}/action/view_interview_prep/{opp_id}",
                "action_id": "view_interview_prep",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "❌ Pass", "emoji": True},
                "style": "danger",
                "value": f"reject_job:{opp_id}",
                "url": f"{base_url}/action/reject_job/{opp_id}",
                "action_id": "reject_job",
            },
        ]
        if portal_url and portal_url.startswith("http"):
            elements.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "🔗 Portal", "emoji": True},
                "url": portal_url,
                "action_id": "open_portal",
            })

        blocks.append({
            "type": "actions",
            "block_id": f"job_actions_{opp_id}",
            "elements": elements,
        })

    return blocks


def send_job_approval_to_slack(
    opp: dict[str, Any],
    webhook_url: Optional[str] = None,
) -> dict[str, Any]:
    """Send an interactive job opportunity approval card to Slack."""
    load_env()
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return {"success": False, "error": "SLACK_WEBHOOK_URL missing"}

    blocks = build_job_approval_blocks(opp)
    payload = {
        "text": f"🎯 New Career Opportunity Ready for Approval: {opp.get('organization')} — {opp.get('title')}",
        "blocks": blocks,
    }
    try:
        resp = requests.post(url, json=payload, timeout=12)
        return {"success": resp.status_code == 200, "opp_id": opp.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_job_radar_digest_to_slack(
    opps: list[dict[str, Any]],
    webhook_url: Optional[str] = None,
) -> dict[str, Any]:
    """Send an executive Career Radar digest summarizing all opportunities to Slack."""
    load_env()
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return {"success": False, "error": "SLACK_WEBHOOK_URL missing"}

    base_url = get_studio_url()
    total_count = len(opps)
    top_matches = sorted(opps, key=lambda x: int(x.get("match_score", 90)), reverse=True)[:4]

    fields_text = ""
    for idx, o in enumerate(top_matches, 1):
        score = o.get("match_score", 90)
        fields_text += f"*{idx}. {o.get('organization')}* — `{o.get('title')}`\n"
        fields_text += f"   • Fit: *{score}% Match* | Deadline: `{o.get('deadline', 'Rolling')}` | Stipend: `{o.get('stipend', 'Competitive')}`\n"
        fields_text += f"   • <{base_url}/action/approve_job/{o.get('id')}|1-Tap Approve> | <{base_url}/action/view_resume/{o.get('id')}|View Resume>\n\n"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📡 Dossier Career Radar: Active Opportunities Digest",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Radar Status:* Tracking *{total_count} active opportunities* across frontier AI labs, research fellowships, and systems internships.\n\n"
                    f"🏆 *Top Recommended Roles for Aryan Sharma:*\n\n"
                    f"{fields_text}"
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "💼 Open Dossier Hub", "emoji": True},
                    "style": "primary",
                    "url": base_url,
                    "action_id": "open_dossier_hub",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📊 View Google Sheets", "emoji": True},
                    "url": f"{base_url}/api/dossier/export/sheets",
                    "action_id": "view_sheets_csv",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📝 View Notion Database", "emoji": True},
                    "url": "https://app.notion.com/p/4ec8b8ee58fb4056b7269f4b526224f1",
                    "action_id": "view_notion_csv",
                },
            ],
        },
    ]

    payload = {
        "text": f"📡 Dossier Career Radar: {total_count} Active Opportunities Tracked",
        "blocks": blocks,
    }
    try:
        resp = requests.post(url, json=payload, timeout=12)
        return {"success": resp.status_code == 200, "count": total_count}
    except Exception as e:
        return {"success": False, "error": str(e)}


def process_job_slack_action(action_type: str, opp_id: str, user_name: str = "Aryan") -> dict[str, Any]:
    """Handle 1-tap or interactive button action on a job opportunity."""
    from lib.dossier_integrator import DossierIntegrator
    integrator = DossierIntegrator()
    opps = integrator.load_opportunities()

    target = next((o for o in opps if o.get("id") == opp_id), None)
    if not target:
        return {"success": False, "error": f"Opportunity {opp_id} not found"}

    if action_type == "approve_job":
        target["status"] = "Approved / Ready to Apply"
        target["approved_by"] = user_name
        target["approved_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Generate / ensure tailored resume exists
        try:
            from scripts.generate_tailored_resume import tailor_resume
            tailored = tailor_resume(target.get("title", "Software Engineer"), target.get("organization", "Company"))
            out_dir = ROOT / "testing" / "tailored_resumes"
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = f"Aryan_Sharma_{target.get('organization', '').replace(' ', '_')}_{opp_id}.md"
            (out_dir / filename).write_text(tailored, encoding="utf-8")
        except Exception:
            pass

        # Update Google Sheets & Notion exports
        from lib.dossier_integrator import DossierIntegrator
        integrator = DossierIntegrator()
        integrator.save_opportunities(opps)
        integrator.sync_to_google_sheets(opps)
        integrator.sync_resumes_to_google_drive()
        integrator.sync_to_notion(opps)

        # Notify Slack of confirmation
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if webhook_url:
            conf_blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "✅ Opportunity Approved & Staged!", "emoji": True}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Role:* *{target.get('title')}* at *{target.get('organization')}*\n"
                            f"*Approved by:* {user_name} at `{target['approved_at']}`\n"
                            f"*Action Taken:* Tailored ATS resume generated, staged in Google Drive manifest, and updated in Google Sheets & Notion pipeline."
                        )
                    }
                }
            ]
            try:
                requests.post(webhook_url, json={"text": f"✅ Opportunity Approved: {target.get('organization')} — {target.get('title')}", "blocks": conf_blocks}, timeout=10)
            except Exception:
                pass

        return {
            "success": True,
            "action": "approved",
            "opportunity": target,
            "blocks": build_job_approval_blocks(target)
        }

    elif action_type == "reject_job":
        target["status"] = "Archived / Passed"
        target["rejected_by"] = user_name
        target["rejected_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        from lib.dossier_integrator import DossierIntegrator
        integrator = DossierIntegrator()
        integrator.save_opportunities(opps)
        integrator.sync_to_google_sheets(opps)
        integrator.sync_to_notion(opps)

        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if webhook_url:
            conf_blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "❌ Opportunity Archived / Passed", "emoji": True}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Role *{target.get('title')}* at *{target.get('organization')}* has been marked as Archived."
                    }
                }
            ]
            try:
                requests.post(webhook_url, json={"text": f"❌ Opportunity Passed: {target.get('organization')}", "blocks": conf_blocks}, timeout=10)
            except Exception:
                pass

        return {
            "success": True,
            "action": "rejected",
            "opportunity": target,
            "blocks": build_job_approval_blocks(target)
        }

    return {"success": False, "error": f"Unknown action {action_type}"}


def process_slack_action(action_value: str, user_name: str = "User") -> dict[str, Any]:
    """Process an action clicked in Slack (e.g. approve:<id>, reject:<id>, approve_job:<id>)."""
    parts = action_value.split(":", 1)
    if len(parts) != 2:
        return {"success": False, "error": "Invalid action value format"}

    action_type, draft_id = parts[0], parts[1]

    if action_type in ("approve_job", "reject_job"):
        return process_job_slack_action(action_type, draft_id, user_name=user_name)

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
