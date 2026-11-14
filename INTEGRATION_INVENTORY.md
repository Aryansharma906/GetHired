# FrontierPilot 2.0 — Integration Inventory

This document maps all external APIs, service boundaries, protocols, environment variables, and authentication mechanisms.

---

## 1. External Services Matrix

| Service | Protocol | Environment Variables | Usage & Boundaries | Failure Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini API** | HTTPS REST / v1beta | `GEMINI_API_KEY` | Post generation, match scoring, resume tailoring, PRDs. | Cascade from `gemini-4-hydrogen` to `gemini-3.5-flash-lite`; 3-min circuit breaker cooldown. |
| **Slack Webhooks & API** | HTTPS REST | `SLACK_WEBHOOK_URL`, `SLACK_SIGNING_SECRET` | Dispatches Block Kit cards; receives button actions & events. | HMAC-SHA256 signature verification; immediate HTTP 200 ack. |
| **Publora API** | HTTPS REST | `PUBLORA_API_KEY`, `LINKEDIN_PLATFORM_ID` | Multi-platform post scheduling and live publishing. | Fallback from Direct LinkedIn REST API; error logged in SQLite. |
| **LinkedIn REST API** | HTTPS OAuth 2.0 | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN` | Direct `POST /v2/ugcPosts` without queue delays. | Falls back to Publora client if access token expired. |
| **Apify Scraper Layer** | HTTPS REST | `APIFY_TOKEN` | Reading LinkedIn posts, comment threads, and engagers cookie-free. | Cached LRU 256 entries, 6-hour TTL; manual paste fallback. |
| **Notion API** | HTTPS REST v1 | `NOTION_API_KEY`, `NOTION_DATABASE_ID` | Synchronizes career radar Kanban items with workspace. | Offline-ready JSON staging fallback if credentials absent. |
| **Google Sheets v4** | HTTPS REST v1 | `GOOGLE_ACCESS_TOKEN`, `GOOGLE_SHEET_ID` | Real-time tabular pipeline synchronization. | Offline CSV export ready for 1-click import if token expired. |
| **Google Drive v3** | HTTPS REST v1 | `GOOGLE_ACCESS_TOKEN` | Automated storage and sharing of tailored PDF dossiers. | Local application bundle directory export fallback. |
| **Wix Headless CMS** | HTTPS REST | `WIX_API_KEY`, `WIX_SITE_ID` | Web showcase staging collection for portfolios. | Staged JSON collection in `testing/` fallback. |
| **Ngrok Tunnel** | TLS Reverse Proxy | `NGROK_AUTHTOKEN` | Exposes local Port 5050 to public HTTPS for mobile Slack clicks. | Self-healing watchdog in autonomous dev daemon. |

---

## 2. Credential Security Guardrail

- **Zero Secrets Above `testing/`**: As verified by `scripts/check_no_secrets.py`, no API keys, private tokens, or credentials exist in tracked Git files.
- Local configuration is loaded via `.env` or `testing/linkedin_credentials.env`, both strictly gitignored.
