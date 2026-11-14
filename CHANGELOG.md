# Changelog — FrontierPilot 2.0 & LinkedIn Skills

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] — 2026-11-14

### 🚀 Architecture & Persistence Overhaul
- **SQLite WAL Relational Database Engine (`lib/database.py`)**: Migrated persistence from raw JSON files to SQLite operating in Write-Ahead Logging (`WAL`) mode with `busy_timeout=5000` (`FP-001`).
- **Optimistic Concurrency Control (OCC)**: Added row-level versioning (`version = version + 1`) to eliminate lost updates from concurrent web requests (`FP-002`).
- **Atomic JSON Mirror Synchronization**: Added real-time atomic JSON dumping to `testing/drafts_queue.json` and `testing/opportunities_tracker.json` ensuring 100% backward compatibility for legacy CLI tools (`FP-003`).
- **Zero-Downtime Data Migration**: Migrated all 55 existing drafts and 27 tracked opportunities with zero data loss.

### 🔒 Security & Access Hardening
- **Master PIN Invalidation & Rotation (`FP-004`)**: Invalidated leaked credential `frontier2026`; rotated default to `frontier-orbitron-2026` via environment variable `FRONTIERPILOT_PIN`.
- **Constant-Time PIN Verification (`FP-005`)**: Replaced equality comparison with `secrets.compare_digest()` to eliminate side-channel timing attacks.
- **Progressive IP Rate-Limiting (`FP-006`)**: Added brute-force lockout: 5 failed PIN attempts locks client IP address for 300 seconds (HTTP 429).
- **Slack HMAC-SHA256 Request Verification (`FP-007`)**: Implemented `verify_slack_request()` checking `X-Slack-Signature` and enforcing 300-second timestamp freshness window (`X-Slack-Request-Timestamp`).
- **Approval Idempotency Table (`FP-008`)**: Created `approval_events` table tracking unique trigger and message timestamps to eliminate duplicate post publishing from double clicks or replayed webhooks.

### 🧠 Gemini AI Systems & Voice Compliance
- **Next-Gen Gemini Cascade (`FP-009`)**: Upgraded deprecated `gemini-flash-latest` model references to multi-tiered cascade: `gemini-4-hydrogen` $\to$ `gemini-3.5-flash-lite` $\to$ `gemini-4-carbon`.
- **API Circuit Breaker (`FP-010`)**: Implemented 180-second automatic cooldown on quota exhaustion (HTTP 429 / 503) with deterministic offline fallback generation.
- **Context-Aware Lexical Scrubber (`FP-011`)**: Enhanced `_scrub_voice_blacklist()` to safely convert software terms (e.g. `test harness` $\to$ `test suite`) while eradicating corporate buzzwords (*leverage, utilize, facilitate, streamline, robust, seamless, delve, navigate, unlock, harness, foster, cultivate, fundamentally, essentially, ultimately, landscape, ecosystem, paradigm, game-changer, deep dive*).

### 🖥️ Frontend & Accessibility Engineering
- **WCAG 2.2 AA Form Annotations (`FP-012`)**: Annotated all 38 previously unlabeled form inputs, selects, and textareas in `studio/templates/frontierpilot.html` with context-rich `aria-label` attributes.
- **High-Contrast Focus Rings**: Standardized `:focus-visible` styling (`2px solid #3b82f6` with `2px offset`).
- **Modal Lock Elimination**: Removed inline `style="display: none;"` from Bootstrap modal containers to prevent viewport freezing.
- **Responsive Geometry**: Validated zero horizontal scroll overflow across 7 standard viewport sizes (1440px down to 320px).

### ⚙️ DevOps & CI/CD Pipelines
- **Automated Security Guard (`.github/workflows/security-guard.yml`) (`FP-013`)**: Populated empty CI workflow with automated secret scanning (`scripts/check_no_secrets.py`), skill frontmatter checks (`scripts/check_frontmatter.py`), 12-skill count validation, unit test execution, and marketplace sync validation.
- **Deterministic Cloud Sync Hashing (`lib/frontierpilot_integrator.py`) (`FP-014`)**: Added SHA-256 state hashing to eliminate redundant writes to Google Sheets, Drive, and Notion.
- **Single-Instance Daemon Guard (`scripts/autonomous_dev_daemon.py`) (`FP-015`)**: Added kernel `fcntl.flock` file locking on `/tmp/frontierpilot-daemon.lock` to prevent overlapping background daemon executions.

---

## [2.0.0] — 2026-11-10
- Initial release of FrontierPilot 2.0 and LinkedIn Creator Studio.
- 10-module single-page PWA dashboard.
- 12 canonical LinkedIn marketing agent skills.
- Integration with Publora publishing API and Apify scraper.
