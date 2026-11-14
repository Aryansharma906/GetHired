# FrontierPilot 2.0 — Data Flow Map

This document tracks data models, serialization schemas, state transitions, and bi-directional flows across the system.

---

## 1. Core Data Entities & Schema Models

### 1.1 Draft Model (`drafts` table)
```sql
CREATE TABLE drafts (
    id TEXT PRIMARY KEY,                       -- e.g. "post_20261114_080000_a1b2c3"
    topic TEXT,                                -- Topical focus or prompt
    hook_formula TEXT,                         -- F01-F20 canonical formula
    angle TEXT,                                -- Analytical angle / persona
    content TEXT,                              -- Full generated copy (scrubbed)
    char_count INTEGER,                        -- Character length (900-1,300 sweetspot)
    status TEXT NOT NULL,                      -- pending_approval, approved, scheduled, published, rejected
    version INTEGER NOT NULL DEFAULT 1,        -- Optimistic locking version
    created_at TEXT NOT NULL,                  -- ISO UTC timestamp
    updated_at TEXT NOT NULL,                  -- ISO UTC timestamp
    scheduled_time TEXT,                       -- Target publication timestamp
    approved_at TEXT,                          -- Approval timestamp
    approved_by TEXT,                          -- Reviewer name (Aryan Sharma)
    approved_content_version INTEGER,          -- Version matching exact approved text
    published_at TEXT,                         -- Confirmation timestamp from LinkedIn
    publora_id TEXT,                           -- Remote platform post URN
    idempotency_key TEXT UNIQUE                -- Prevent duplicate publishing
);
```

### 1.2 Opportunity Model (`opportunities` table)
```sql
CREATE TABLE opportunities (
    id TEXT PRIMARY KEY,                       -- e.g. "opp_anthropic_eval"
    organization TEXT,                         -- Company / Lab name
    title TEXT,                                -- Role title
    category TEXT,                             -- engineering, research, evaluation, systems
    status TEXT NOT NULL DEFAULT 'radar',      -- radar, tailoring, submitted, interviewing, offer, archived
    deadline TEXT,                             -- Application deadline
    comp_stipend TEXT,                         -- Compensation or stipend range
    match_score INTEGER,                       -- 0-100 fit score from Gemini
    match_reason TEXT,                         -- Tactical rationale
    target_url TEXT,                           -- Career portal link
    notes TEXT,                                -- Candidate notes
    action_plan TEXT,                          -- 30-day proof-of-work plan
    version INTEGER NOT NULL DEFAULT 1,        -- Optimistic locking version
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

## 2. Key Data Pipelines

### Pipeline 1: LinkedIn Content Creation & Human Approval
```
[User / Cron Trigger]
        │
        ▼
[gemini-4-hydrogen] ──(429/Timeout)──> [gemini-3.5-flash-lite]
        │
        ▼ (Post text)
[_scrub_voice_blacklist] (Purges slop while preserving technical terms)
        │
        ▼
[SQLite WAL `drafts` table] ──(INSERT status='pending_approval')
        │
        ├─────────────────────────────────┐
        ▼                                 ▼
[testing/drafts_queue.json]      [Slack Incoming Webhook]
(Bi-directional Mirror)         (Block Kit Card with Approve / Reject)
                                          │
                                          ▼
                                 [Aryan Sharma Clicks]
                                          │
                                          ▼
                                 [/slack/interactions]
                                 (HMAC Signature Verified)
                                          │
                                          ▼
                                 [db_transition_approval]
                                 - status='scheduled'
                                 - records event_id in approval_events
                                          │
                                          ▼
                                 [Publora / Direct REST Worker]
                                 - Dispatches to LinkedIn
                                 - Updates status='published'
```

### Pipeline 2: Multi-Cloud Staging & Reconciliation
```
[FrontierPilot Cockpit / CLI]
        │
        ▼
[FrontierPilotIntegrator]
        ├──> Notion API (Reads / Writes Opportunities Database)
        ├──> Google Sheets v4 (Staged CSV & Live REST Spreadsheet sync)
        ├──> Google Drive API (Exports Zipped Dossiers & Tailored Resumes)
        └──> Wix CMS API (Staging Collection Sync)
        │
        ▼
[Deterministic Payload Hash (SHA-256)]
(Prevents redundant writes when data is identical)
```
