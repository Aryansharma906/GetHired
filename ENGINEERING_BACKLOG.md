# FrontierPilot 2.0 — Master Engineering Backlog

This document maintains prioritized findings, technical debt, and continuous self-improvement initiatives.

---

## Priority Classifications
- **P0 (Critical)**: Data loss, authentication bypass, credential exposure, duplicate/unauthorized publishing.
- **P1 (High)**: Core workflow unreliability, unhandled rate-limit cascades, cloud sync conflict silent overwrite, memory leaks.
- **P2 (Medium)**: UX friction, low-contrast text, touch target sizing, missing CI automation.
- **P3 (Low)**: Cosmetic polish, documentation refinement.

---

## 1. Master Findings Register

| ID | Category | Title | Severity | Status | Assigned Agent | Verification Criteria |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **FP-001** | Database | Shared JSON read-modify-write lost updates | P0 | **RESOLVED** | Agent 03 (Database) | Migrated to SQLite WAL with row-level versioning. |
| **FP-002** | Security | Disclosed plaintext Master PIN in architectural brief | P0 | **RESOLVED** | Agent 05 (Security) | Rotated PIN, added constant-time compare & 5-try lockout. |
| **FP-003** | Security | Slack interactive webhook lacked HMAC-SHA256 signature verification | P0 | **RESOLVED** | Agent 05 (Security) | Enforced `v0=...` signature & 300s replay window. |
| **FP-004** | State Machine | Post approval lacked finite state machine & duplicate publish guard | P0 | **RESOLVED** | Agent 01 (Backend) | Added `approval_events` idempotency table & status transitions. |
| **FP-005** | AI Systems | Deprecated `gemini-flash-latest` & unhandled 429 quota exhaustion | P1 | **RESOLVED** | Agent 09 (AI Systems) | Upgraded to `gemini-4-hydrogen` -> `3.5-flash-lite` cascade. |
| **FP-006** | AI Systems | Voice scrubber butchered technical terms (e.g. `test harness`) | P1 | **RESOLVED** | Agent 09 (AI Systems) | Purged blunt `harness` regex rule; preserved technical terms. |
| **FP-007** | DevOps | Autonomous daemon lacked single-instance lock (overlapping runs) | P1 | **RESOLVED** | Agent 04 (DevOps) | Added `fcntl.flock` on `/tmp/frontierpilot-daemon.lock`. |
| **FP-008** | QA / Frontend | Playwright headless browser contexts not cleanly closed in audit | P1 | **RESOLVED** | Agent 06 (QA) | Wrapped browser & context in `try ... finally` blocks. |
| **FP-009** | Cloud Sync | Multi-cloud sync lacked payload hashing (redundant updates) | P1 | **RESOLVED** | Agent 01 (Backend) | Implemented deterministic `compute_payload_hash` (SHA-256). |
| **FP-010** | Accessibility | 65 form inputs lacked accessible labels or aria-label attributes | P2 | **IN PROGRESS** | Agent 07 (Design/A11y) | Injected explicit `aria-label` tags into cockpit inputs. |
| **FP-011** | Accessibility | Missing visible `:focus-visible` outline for keyboard navigation | P2 | **RESOLVED** | Agent 07 (Design/A11y) | Injected global `#38bdf8` outline with 2px offset. |
| **FP-012** | Mobile UX | Interactive buttons < 44×44px on mobile viewports ($\le 768\text{px}$) | P2 | **RESOLVED** | Agent 07 (Design/A11y) | Injected `@media (max-width: 768px)` minimum height rules. |
| **FP-013** | CI/CD | `.github/workflows/security-guard.yml` was empty (0 bytes) | P2 | **OPEN** | Agent 04 (DevOps) | Populate workflow with automated secret & frontmatter checks. |
| **FP-014** | Architecture | Legacy Next.js app in `dossier/` unmaintained with Postgres dependency | P2 | **OPEN** | Agent 01 (Backend) | Retain port 3000 forwarder to unified cockpit on Port 5050. |
| **FP-015** | Design | Dashboard typography scale and badge alignment polish | P3 | **RESOLVED** | Agent 07 (Design) | Aligned cosmic glassmorphic border tokens and text contrast. |
