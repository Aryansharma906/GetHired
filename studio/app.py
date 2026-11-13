#!/usr/bin/env python3
"""Approval Studio Web Platform for LinkedIn automation.

Provides a local web dashboard at http://localhost:5050 to review, approve,
edit, copy, or generate LinkedIn drafts in 1 click.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request, redirect, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib._env import load_env
from lib.drafts_store import create_draft, get_draft, list_drafts
from lib.gemini_generator import generate_post_with_gemini
from lib.slack_approver import process_slack_action, send_draft_to_slack

load_env()

app = Flask(__name__, template_folder=str(ROOT / "studio" / "templates"))
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/media/<path:filename>")
def serve_media(filename: str):
    media_dir = ROOT / "testing" / "images"
    return send_from_directory(str(media_dir), filename)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/drafts", methods=["GET"])
def get_all_drafts():
    return jsonify(list_drafts())


@app.route("/api/drafts/<draft_id>/approve", methods=["POST"])
def approve_draft_endpoint(draft_id: str):
    res = process_slack_action(f"approve:{draft_id}", user_name="Aryan")
    return jsonify(res)


@app.route("/api/drafts/<draft_id>/reject", methods=["POST"])
def reject_draft_endpoint(draft_id: str):
    res = process_slack_action(f"reject:{draft_id}", user_name="Aryan")
    return jsonify(res)


@app.route("/api/drafts/<draft_id>", methods=["DELETE"])
def delete_draft_endpoint(draft_id: str):
    drafts = list_drafts()
    remaining = [d for d in drafts if d.get("id") != draft_id]
    from lib.drafts_store import _write_queue
    _write_queue(remaining)
    return jsonify({"success": True})


@app.route("/auth/linkedin", methods=["GET"])
def linkedin_oauth_login():
    """Redirect user to LinkedIn OAuth2 consent screen."""
    from testing.linkedin_official_client import LinkedInOfficialClient
    client = LinkedInOfficialClient()
    if not client.client_id:
        return "Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env first.", 400
    return redirect(client.get_authorization_url())


@app.route("/auth/linkedin/callback", methods=["GET"])
def linkedin_oauth_callback():
    """Handle OAuth2 callback and save access token directly to .env."""
    error = request.args.get("error")
    error_desc = request.args.get("error_description")
    if error:
        return f"LinkedIn OAuth Error ({error}): {error_desc}", 400

    code = request.args.get("code")
    if not code:
        return "Authorization code missing", 400

    from testing.linkedin_official_client import LinkedInOfficialClient
    client = LinkedInOfficialClient()
    token_data = client.exchange_code_for_token(code)
    access_token = token_data.get("access_token")

    if not access_token:
        return f"OAuth failed: {token_data}", 500

    # Auto-save token to testing/linkedin_credentials.env scratch file
    creds_path = ROOT / "testing" / "linkedin_credentials.env"
    lines = creds_path.read_text().splitlines() if creds_path.exists() else []
    new_lines = [l for l in lines if not l.startswith("LINKEDIN_ACCESS_TOKEN=")]
    new_lines.append(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    creds_path.write_text("\n".join(new_lines) + "\n")

    return """<!DOCTYPE html>
    <html>
    <head><title>LinkedIn Connected</title><style>body { font-family: -apple-system, sans-serif; background: #0f172a; color: white; padding: 40px; text-align: center; }</style></head>
    <body>
        <h1>✅ LinkedIn Official API Connected!</h1>
        <p>Access token has been safely stored in your local configuration.</p>
        <p>You can now post unlimited LinkedIn updates with zero third-party limits.</p>
        <a href="/" style="display:inline-block; margin-top:20px; background:#3b82f6; color:white; padding:12px 24px; border-radius:8px; text-decoration:none;">Open Studio</a>
    </body>
    </html>"""


@app.route("/api/linkedin/token", methods=["GET", "POST"])
def linkedin_token_api():
    from testing.linkedin_official_client import LinkedInOfficialClient
    client = LinkedInOfficialClient()
    creds_path = ROOT / "testing" / "linkedin_credentials.env"

    if request.method == "POST":
        data = request.get_json() or {}
        token = data.get("access_token", "").strip()
        if not token:
            return jsonify({"success": False, "error": "access_token required"}), 400

        lines = creds_path.read_text().splitlines() if creds_path.exists() else []
        new_lines = [l for l in lines if not l.startswith("LINKEDIN_ACCESS_TOKEN=")]
        new_lines.append(f"LINKEDIN_ACCESS_TOKEN={token}")
        creds_path.write_text("\n".join(new_lines) + "\n")
        return jsonify({"success": True, "message": "Token saved successfully"})

    return jsonify({
        "client_id": client.client_id,
        "has_token": bool(client.access_token),
        "auth_url": client.get_authorization_url() if client.client_id else None,
    })


DEFAULT_OPPORTUNITIES = [
    {
        "id": "gsoc-2026",
        "title": "Open Source AI & Systems Contributor",
        "organization": "Google Summer of Code (GSoC)",
        "category": "Open Source Fellowship",
        "deadline": "March 31 (Annual contributor proposal window)",
        "cycle": "Annual Summer Batch",
        "stipend": "$1,500 – $3,300+ (Stipend)",
        "status": "Upcoming / Preparing Proposals",
        "url": "https://summerofcode.withgoogle.com/",
        "match_reason": "High synergy with Python, systems evaluation, and LLM prompt security research.",
        "tags": ["AI/ML", "Open Source", "Google", "Systems"]
    },
    {
        "id": "lfx-2026-term3",
        "title": "Linux Foundation Mentee (Cloud Native & AI Infra)",
        "organization": "Linux Foundation (LFX)",
        "category": "Mentorship & Internship",
        "deadline": "August 18 (Fall) / Jan 2027 (Spring)",
        "cycle": "Tri-annual Cohorts",
        "stipend": "$3,000 – $6,600",
        "status": "Open for Exploration",
        "url": "https://mentorship.lfx.linuxfoundation.org/",
        "match_reason": "Direct match for Linux, backend data pipelines, and CNCF ecosystem projects.",
        "tags": ["Cloud-Native", "Linux", "Kubernetes", "Systems"]
    },
    {
        "id": "mlh-fellowship",
        "title": "Open Source Software & AI Fellow",
        "organization": "Major League Hacking (MLH)",
        "category": "Global Fellowship",
        "deadline": "August 31 (Fall) / Rolling for Spring",
        "cycle": "Spring / Summer / Fall",
        "stipend": "$5,000 Educational Grant",
        "status": "Active / Rolling Applications",
        "url": "https://fellowship.mlh.io/",
        "match_reason": "Perfect match for remote engineering contributions and student developer cohorts.",
        "tags": ["Software Engineering", "AI", "Open Source"]
    },
    {
        "id": "github-octernships",
        "title": "Open Source Engineering & Systems Intern",
        "organization": "GitHub Education & Partner Orgs",
        "category": "Global Remote Internship",
        "deadline": "Rolling (Monthly project cycles)",
        "cycle": "Year-Round Batches",
        "stipend": "$500 – $2,500/month (Stipend)",
        "status": "Active / Rolling Applications",
        "url": "https://github.com/education/octernships",
        "match_reason": "High synergy with public GitHub repositories, open-source code contribution, and automated pipelines.",
        "tags": ["GitHub", "Open Source", "Remote", "SWE"]
    },
    {
        "id": "anthropic-safety-fellow",
        "title": "Model Alignment & Red-Teaming Research Fellow",
        "organization": "Anthropic",
        "category": "Frontier AI Safety Fellowship",
        "deadline": "Rolling Applications",
        "cycle": "4–6 month Fellowship Cohorts",
        "stipend": "Top-tier Frontier Lab Pay (~$15,000+/month)",
        "status": "Active / Rolling Applications",
        "url": "https://www.anthropic.com/careers",
        "match_reason": "100% direct match for Aryan's published paper on LLM prompt injection and semantic security.",
        "tags": ["Anthropic", "AI Safety", "Red Teaming", "Claude"]
    },
    {
        "id": "microsoft-research-intern",
        "title": "AI & Systems Research Intern",
        "organization": "Microsoft Research (MSR)",
        "category": "Tier-1 Industrial AI Lab Internship",
        "deadline": "Rolling (Opens Fall for Summer)",
        "cycle": "12-week Summer Batch",
        "stipend": "$8,000 – $10,500/month + Housing",
        "status": "Active / Rolling Applications",
        "url": "https://careers.microsoft.com/v2/global/en/students/research",
        "match_reason": "Synergistic with LLM prompt vulnerability publication, AI evaluation at Handshake, and safety alignment.",
        "tags": ["Microsoft", "AI Research", "NLP", "Security"]
    },
    {
        "id": "cern-openlab-2027",
        "title": "Computing & AI Research Student Intern",
        "organization": "CERN (Geneva, Switzerland)",
        "category": "Scientific Computing & AI Residency",
        "deadline": "January 31 annually",
        "cycle": "Summer 9-week Residency",
        "stipend": "~90 CHF/day (~$3,000/mo tax-free) + Travel",
        "status": "Applications Open Nov – Jan",
        "url": "https://openlab.cern/education/summer-student-programme",
        "match_reason": "Aligns directly with NASA Sagan workshop background, computational pipelines, and physics data analysis.",
        "tags": ["CERN", "High Performance Computing", "AI", "Europe"]
    },
    {
        "id": "google-student-researcher",
        "title": "Student Researcher (AI / Deep Learning)",
        "organization": "Google Careers",
        "category": "Big Tech Research Internship",
        "deadline": "Rolling (Opens Aug – Oct annually)",
        "cycle": "Summer Cycle",
        "stipend": "Top-tier Big Tech SWE Compensation",
        "status": "Active / Rolling Applications",
        "url": "https://careers.google.com/students/",
        "match_reason": "Strong alignment with LLM evaluation, prompt injection publication, and CS50x rigor.",
        "tags": ["AI Research", "Deep Learning", "Google", "LLMs"]
    },
    {
        "id": "openai-residency",
        "title": "AI Research & Engineering Resident",
        "organization": "OpenAI",
        "category": "Frontier Tech Research Fellowship",
        "deadline": "Rolling Applications",
        "cycle": "6-month Full-Time Cohorts",
        "stipend": "$210,000/year annualized (~$17,500/month)",
        "status": "Open for Applications",
        "url": "https://openai.com/careers/",
        "match_reason": "Designed for software engineers transitioning into frontier model evaluation and semantic safety defense.",
        "tags": ["OpenAI", "Frontier AI", "LLM Safety", "Silicon Valley"]
    },
    {
        "id": "outreachy-internship",
        "title": "Distributed Systems & Machine Learning Intern",
        "organization": "Outreachy / SFC",
        "category": "Remote Internship",
        "deadline": "Aug 31 (Dec Cohort) / Feb 13 (May Cohort)",
        "cycle": "Bi-annual",
        "stipend": "$7,000 Total Stipend",
        "status": "Contribution Period Prep",
        "url": "https://www.outreachy.org/",
        "match_reason": "Strong alignment with data engineering, Python tools, and open-source tooling.",
        "tags": ["Python", "Data", "Distributed Systems"]
    },
    {
        "id": "uber-star-swe-intern",
        "title": "Backend & Data Platform Engineering Intern",
        "organization": "Uber Technologies",
        "category": "Big Tech Early Career Internship",
        "deadline": "Rolling (Fall cycle)",
        "cycle": "Summer Cycle",
        "stipend": "$50 – $65/hr (~$9,000/month) + Relocation",
        "status": "Active / Rolling Applications",
        "url": "https://www.uber.com/us/en/careers/university/",
        "match_reason": "Systems architecture, high-throughput backend APIs, and Python/microservice data flows.",
        "tags": ["Uber", "Big Tech", "Distributed Systems", "SWE"]
    },
    {
        "id": "summer-of-protocols",
        "title": "Autonomous Systems & Protocol Researcher",
        "organization": "Summer of Protocols / Ethereum Ecosystem",
        "category": "Funded Research Grant & Fellowship",
        "deadline": "April 15 annually",
        "cycle": "18-week Summer Cohort",
        "stipend": "$1,000 – $10,000 Research Grant",
        "status": "Active / Proposal Prep",
        "url": "https://summerofprotocols.com/",
        "match_reason": "Ideal for Aryan's JABSON AI autonomous agent orchestration and semantic security research thesis.",
        "tags": ["Research Grant", "Autonomous Agents", "Protocols"]
    },
    {
        "id": "redhat-swe-intern",
        "title": "Linux Kernel & Cloud Infrastructure Intern",
        "organization": "Red Hat / IBM",
        "category": "Open Source Enterprise SWE",
        "deadline": "Rolling (Fall & Spring postings)",
        "cycle": "Summer / Year-Round Co-op",
        "stipend": "Competitive Global Tech Stipend",
        "status": "Active / Rolling Postings",
        "url": "https://www.redhat.com/en/jobs/students-graduates",
        "match_reason": "Direct fit for Linux internals, container architecture, and Python open-source automation.",
        "tags": ["Red Hat", "Linux", "Kubernetes", "Cloud"]
    },
    {
        "id": "emergent-ventures",
        "title": "Moonshot AI & Systems Grantee",
        "organization": "Mercatus Center (Tyler Cowen)",
        "category": "Equity-Free Grant",
        "deadline": "Rolling / Open Year-Round",
        "cycle": "Continuous",
        "stipend": "$10,000 – $100,000+ Non-Dilutive Grant",
        "status": "Open Year-Round",
        "url": "https://www.mercatus.org/emergent-ventures",
        "match_reason": "Tailored for autonomous multi-agent systems and JABSON AI founder velocity.",
        "tags": ["Grants", "AI Founders", "Autonomous Agents"]
    },
    {
        "id": "hpair-fellowship",
        "title": "International Tech & Governance Delegate",
        "organization": "Harvard College (HPAIR)",
        "category": "Global Conference & Fellowship",
        "deadline": "Annual Selection Cycle",
        "cycle": "Annual",
        "stipend": "Executive Leadership & Global Network",
        "status": "Selected Delegate (Alumnus / Ongoing)",
        "url": "https://hpair.org/",
        "match_reason": "Existing verified selection on Aryan's resume.",
        "tags": ["Leadership", "Harvard", "Global Tech"]
    }
]


@app.route("/api/opportunities", methods=["GET", "POST"])
def opportunities_api():
    opps_path = ROOT / "testing" / "opportunities_tracker.json"
    opps = []
    if opps_path.exists():
        try:
            opps = json.loads(opps_path.read_text(encoding="utf-8"))
        except Exception as e:
            opps = []

    if not opps or not isinstance(opps, list) or len(opps) == 0:
        opps = DEFAULT_OPPORTUNITIES
        opps_path.parent.mkdir(parents=True, exist_ok=True)
        opps_path.write_text(json.dumps(opps, indent=2), encoding="utf-8")

    if request.method == "POST":
        data = request.get_json() or {}
        title = data.get("title", "").strip()
        org = data.get("organization", "").strip()
        if not title or not org:
            return jsonify({"success": False, "error": "Title and organization required"}), 400

        import uuid
        new_opp = {
            "id": f"opp_{uuid.uuid4().hex[:6]}",
            "title": title,
            "organization": org,
            "category": data.get("category", "Job / Internship"),
            "deadline": data.get("deadline", "Rolling"),
            "cycle": data.get("cycle", "2026"),
            "stipend": data.get("stipend", "Competitive"),
            "status": data.get("status", "Active"),
            "url": data.get("url", "#"),
            "match_reason": data.get("match_reason", "Custom tracked role"),
            "tags": data.get("tags", ["Opportunity"])
        }
        opps.insert(0, new_opp)
        opps_path.write_text(json.dumps(opps, indent=2), encoding="utf-8")
        return jsonify({"success": True, "opportunity": new_opp})

    return jsonify({"success": True, "opportunities": opps})


@app.route("/api/opportunities/<opp_id>/resume", methods=["POST"])
def generate_opportunity_resume(opp_id: str):
    opps_path = ROOT / "testing" / "opportunities_tracker.json"
    try:
        opps = json.loads(opps_path.read_text(encoding="utf-8"))
    except Exception:
        opps = []

    target_opp = next((o for o in opps if o.get("id") == opp_id), None)
    if not target_opp:
        return jsonify({"success": False, "error": f"Opportunity {opp_id} not found"}), 404

    from scripts.generate_tailored_resume import tailor_resume
    tailored = tailor_resume(target_opp.get("title", "Software Engineer"), target_opp.get("organization", "Company"))
    
    out_dir = ROOT / "testing" / "tailored_resumes"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"Aryan_Sharma_{target_opp.get('organization', '').replace(' ', '_')}_{opp_id}.md"
    file_path = out_dir / filename
    file_path.write_text(tailored, encoding="utf-8")

    return jsonify({
        "success": True,
        "resume_markdown": tailored,
        "file_name": filename,
        "file_path": str(file_path),
    })


# =========================================================================
# Dossier Career Hub & Multi-Platform Integration API
# =========================================================================

@app.route("/api/dossier/status", methods=["GET"])
def dossier_status_api():
    """Return status of all 5 connected services and opportunity pipeline."""
    from lib.dossier_integrator import DossierIntegrator
    integrator = DossierIntegrator()
    opps = integrator.load_opportunities()
    
    return jsonify({
        "success": True,
        "opportunities_count": len(opps),
        "gemini": bool(integrator.gemini_key),
        "google_sheets": "live_api" if (integrator.google_access_token and integrator.google_sheet_id) else "staged_csv",
        "google_drive": "live_api" if integrator.google_access_token else "staged_manifest",
        "gmail": "live_mailbox" if integrator.google_access_token else "oauth_ready",
        "notion": "live_api" if (integrator.notion_api_key and integrator.notion_database_id) else "staged_csv",
        "slack": bool(integrator.slack_webhook),
        "staged_files": {
            "sheets_csv": (ROOT / "testing" / "dossier_exports" / "google_sheets_pipeline.csv").exists(),
            "drive_manifest": (ROOT / "testing" / "dossier_exports" / "google_drive_manifest.json").exists(),
            "notion_csv": (ROOT / "testing" / "dossier_exports" / "notion_database_pipeline.csv").exists(),
        }
    })


@app.route("/api/dossier/sync", methods=["POST"])
def dossier_sync_api():
    """Execute on-demand sync for all or specific services."""
    from lib.dossier_integrator import DossierIntegrator
    integrator = DossierIntegrator()
    data = request.get_json() or {}
    action = data.get("action", "all")

    if action == "all":
        result = integrator.run_full_dossier_sync()
        return jsonify({"success": True, "action": "all", "result": result})
    elif action == "sheets":
        result = integrator.sync_to_google_sheets()
        return jsonify({"success": True, "action": "sheets", "result": result})
    elif action == "drive":
        result = integrator.sync_resumes_to_google_drive()
        return jsonify({"success": True, "action": "drive", "result": result})
    elif action == "gmail":
        result = integrator.scan_gmail_for_updates()
        return jsonify({"success": True, "action": "gmail", "result": result})
    elif action == "notion":
        result = integrator.sync_to_notion()
        return jsonify({"success": True, "action": "notion", "result": result})
    elif action == "gemini":
        opps = integrator.load_opportunities()
        scored = 0
        for o in opps:
            res = integrator.score_opportunity_with_gemini(o)
            o["match_score"] = res.get("match_score", 90)
            o["matching_skills"] = res.get("matching_skills", [])
            o["gaps_or_growth_areas"] = res.get("gaps_or_growth_areas", [])
            o["executive_summary"] = res.get("executive_summary", "")
            scored += 1
        integrator.save_opportunities(opps)
        return jsonify({"success": True, "action": "gemini", "scored_count": scored})
    else:
        return jsonify({"success": False, "error": f"Unknown action: {action}"}), 400


@app.route("/api/dossier/opportunities/<opp_id>/score", methods=["POST"])
def score_single_opportunity_api(opp_id: str):
    """Score a specific opportunity against Aryan's profile with Google Gemini."""
    from lib.dossier_integrator import DossierIntegrator
    integrator = DossierIntegrator()
    opps = integrator.load_opportunities()
    target = next((o for o in opps if o.get("id") == opp_id), None)
    if not target:
        return jsonify({"success": False, "error": "Opportunity not found"}), 404

    data = request.get_json() or {}
    job_desc = data.get("job_description")

    res = integrator.score_opportunity_with_gemini(target, job_description=job_desc)
    target["match_score"] = res.get("match_score", 90)
    target["matching_skills"] = res.get("matching_skills", [])
    target["gaps_or_growth_areas"] = res.get("gaps_or_growth_areas", [])
    target["executive_summary"] = res.get("executive_summary", "")
    integrator.save_opportunities(opps)

    return jsonify({"success": True, "opportunity": target, "score_data": res})


@app.route("/api/dossier/export/<kind>", methods=["GET"])
def export_dossier_file(kind: str):
    """Download staged CSV or manifest for Google Sheets, Notion, or Drive."""
    staging_dir = ROOT / "testing" / "dossier_exports"
    if kind == "sheets":
        file_path = staging_dir / "google_sheets_pipeline.csv"
        mimetype = "text/csv"
    elif kind == "notion":
        file_path = staging_dir / "notion_database_pipeline.csv"
        mimetype = "text/csv"
    elif kind == "drive":
        file_path = staging_dir / "google_drive_manifest.json"
        mimetype = "application/json"
    else:
        return jsonify({"error": "Unknown export kind"}), 404

    if not file_path.exists():
        # Trigger regeneration
        from lib.dossier_integrator import DossierIntegrator
        d = DossierIntegrator()
        d.sync_to_google_sheets()
        d.sync_resumes_to_google_drive()
        d.sync_to_notion()

    from flask import send_file
    return send_file(str(file_path), as_attachment=True, download_name=file_path.name, mimetype=mimetype)


@app.route("/action/<action_type>/<draft_id>", methods=["GET"])
def direct_action_page(action_type: str, draft_id: str):
    """1-Tap instant action URL from mobile Slack without relying on Slack Interactivity limits."""
    if action_type not in ("approve", "reject"):
        return "Invalid action", 400

    res = process_slack_action(f"{action_type}:{draft_id}", user_name="Aryan (Mobile 1-Tap)")
    draft = get_draft(draft_id) or {}
    topic = draft.get("topic", "LinkedIn Post")

    if action_type == "approve":
        status_badge = "✅ Approved & Scheduled"
        bg = "#10b981"
        sub = "Post has been scheduled into Publora for optimal LinkedIn distribution."
    else:
        status_badge = "❌ Post Rejected"
        bg = "#ef4444"
        sub = "Draft has been archived locally."

    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{status_badge}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; text-align: center; }}
            .card {{ background: #1e293b; border-radius: 16px; padding: 32px 24px; max-width: 480px; margin: 40px auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            .badge {{ display: inline-block; background: {bg}; color: white; padding: 8px 18px; border-radius: 9999px; font-weight: 700; font-size: 16px; margin-bottom: 20px; }}
            h2 {{ font-size: 20px; margin-bottom: 12px; line-height: 1.4; }}
            p {{ color: #94a3b8; font-size: 14px; line-height: 1.6; margin-bottom: 28px; }}
            a.btn {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">{status_badge}</div>
            <h2>{topic}</h2>
            <p>{sub}</p>
            <a href="/" class="btn">📱 Open Approval Studio</a>
        </div>
    </body>
    </html>"""
    return html


@app.route("/api/drafts/<draft_id>/restore", methods=["POST"])
def restore_draft_endpoint(draft_id: str):
    from lib.drafts_store import update_draft_status
    updated = update_draft_status(draft_id, "pending_approval")
    return jsonify({"success": True, "draft": updated})


@app.route("/api/publora/posts", methods=["GET"])
def get_publora_posts():
    try:
        from lib.publora_client import PubloraClient
        client = PubloraClient()
        posts = client._session.get(f"{client.BASE_URL}/list-posts", timeout=10).json()
        return jsonify(posts)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "posts": []})


@app.route("/api/drafts/generate", methods=["POST"])
def generate_draft_endpoint():
    data = request.get_json() or {}
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"success": False, "error": "Topic is required"}), 400

    style = data.get("style") or "Vaibhav Sisinty Growth Storytelling + Senior Engineer Depth"
    instructions = data.get("instructions", "").strip() or None
    length_preset = data.get("length", "long")
    hook_preference = data.get("hook_formula") or None

    gemini_res = generate_post_with_gemini(
        topic,
        style=style,
        instructions=instructions,
        length_preset=length_preset,
        hook_preference=hook_preference,
    )
    if not gemini_res:
        return jsonify({
            "success": False,
            "error": "Gemini generation failed or timed out. Please try again."
        }), 500

    content = gemini_res.get("content", "").strip()
    hook = gemini_res.get("hook_formula", "Proven Hook")
    angle = gemini_res.get("angle", "Founder Angle")

    draft = create_draft(content=content, topic=topic, hook_formula=hook, angle=angle)
    # Also notify Slack channel
    try:
        send_draft_to_slack(draft)
    except Exception as e:
        print(f"Failed to send draft to Slack: {e}")

    return jsonify({"success": True, "draft": draft})


@app.route("/api/sparks/trigger", methods=["POST"])
def sparks_trigger_endpoint():
    """Webhook endpoint for Google Sparks or external automation routines.
    
    Accepts:
    {
      "topic": "Optional custom topic or prompt",
      "content": "Optional direct post content (if pre-generated by a custom Gem)",
      "auto_generate": true/false,
      "secret": "Optional auth secret"
    }
    """
    data = request.get_json() or {}
    secret = data.get("secret")
    expected_secret = os.environ.get("SPARKS_WEBHOOK_SECRET")
    if expected_secret and secret != expected_secret:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    topic = data.get("topic", "").strip()
    direct_content = data.get("content", "").strip()

    if direct_content:
        # Pre-generated by Custom Gem / Sparks
        hook = data.get("hook_formula", "Gem-Generated Hook")
        angle = data.get("angle", "Sparks Automation")
        draft = create_draft(
            content=direct_content,
            topic=topic or "Gem Post",
            hook_formula=hook,
            angle=angle,
        )
    else:
        # Generate dynamically via Gemini
        if not topic and data.get("auto_generate", True):
            from scripts.run_slack_pipeline import SAMPLE_FOUNDER_POSTS
            import random
            picked = random.choice(SAMPLE_FOUNDER_POSTS)
            topic = picked["topic"]

        if not topic:
            return jsonify({"success": False, "error": "Topic or content is required"}), 400

        gemini_res = generate_post_with_gemini(
            topic,
            style="Aryan Sharma Systems Depth + Vaibhav Sisinty Growth Storytelling + Raj Shamani Unit Economics",
            length_preset="long",
        )
        if not gemini_res:
            return jsonify({"success": False, "error": "Gemini generation failed"}), 500

        draft = create_draft(
            content=gemini_res.get("content", "").strip(),
            topic=topic,
            hook_formula=gemini_res.get("hook_formula", "Proven Hook"),
            angle=gemini_res.get("angle", "Tri-Voice Synthesis"),
        )

    # Automatically dispatch Block Kit card to Slack
    slack_sent = False
    try:
        slack_sent = send_draft_to_slack(draft)
    except Exception as e:
        print(f"Failed to dispatch Sparks draft to Slack: {e}")

    return jsonify({
        "success": True,
        "draft_id": draft.get("id"),
        "slack_dispatched": slack_sent,
        "draft": draft,
    })


@app.route("/slack/interactions", methods=["POST"])
def slack_interactions():
    """Handle interactive button clicks from Slack ([Approve], [Reject])."""
    import json
    payload_raw = request.form.get("payload")
    if not payload_raw:
        payload_json = request.get_json(silent=True) or {}
    else:
        try:
            payload_json = json.loads(payload_raw)
        except Exception:
            payload_json = {}

    actions = payload_json.get("actions", [])
    user_info = payload_json.get("user", {})
    user_name = user_info.get("name") or user_info.get("username") or "Aryan (Slack)"

    if not actions:
        return jsonify({"text": "No action received"}), 400

    first_action = actions[0]
    action_val = first_action.get("value", "")

    result = process_slack_action(action_val, user_name=user_name)

    if result.get("success") and "blocks" in result:
        return jsonify({
            "replace_original": True,
            "blocks": result["blocks"],
        })

    return jsonify({"text": f"Processed: {result.get('error') or 'OK'}"})


@app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle Slack Events API for conversational chat with the agent."""
    data = request.get_json(silent=True) or {}

    # 1. URL Verification challenge from Slack
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge")})

    # 2. Event Callback (e.g. app_mention or message)
    if data.get("type") == "event_callback":
        event = data.get("event", {})
        event_type = event.get("type")

        # Ignore bot's own messages to avoid loops
        if event.get("bot_id") or event.get("subtype") == "bot_message":
            return jsonify({"status": "ignored_bot_message"})

        if event_type in ("app_mention", "message"):
            text = event.get("text", "")
            channel = event.get("channel")
            user = event.get("user")

            # Clean out <@BOTID> mentions
            import re
            cleaned_prompt = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
            if not cleaned_prompt:
                cleaned_prompt = "Hello! What can I help you draft or check today?"

            # Generate conversational response or new draft using Gemini
            from lib.gemini_generator import generate_post_with_gemini
            from lib._env import load_env
            import requests, os
            load_env()
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")

            # If user asks to draft or write a post
            if any(k in cleaned_prompt.lower() for k in ["draft", "write", "post", "create", "generate"]):
                gemini_res = generate_post_with_gemini(
                    cleaned_prompt,
                    style="Aryan Sharma Systems Depth + Vaibhav Sisinty Growth Storytelling",
                    length_preset="long",
                )
                if gemini_res:
                    draft = create_draft(
                        content=gemini_res.get("content", "").strip(),
                        topic=cleaned_prompt[:60],
                        hook_formula=gemini_res.get("hook_formula", "Proven Hook"),
                        angle="Slack Conversational Prompt",
                    )
                    send_draft_to_slack(draft)
                    return jsonify({"status": "draft_created_and_sent"})

            # General conversational reply via Gemini
            try:
                api_key = os.getenv("GEMINI_API_KEY")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
                prompt_body = {
                    "contents": [{
                        "parts": [{
                            "text": (
                                "You are Aryan Sharma's AI Systems Assistant and LinkedIn Architect. "
                                "Answer concisely, technically, and authoritatively in 2-4 sentences:\n\n"
                                f"User question: {cleaned_prompt}"
                            )
                        }]
                    }]
                }
                resp = requests.post(url, json=prompt_body, timeout=12).json()
                reply_text = (
                    resp.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "I received your message and I am processing it.")
                )
                if webhook_url:
                    requests.post(webhook_url, json={"text": reply_text}, timeout=10)
            except Exception as e:
                print(f"Chat error: {e}")

            return jsonify({"status": "ok"})

    return jsonify({"status": "ignored"})


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "5050")))
    args, _ = parser.parse_known_args()
    port = args.port
    print(f"🚀 LinkedIn Approval Studio is running on:\n   • Localhost: http://localhost:{port}\n   • Loopback:  http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
