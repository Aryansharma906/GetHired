# FrontierPilot 2.0 — System Component Map

This document establishes the physical file topology, module ownership, component dependencies, and architectural boundaries across the repository.

---

## 1. Physical File Topology & Component Ownership

```
linkedin-skills/
│
├── studio/                               # [Presentation & Routing]
│   ├── app.py                            # Flask application entry point (Port 5050), API routes, Slack listener
│   └── templates/
│       ├── frontierpilot.html             # 10-tab cosmic cockpit PWA template (5,400+ LOC)
│       └── login.html                     # Rotated Master PIN gatekeeper & Slack push access
│
├── lib/                                  # [Core Domain Services]
│   ├── database.py                       # SQLite WAL ACID persistence engine & mirror syncer
│   ├── drafts_store.py                   # High-level drafts queue abstraction layer
│   ├── gemini_generator.py               # Google Gemini content engine, circuit breaker, 2026 voice rules
│   ├── vaibhav_growth_engine.py          # 5-in-1 Vaibhav Sisinty Growth Studio algorithms
│   ├── job_hunter_engine.py              # ATS keyword optimizer, match scorer, application packager
│   ├── frontierpilot_integrator.py       # Multi-cloud reconciler (Notion, Wix, Sheets, Drive, Gmail)
│   ├── slack_approver.py                 # Slack Block Kit card builder & interactive button handler
│   ├── publora_client.py                 # Multi-platform write layer (LinkedIn direct REST & Publora)
│   ├── apify_client.py                   # Cookie-free read layer (Post, comment, engager scrapers)
│   ├── backend_selector.py               # Dynamic dispatch between official REST, Publora, and manual modes
│   └── _env.py                           # Secure environment variable loader
│
├── skills/                               # [12 Canonical Agent Skills - Bundle Invariant]
│   ├── linkedin-post-writer/             # Post drafting using 20 canonical hook formulas (F01-F20)
│   ├── linkedin-humanizer/               # Anti-slop rewriting & AI detection evasion suite
│   ├── linkedin-comment-drafter/         # Contextual thought leadership comments
│   ├── linkedin-reply-handler/           # Comment thread triage & lead conversion
│   ├── linkedin-post-audit/              # Pre-publish algorithm heuristics & readability checks
│   ├── linkedin-hook-extractor/          # Viral pattern extraction from founder feeds
│   ├── linkedin-content-planner/         # 30-day topical calendar structuring & founder pillar mapping
│   ├── linkedin-engagement-monitor/      # Follower velocity & engagement drop detection
│   ├── linkedin-profile-optimizer/       # Headline, About, and Featured section conversion audit
│   ├── linkedin-employee-advocacy/       # Team amplification & company culture distribution
│   ├── linkedin-repurposer/              # Multi-channel content repurposing
│   └── linkedin-interviewer/             # Voice extraction via structured founder Q&A
│
├── scripts/                              # [Operational & Automation Tooling]
│   ├── autonomous_dev_daemon.py          # 30-min background watchdog with single-instance lock
│   ├── start_studio.sh                   # Cockpit bootstrapper (Flask + Ngrok + Slack alert)
│   ├── redirect_3000_to_5050.py          # Legacy port forwarder
│   ├── sync_codex_marketplace.py         # Syncs .codex-marketplace/ mirror package
│   ├── build_studio_static.py            # Static PWA builder for GitHub Pages / Netlify (docs/)
│   ├── full_ux_audit_suite.js            # Automated Playwright 7-viewport responsive UX audit
│   └── audit_mobile_ux.js                # Headless mobile audit with memory leak protections
│
├── testing/                              # [Local Ephemeral State - Strictly Gitignored]
│   ├── frontierpilot.db                  # Authoritative SQLite database in WAL mode
│   ├── drafts_queue.json                 # Mirror of drafts table (55 posts)
│   ├── opportunities_tracker.json        # Mirror of opportunities table (27 roles)
│   └── autonomous_dev_ledger.json        # Persistent cycle log
│
└── tests/                                # [Automated Regression Test Suite - 139 Tests]
    ├── test_slack_integration.py         # Tests Block Kit generation & callback execution
    ├── test_frontierpilot_creator_studio.py # Tests Studio API routes, auth, and draft lifecycle
    ├── test_vaibhav_growth_engine.py     # Tests 5 Vaibhav tools with model cascade
    ├── test_job_hunter_engine.py         # Tests resume tailoring & match evaluation
    ├── test_frontierpilot_integrator.py  # Tests cloud sync data transformations
    ├── test_client_behaviour.py          # Tests HTTP client contracts & retries
    ├── test_response_shapes.py           # Validates payload schemas
    └── test_instruction_integrity.py     # Validates voice rules & blacklist integrity
```

---

## 2. Component Dependency Graph

```
[studio/app.py]
  │
  ├──> [lib/database.py] <───> [testing/frontierpilot.db (WAL)]
  │         │
  │         └──> [testing/drafts_queue.json] (Bi-Directional Mirror)
  │         └──> [testing/opportunities_tracker.json] (Bi-Directional Mirror)
  │
  ├──> [lib/gemini_generator.py] ──> [Google Generative Language API v1beta]
  │
  ├──> [lib/vaibhav_growth_engine.py] ──> [Google Generative Language API v1beta]
  │
  ├──> [lib/job_hunter_engine.py] ──> [Google Generative Language API v1beta]
  │
  ├──> [lib/slack_approver.py] ──> [Slack Incoming Webhooks / API]
  │
  ├──> [lib/frontierpilot_integrator.py]
  │         ├──> [Notion API]
  │         ├──> [Wix CMS API]
  │         ├──> [Google Sheets v4 API]
  │         └──> [Google Drive API]
  │
  └──> [lib/publora_client.py] ──> [Publora REST API / Official LinkedIn API]
```
