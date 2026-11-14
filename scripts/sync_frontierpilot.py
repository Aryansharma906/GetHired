#!/usr/bin/env python3
"""FrontierPilot 2.0 Autonomous CLI Synchronization Utility.

Synchronizes career opportunities, applications, and documents across:
- Google Gemini (Job alignment scoring & tailoring)
- Google Sheets (Pipeline table sync & CSV export)
- Google Drive (Resume & cover letter storage manifest)
- Gmail (Recruiter outreach & interview alert scanner)
- Notion (Database Kanban sync)
- Slack (Real-time executive status reporting)

Usage:
    python3 scripts/sync_frontierpilot.py --all
    python3 scripts/sync_frontierpilot.py --sheets
    python3 scripts/sync_frontierpilot.py --drive
    python3 scripts/sync_frontierpilot.py --gmail
    python3 scripts/sync_frontierpilot.py --notion
    python3 scripts/sync_frontierpilot.py --gemini
    python3 scripts/sync_frontierpilot.py --status
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib._env import load_env
from lib.frontierpilot_integrator import FrontierPilotIntegrator

load_env()


def print_banner():
    print("=" * 65)
    print("🚀 FRONTIERPILOT 2.0 CAREER COCKPIT & INTEGRATION HUB")
    print("=" * 65)


def check_status(integrator: FrontierPilotIntegrator):
    print("\n🔍 Service Connection Status:")
    opps = integrator.load_opportunities()
    print(f"  • Tracked Opportunities:  {len(opps)} active roles")

    # Gemini
    gemini_status = "✅ Connected (API Key present)" if integrator.gemini_key else "⚠️ Missing GEMINI_API_KEY"
    print(f"  • 🤖 Google Gemini:       {gemini_status}")

    # Sheets
    sheets_mode = "✅ Live API (Token + Sheet ID)" if (integrator.google_access_token and integrator.google_sheet_id) else "📁 Staged CSV (Direct Import Ready)"
    print(f"  • 📊 Google Sheets:       {sheets_mode}")

    # Drive
    drive_mode = "✅ Live Drive API" if integrator.google_access_token else "📁 Staged Manifest (Local Folder Ready)"
    print(f"  • ☁️ Google Drive:        {drive_mode}")

    # Gmail
    gmail_mode = "✅ Live Mailbox Scanner" if integrator.google_access_token else "📁 Simulation / OAuth Ready"
    print(f"  • 📬 Gmail:               {gmail_mode}")

    # Notion
    notion_mode = "✅ Live Notion API" if (integrator.notion_api_key and integrator.notion_database_id) else "📁 Staged CSV (Database Table Ready)"
    print(f"  • 📝 Notion:              {notion_mode}")

    # Slack
    slack_status = "✅ Connected" if integrator.slack_webhook else "⚠️ Missing SLACK_WEBHOOK_URL"
    print(f"  • 💬 Slack Reporting:     {slack_status}")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="FrontierPilot Unified Integration Sync")
    parser.add_argument("--all", action="store_true", help="Sync all services and dispatch Slack summary")
    parser.add_argument("--sheets", action="store_true", help="Sync opportunities to Google Sheets / CSV")
    parser.add_argument("--drive", action="store_true", help="Stage & sync resumes to Google Drive")
    parser.add_argument("--gmail", action="store_true", help="Scan Gmail for recruiter updates")
    parser.add_argument("--notion", action="store_true", help="Sync pipeline to Notion Database")
    parser.add_argument("--gemini", action="store_true", help="Score opportunities using Google Gemini")
    parser.add_argument("--dispatch-jobs", action="store_true", help="Send top job approval cards to Slack")
    parser.add_argument("--digest", action="store_true", help="Send Career Radar digest to Slack")
    parser.add_argument("--package", type=str, metavar="OPP_ID", help="Generate complete application package ZIP for an opportunity")
    parser.add_argument("--pitch", type=str, metavar="OPP_ID", help="Generate 3-sentence recruiter DM & 1-page PoW plan")
    parser.add_argument("--status", action="store_true", help="Check connectivity status of all services")

    args = parser.parse_args()
    print_banner()

    integrator = FrontierPilotIntegrator()

    # Default to status if no flag provided
    if not any([args.all, args.sheets, args.drive, args.gmail, args.notion, args.gemini, args.dispatch_jobs, args.digest, args.package, args.pitch, args.status]):
        args.status = True

    if args.status:
        check_status(integrator)
        return

    if args.package:
        from lib.job_hunter_engine import JobHunterEngine
        opps = integrator.load_opportunities()
        target = next((o for o in opps if o.get("id") == args.package or args.package.lower() in o.get("organization", "").lower()), None)
        if not target:
            print(f"❌ Opportunity '{args.package}' not found in tracker.")
            return
        print(f"\n📦 Building complete application bundle for: [{target.get('organization')}] {target.get('title')}")
        engine = JobHunterEngine()
        bundle_res = engine.create_complete_application_bundle(target)
        print(f"✅ Application package generated successfully!")
        print(f"  • ZIP File:     {bundle_res.get('zip_path')}")
        print(f"  • Files:        {', '.join(bundle_res.get('bundle_files', []))}")
        print(f"  • ATS Keywords: {', '.join(bundle_res.get('ats_keywords', []))}")
        return

    if args.pitch:
        from lib.job_hunter_engine import JobHunterEngine
        opps = integrator.load_opportunities()
        target = next((o for o in opps if o.get("id") == args.pitch or args.pitch.lower() in o.get("organization", "").lower()), None)
        if not target:
            print(f"❌ Opportunity '{args.pitch}' not found in tracker.")
            return
        print(f"\n🎯 Direct Recruiter DM & Tactical PoW Plan for: [{target.get('organization')}] {target.get('title')}")
        engine = JobHunterEngine()
        dm_data = engine.generate_recruiter_outreach_dm(target)
        pow_plan = engine.generate_proof_of_work_plan(target)
        print("\n" + "=" * 50)
        print("💬 3-SENTENCE RECRUITER LINKEDIN DM (Vaibhav Sisinty Framework):")
        print("=" * 50)
        print(dm_data.get("linkedin_dm_3_sentences"))
        print("\n" + "=" * 50)
        print("🏗️ 1-PAGE TACTICAL PROOF-OF-WORK PLAN:")
        print("=" * 50)
        print(pow_plan)
        return

    if args.gemini or args.all:
        print("\n🤖 Running Google Gemini scoring on tracked roles...")
        opps = integrator.load_opportunities()
        scored_count = 0
        to_score = opps if args.gemini else [o for o in opps if "match_score" not in o][:3]
        for o in to_score:
            res = integrator.score_opportunity_with_gemini(o)
            o["match_score"] = res.get("match_score", 90)
            o["matching_skills"] = res.get("matching_skills", [])
            o["gaps_or_growth_areas"] = res.get("gaps_or_growth_areas", [])
            o["executive_summary"] = res.get("executive_summary", "")
            scored_count += 1
            print(f"  • [{o.get('organization')}] {o.get('title')}: {o['match_score']}% match")
        integrator.save_opportunities(opps)
        print(f"✅ Gemini scored {scored_count} opportunities.")

    if args.sheets or args.all:
        print("\n📊 Syncing to Google Sheets...")
        res = integrator.sync_to_google_sheets()
        print(f"  • Mode: {res.get('mode')}")
        if "csv_path" in res:
            print(f"  • Exported: {res['csv_path']}")
        print(f"✅ Google Sheets sync complete.")

    if args.drive or args.all:
        print("\n☁️ Syncing tailored resumes to Google Drive...")
        res = integrator.sync_resumes_to_google_drive()
        print(f"  • Mode: {res.get('mode')}")
        print(f"  • Files: {res.get('files_ready', 0)} files in manifest ({res.get('manifest_file')})")
        print(f"✅ Google Drive staging complete.")

    if args.gmail or args.all:
        print("\n📬 Scanning Gmail for recruiter updates...")
        res = integrator.scan_gmail_for_updates()
        print(f"  • Mode: {res.get('mode')}")
        alerts = res.get("recent_alerts", [])
        print(f"  • Alerts found: {len(alerts)}")
        for a in alerts:
            print(f"    - {a.get('snippet', '')[:80]}...")
        print(f"✅ Gmail scan complete.")

    if args.notion or args.all:
        print("\n📝 Syncing to Notion Database...")
        res = integrator.sync_to_notion()
        print(f"  • Mode: {res.get('mode')}")
        if "csv_path" in res:
            print(f"  • Exported: {res['csv_path']}")
        print(f"✅ Notion sync complete.")

    if args.all:
        print("\n💬 Dispatching unified summary card to Slack...")
        summary = integrator.run_full_frontierpilot_sync()
        print(f"✅ Full FrontierPilot sync finished at {summary.get('timestamp')}.")

    from lib.slack_approver import send_job_approval_to_slack, send_job_radar_digest_to_slack

    if args.digest or args.all:
        print("\n📡 Dispatching Career Radar digest to Slack...")
        opps = integrator.load_opportunities()
        digest_res = send_job_radar_digest_to_slack(opps)
        if digest_res.get("success"):
            print("✅ Career Radar digest sent to Slack.")
        else:
            print(f"⚠️ Digest not sent: {digest_res.get('error')}")

    if args.dispatch_jobs or args.all:
        print("\n🎯 Dispatching top priority job approval card to Slack...")
        opps = integrator.load_opportunities()
        # Find highest fit opportunity not yet approved
        pending = [o for o in opps if "Approved" not in o.get("status", "") and "Archived" not in o.get("status", "")]
        if pending:
            pending.sort(key=lambda x: int(x.get("match_score", 90)), reverse=True)
            top_opp = pending[0]
            card_res = send_job_approval_to_slack(top_opp)
            if card_res.get("success"):
                print(f"✅ Dispatched approval card for: [{top_opp.get('organization')}] {top_opp.get('title')}")
            else:
                print(f"⚠️ Approval card not sent: {card_res.get('error')}")
        else:
            print("ℹ️ All tracked opportunities have already been approved or archived.")


if __name__ == "__main__":
    main()
