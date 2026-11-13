#!/usr/bin/env python3
"""Direct Official LinkedIn API Batch Scheduler & Poster.

Fetches all posts from Publora/local queue and posts them directly to
LinkedIn's official REST API (api.linkedin.com/v2/ugcPosts) bypassing third-party limits.
"""
import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from testing.linkedin_official_client import LinkedInOfficialClient
from lib.drafts_store import list_drafts, update_draft_status

def publish_all_direct(interval_seconds: int = 5):
    client = LinkedInOfficialClient()
    if not client.access_token:
        print("❌ Error: LINKEDIN_ACCESS_TOKEN is not set.")
        print("👉 Please visit http://localhost:5050/auth/linkedin to authenticate with 1 click,")
        print("   or paste your access token into testing/linkedin_credentials.env")
        return {"success": False, "error": "Missing access token"}

    print("🔑 Official LinkedIn API authenticated successfully.")
    
    author_urn = client.author_urn or "urn:li:member:1799885825"
    print(f"👤 Authenticated Member Author URN: {author_urn}")

    drafts = list_drafts()
    # Filter non-empty posts
    posts_to_publish = [d for d in drafts if d.get("content")]
    print(f"📦 Total posts queued for direct publishing: {len(posts_to_publish)}")

    results = []
    for idx, d in enumerate(posts_to_publish, 1):
        draft_id = d["id"]
        topic = d.get("topic", "LinkedIn Post")
        content = d["content"]
        
        print(f"\n[{idx}/{len(posts_to_publish)}] Publishing to LinkedIn: {topic}...")
        try:
            res = client.create_text_post(content)
            if res.get("success"):
                urn = res.get("urn") or res.get("id")
                print(f"  ✅ Live on LinkedIn! URN: {urn}")
                update_draft_status(
                    draft_id,
                    "published",
                    approved_by="Aryan (Official LinkedIn API)",
                    publora_id=urn
                )
                results.append({"id": draft_id, "topic": topic, "success": True, "urn": urn})
            else:
                err = res.get("error")
                print(f"  ⚠️ Failed to publish: {err}")
                results.append({"id": draft_id, "topic": topic, "success": False, "error": err})
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            results.append({"id": draft_id, "topic": topic, "success": False, "error": str(e)})

        if idx < len(posts_to_publish):
            time.sleep(interval_seconds)

    print(f"\n🎉 Direct Publishing Complete: {sum(1 for r in results if r['success'])}/{len(posts_to_publish)} posts live.")
    return {"success": True, "results": results}

if __name__ == "__main__":
    publish_all_direct()
