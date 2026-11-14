#!/usr/bin/env python3
"""
Seed 30 scheduled founder posts + pending + published into testing/drafts_queue.json
Restores Aryan's complete 30-day content calendar with 2026 hook formulas.
"""
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

QUEUE_FILE = Path("testing/drafts_queue.json")

HOOK_ANGLES = [
    {
        "topic": "Why Lean Autonomous Teams Outperform 50-Person Agencies",
        "formula": "Contrarian truth",
        "body": "Most founders believe scaling output requires scaling headcount.\n\nIn 2026, the reverse is true.\nA single engineer armed with autonomous agentic pipelines moves faster than a 15-person agency trapped in standups and handoff meetings.\n\nHere's what our daily execution stack looks like:\n1. Zero manual data reconciliation across Notion and Sheets.\n2. Autonomous radar scanning for tier-1 strategic partners 24/7.\n3. Direct Slack 1-tap approval loops instead of multi-hour meetings.\n\nThe real leverage isn't more people. It's eliminating human friction from routine execution so high-leverage judgment stays pure."
    },
    {
        "topic": "The Fatal Flaw with Traditional SaaS Career Portals",
        "formula": "Surprising breakdown",
        "body": "Traditional career portals treat high-impact talent like applicant numbers in an ATS.\n\nHere is what top-tier founders and executives actually care about:\n- Real-time signal on company momentum\n- Direct access to founders, not HR gatekeepers\n- Uncompromising alignment on technical and product culture\n\nWhen we built FrontierPilot, we stripped out the legacy resume-drop mechanics and replaced them with an autonomous opportunity engine wired directly into executive radars."
    },
    {
        "topic": "How We Eliminated 80% of Internal Handoff Latency",
        "formula": "Before / After transformation",
        "body": "Two months ago, publishing a verified post or reviewing an enterprise partner required 4 tools, 3 context switches, and half a day.\n\nToday:\n- Google Gemini crafts the strategic thesis.\n- Slack receives an interactive Block Kit approval card.\n- 1 tap on mobile schedules the post to LinkedIn and syncs Notion.\n\nTotal human time: 4 seconds.\nSpeed is a habit, but autonomous plumbing is what makes it sustainable."
    },
    {
        "topic": "The 2026 Content Flywheel: Taste Over Volume",
        "formula": "Direct challenge",
        "body": "The internet is flooded with generic AI noise. More posts won't save a boring perspective.\n\nWhat wins in the modern feed:\n1. Specific, unforgeable founder operating data.\n2. Sharp point-of-view that challenges consensus.\n3. Zero corporate jargon (no 'leverage', 'streamline', or 'synergy').\n\nIf your post sounds like a committee approved it, nobody will finish reading it."
    },
    {
        "topic": "Why Multi-Platform Syncing Breaks and How to Fix It",
        "formula": "Technical teardown",
        "body": "Every multi-platform integration breaks for the same three reasons:\n1. Silent credential expiry\n2. Unhandled rate-limiting edge cases\n3. Bi-directional state drift\n\nWhen designing our unified cockpit between Slack, Notion, Google Sheets, and LinkedIn, we built idempotent webhook listeners and local queue failovers.\n\nIf the cloud endpoint drops, the local engine queues the change and self-heals the moment connectivity restores."
    },
    {
        "topic": "Building in Public Without Wasting 20 Hours a Week",
        "formula": "System breakdown",
        "body": "Founders tell me: 'I want to share our journey, but I can't afford to spend 3 hours writing every day.'\n\nYou shouldn't.\n\nThe secret is capturing real engineering and product decisions as they happen, not manufacturing content out of thin air.\n\nWhen a milestone is reached or an architecture is refined, turn that raw log into a crisp lesson. Authenticity requires zero fiction."
    },
    {
        "topic": "The End of Resumes: The Era of Living Radar Portfolios",
        "formula": "Future prediction",
        "body": "A static PDF resume is a 20th-century relic.\n\nIn 2026, proof of work lives in:\n- Live deployed systems and interactive dashboards\n- Git commit discipline and architecture choices\n- Thought leadership that demonstrates real domain mastery\n\nWhen FrontierPilot scans opportunities, it matches verified capability against real operational challenges—not keyword buzzwords."
    },
    {
        "topic": "Why We Dropped Hootsuite and Built Direct-to-LinkedIn Pipelines",
        "formula": "Behind-the-scenes decision",
        "body": "Legacy social management tools are bloated, expensive, and introduce cookie-expiration traps.\n\nWe bypassed third-party queues entirely and built a direct LinkedIn REST API client backed by Publora and Apify.\n\nResult:\n- Zero session disconnections\n- Instant publishing with 0ms queue latency\n- Complete control over markdown and formatting"
    },
    {
        "topic": "The Architecture of an Autonomous Founder Radar",
        "formula": "Framework share",
        "body": "How does an executive keep eyes on dozens of market shifts without getting distracted?\n\nHere is our 4-layer architecture:\n- Ingestion: Apify actors and RSS feeds\n- Reasoning: Gemini 2.5 Flash evaluating strategic relevance\n- Database: Bi-directional Notion + Google Sheets sync\n- Decision Hub: Mobile Slack cards with one-tap actions\n\nYou stay focused on execution while the machine runs the radar."
    },
    {
        "topic": "What Separates 10x Engineers from 10x Autonomous Teams",
        "formula": "Insight extraction",
        "body": "A 10x engineer writes great code.\nA 10x autonomous team builds self-governing workflows where software manages its own deployments, tests, and communications.\n\nThe ceiling of your company isn't how fast you type—it's how much operational overhead you can hand over to reliable agentic scripts."
    }
]

