# FrontierPilot 2.0 & LinkedIn Creator Studio — System Architecture
**Version**: 2.1 (Stabilized)  
**Author**: Aryan Sharma (`Orbitron AI` • `aryanaryan.9956@icloud.com`)  
**Status**: Active Production Candidate  
**Date**: November 14, 2026

---

## 1. High-Level Architectural Model

FrontierPilot 2.0 operates as an autonomous, self-healing career intelligence cockpit and LinkedIn thought-leadership studio. It couples low-latency generative AI generation with a strict **Human Taste Gate** (Aryan Sharma) via interactive Slack Block Kit cards.

```
                                  +------------------------------------+
                                  |         Aryan Sharma (Human)       |
                                  |     Mobile Slack Interactive Hub   |
                                  +------------------+-----------------+
                                                     ^
                                                     | (1-Tap Approve / Reject Block Kit Cards)
                                                     v
+----------------------------------------------------+-----------------------------------------------------+
|                                            FRONTIERPILOT CORE HOST                                       |
|                                                                                                          |
|   +--------------------------+       +----------------------------+       +--------------------------+   |
|   |   Unified Flask Core     |       |   Gemini AI Systems        |       |  Vaibhav Growth Studio   |   |
|   |   - Port 5050 PWA        |<----->|   - gemini-4-hydrogen      |<----->|  - GPS Auditor (Prompt)  |   |
|   |   - Session Auth / PIN   |       |   - gemini-3.5-flash-lite  |       |  - Google XYZ Optimizer  |   |
|   |   - Slack Signature HMAC |       |   - Circuit Breaker        |       |  - 90-Day Tactical PRD   |   |
|   +-------------+------------+       +----------------------------+       |  - 3-Sentence Founder DM |   |
|                 |                                                         |  - 60s Video Script      |   |
|                 v                                                         +--------------------------+   |
|   +--------------------------+       +----------------------------+                                      |
|   |   SQLite WAL Engine      |       |   Autonomous Dev Daemon    |                                      |
|   |   - data/frontierpilot.db|<----->|   - 30-min Cycle Watchdog  |                                      |
|   |   - Optimistic Locking   |       |   - Single-Instance Lock   |                                      |
|   |   - Idempotent Outbox    |       |   - Playwright UX Audits   |                                      |
|   +-------------+------------+       +----------------------------+                                      |
+-----------------+----------------------------------------------------------------------------------------+
                  |
                  v (Bi-Directional Staged Reconciler)
+-----------------+----------------------------------------------------------------------------------------+
|                                              EXTERNAL INTEGRATIONS                                       |
|  • LinkedIn REST API / Publora API (Publishing)     • Notion Databases (Career Radar Staging)            |
|  • Apify Scraper Layer (Cookie-Free Reading)        • Google Sheets v4 & Drive (Dossier & Exports)       |
|  • Slack Webhooks & Events API                      • Ngrok Secure Ephemeral / Static Reverse Proxy      |
+----------------------------------------------------------------------------------------------------------+
```

---

## 2. Layer-by-Layer Architectural Decomposition

### 2.1 Presentation & Client Layer (PWA)
- **Host**: Served by Flask at `/`, `/frontierpilot`, `/gethired`, `/dossier`.
- **Framework**: Semantic HTML5, Bootstrap 5.3, Bootstrap Icons, Chart.js, Vanilla ES6+ async modules.
- **Service Worker (`docs/sw.js` / `/sw.js`)**:
  - `Network-First` for all HTML navigations and state-changing APIs.
  - `Cache-First` for immutable vendor assets (Bootstrap, Popper, Chart.js, JSZip).
  - Versioned cache identifier (`CACHE_NAME = 'studio-cache-v9'`).
- **Ergonomics**: Responsive across 320px to 1440px+ viewports with zero horizontal overflow; off-canvas mobile drawer and synchronized bottom navigation bar.

### 2.2 Security & Authentication Perimeter
- **Rotated Master PIN Gatekeeper**: Passcode `frontier-orbitron-2026` evaluated via constant-time `secrets.compare_digest`.
- **Progressive Rate Limiting & Lockout**: 5 failed PIN attempts per remote IP locks out the endpoint for 300 seconds (HTTP 429).
- **Session Protection**: `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`, 12-hour lifetime.
- **Slack Signature Verification**: All requests to `/slack/interactions` and `/slack/events` are cryptographically verified using HMAC-SHA256 (`v0=...`) with a strict 300-second timestamp freshness window.

### 2.3 Application & Orchestration Layer (Flask Port 5050)
- Single-process Python WSGI server configured with automatic reload in development and thread isolation for webhook dispatches.
- 82 registered endpoints spanning draft lifecycle, career opportunities, Vaibhav Sisinty growth engines, multi-cloud sync, and real-time Slack interactions.

### 2.4 Generative AI Engine & Fallback Cascade
- **Primary Model**: `gemini-4-hydrogen` (temperature 0.7 for creative posts, 0.25-0.3 for structured JSON extraction).
- **Secondary Fallback**: `gemini-3.5-flash-lite` automatically engaged upon HTTP 429 quota exhaustion or socket read timeouts (>8s).
- **Circuit Breaker**: Models exceeding quota enter a 180-second cooldown state to prevent cascade latency spikes.
- **Voice Scrubber**: Purges AI slop tokens while preserving technical engineering terminology (e.g., "evaluation harness").

### 2.5 Data Persistence & Transactional Boundaries
- **Primary Source of Truth**: SQLite database with Write-Ahead Logging (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`).
- **Tables**: `drafts`, `opportunities`, `approval_events`, `outbox_jobs`.
- **Optimistic Concurrency**: Row-level updates assert `version = version + 1`.
- **Mirroring**: Automatically mirrors state to `testing/drafts_queue.json` and `testing/opportunities_tracker.json` to guarantee zero breaking changes for static site builders.

### 2.6 Autonomous Background Supervision
- **Engine**: `scripts/autonomous_dev_daemon.py` executing on a 30-minute interval.
- **Process Guard**: Inode lock on `/tmp/frontierpilot-daemon.lock` using `fcntl.flock(LOCK_EX | LOCK_NB)` preventing concurrent overlap.
- **Resource Hygiene**: Headless Playwright browser and context lifecycles wrapped in strict `try ... finally` blocks.
