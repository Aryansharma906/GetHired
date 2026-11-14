# FrontierPilot 2.0 Implementation Plan: LinkedIn Creator Studio Integration

## Status: COMPLETED & VERIFIED
**Branch**: main
**Owner**: Principal Engineer (Antigravity & Gemini Content Engine)

---

## 1. Objectives & Architectural Decisions

Following the product interview (/grill-me):
1. **Side-by-Side Dual-Mode Architecture**: Standalone Studio remains accessible at `/`, while FrontierPilot (`/frontierpilot`) gains a native, first-class **LinkedIn Creator Studio** section (`data-tab="creator-studio"`) adopting FrontierPilot's exact design system, CSS variables, typography, and responsive layout.
2. **Broken Link Remediation**:
   - Fixed all broken links (`./index.html` which threw 404 in web runtime).
   - In `studio/app.py`, mapped `/index.html` to cleanly redirect (HTTP 302) to `/`.
   - Updated FrontierPilot sidebar with dual entries:
     - `LinkedIn Creator Hub` (`data-tab="creator-studio"`): Activates the native in-app studio.
     - `Standalone Studio ↗` (`href="/" target="_blank"`): Opens standalone studio in a new tab.
   - Updated top header and jump banner action buttons to switch tabs internally or launch standalone.
3. **Split Master-Detail Layout in FrontierPilot**:
   - **Left Pane (Drafts Queue & Status)**: Real-time KPI counters (Pending, Scheduled, Published, Total), filter pills (All, Pending, Scheduled, Published, Rejected), search input, rich cards with hook formula badge, angle badge, character/word counters, Slack card status, and 1-click [Approve & Schedule], [Instant Publish], [Edit in Composer], [Reject], [Delete], [Copy].
   - **Right Pane (Live Composer & AI Studio)**:
     - Repurpose from FrontierPilot selector (Target Applications & Master Profile projects).
     - 2026 Hook formula selector & Topic input.
     - Real-time 2026 LinkedIn Compliance Meter:
       - Em-dash density meter (max 1 per 100 words).
       - Vocabulary anti-slop scanner (flags blacklisted AI words).
       - Sweet spot length gauge (900-1300 chars optimal; 3000 max).
     - AI Media & Document preview attachment pane.
     - 1-Click [✨ Generate with Gemini], [💾 Save Draft], [📱 Send to Slack for Approval], [🚀 Instant Publish].
4. **Deep Career-to-Content Pipeline**:
   - Added quick action button `"🚀 Draft LinkedIn Post"` directly on Application cards (`renderAllRoles`) and Master Profile research milestones to prefill and switch to the Creator Studio.
5. **Server-Only Persistence**:
   - All draft mutations execute directly against `/api/drafts` backend endpoints.
   - Added `/api/drafts/<draft_id>` (PUT/POST update), `/api/drafts/create`, and `/api/drafts/repurpose` endpoints.

---

## 2. Implementation Milestones

- [x] Phase 1: Architecture & Design Decisions finalized with user via /grill-me.
- [x] Phase 2: Backend API Enhancements (`studio/app.py` & `lib/drafts_store.py`):
  - Added `/index.html` redirect route (verified HTTP 302 -> `/`).
  - Added `/api/drafts/create` and `/api/drafts/<draft_id>` update endpoints.
  - Added `/api/drafts/repurpose` endpoint for Gemini-powered career-to-content generation.
  - Added `_scrub_voice_blacklist` in `lib/gemini_generator.py` for automated 2026 voice compliance.
- [x] Phase 3: Frontend FrontierPilot Template Updates (`studio/templates/frontierpilot.html`):
  - Sidebar dual-navigation items (`LinkedIn Creator Hub` + `Standalone Studio ↗`).
  - Fixed header and banner buttons.
  - Implemented master-detail `#tabCreatorStudio` viewport.
  - Real-time 2026 compliance meter JavaScript engine.
  - "🚀 Draft LinkedIn Post" buttons on Application and Master Profile cards.
- [x] Phase 4: Static PWA compilation (`scripts/build_studio_static.py` -> `docs/frontierpilot.html`, `docs/index.html`, `docs/sw.js` bumped to v3).
- [x] Phase 5: Automated Testing & Verification:
  - Unit tests in `tests/test_frontierpilot_creator_studio.py` (7/7 PASS).
  - Full repo test suite `python3 -m unittest discover -s tests` (131/131 PASS).
  - Codex package sync via `scripts/sync_codex_marketplace.py`.
  - Live server verification on `http://127.0.0.1:5050/index.html` (302) and `http://127.0.0.1:5050/frontierpilot` (200).
  - REST Opportunity CRUD lifecycle verified (Create, Read, Update, Delete).
  - Global Command Palette (`Cmd+K` / `Ctrl+K`), WCAG 2.2 AA accessibility focus rings, and skip link verified.