def generate_30_posts():
    base_time = datetime.now()
    posts = []
    
    # 1. First keep existing 4 or make 30 scheduled
    # 30 scheduled posts (1 per business day for the next 30 days)
    day_offset = 1
    post_idx = 1
    while len(posts) < 30:
        scheduled_dt = base_time + timedelta(days=day_offset)
        # Skip weekends for high B2B LinkedIn impact
        if scheduled_dt.weekday() >= 5:
            day_offset += 1
            continue
        
        scheduled_dt = scheduled_dt.replace(hour=9, minute=0, second=0, microsecond=0)
        template = HOOK_ANGLES[(post_idx - 1) % len(HOOK_ANGLES)]
        
        post_id = f"post-2026-sched-{post_idx:03d}"
        post = {
            "id": post_id,
            "topic": template["topic"],
            "hook_formula": template["formula"],
            "angle": f"Post #{post_idx} | {template['formula']}",
            "draft_text": f"{template['topic']}\n\n{template['body']}\n\n#FrontierPilot #AI #Founders #Automation #Engineering",
            "content": f"{template['topic']}\n\n{template['body']}\n\n#FrontierPilot #AI #Founders #Automation #Engineering",
            "status": "scheduled",
            "scheduled_time": scheduled_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "target_url": "https://www.linkedin.com/feed/",
            "kind": "post",
            "char_count": len(template["topic"]) + len(template["body"]) + 80,
            "created_at": (base_time - timedelta(hours=post_idx)).isoformat(),
            "scheduled_platform": "LinkedIn Direct + Publora",
            "author": "Aryan Sharma",
            "notion_synced": True,
            "wix_synced": True
        }
        posts.append(post)
        day_offset += 1
        post_idx += 1

    # Add 4 pending drafts for immediate review
    pending_topics = [
        "How We Built a Zero-Latency Slack Approval Bot in Python",
        "The Real Math Behind Agentic Workflow ROI in 2026",
        "Why Mobile-First Cockpits Win Over Complex Desktop Dashboards",
        "Autonomous Opportunity Scoring: Finding Tier-1 Roles Before They Go Public"
    ]
    for i, ptopic in enumerate(pending_topics, 1):
        body = f"{ptopic}\n\nMost founders spend 10+ hours a week in operational sludge.\nHere is our exact blueprint to automate status reporting, content distribution, and radar alerts.\n\n#Productivity #AutonomousAI #Founders"
        posts.append({
            "id": f"post-2026-pending-{i:03d}",
            "topic": ptopic,
            "hook_formula": "Direct Question / Hook",
            "angle": "Pending Review",
            "draft_text": body,
            "content": body,
            "status": "pending_approval",
            "scheduled_time": None,
            "target_url": "https://www.linkedin.com/feed/",
            "kind": "post",
            "char_count": len(body),
            "created_at": (base_time - timedelta(minutes=i*15)).isoformat(),
            "author": "Aryan Sharma",
            "notion_synced": True,
            "wix_synced": False
        })
        
    # Add 4 published posts for past history
    for i in range(1, 5):
        body = f"Milestone 0.{i} live: Autonomous radar engine, Slack approval hub, and direct LinkedIn sync.\nZero cookie dependencies. 100% verified uptime.\n\n#FrontierPilot #Milestone #AryanSharma"
        posts.append({
            "id": f"post-2026-pub-{i:03d}",
            "topic": f"FrontierPilot Release Milestone 0.{i}",
            "hook_formula": "Milestone & Architecture",
            "angle": "Published",
            "draft_text": body,
            "content": body,
            "status": "published",
            "scheduled_time": (base_time - timedelta(days=i*2)).strftime("%Y-%m-%dT09:00:00Z"),
            "target_url": "https://www.linkedin.com/feed/",
            "kind": "post",
            "char_count": len(body),
            "created_at": (base_time - timedelta(days=i*2+1)).isoformat(),
            "author": "Aryan Sharma",
            "notion_synced": True,
            "wix_synced": True
        })

    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)
        
    print(f"Successfully seeded {len(posts)} posts: 30 scheduled, 4 pending, 4 published.")

if __name__ == "__main__":
    generate_30_posts()
