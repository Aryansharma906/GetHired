# Gemini & Antigravity Conventions — linkedin-skills

This file is the configuration and operations manual for **Google Antigravity** and **Gemini** maintaining this repository.

---

## 1. System Architecture

This repository contains:
- **12 LinkedIn Marketing Skills** (`skills/*/SKILL.md`): Post Writer, Comment Drafter, Reply Handler, Post Audit, Humanizer, Hook Extractor, Content Planner, Engagement Monitor, Profile Optimizer, Employee Advocacy, Repurposer, and Interviewer.
- **Gemini Content Engine** (`lib/gemini_generator.py`): Leverages Google Gemini models to craft authentic, algorithm-compliant founder posts using 2026 hook formulas.
- **Slack Approval Hub** (`lib/slack_approver.py`, `scripts/run_slack_pipeline.py`): Posts rich Block Kit cards to a Slack channel with interactive `[Approve & Schedule]` and `[Reject]` actions.
- **Draft Queue & Storage** (`lib/drafts_store.py`): Persistent state in `testing/drafts_queue.json`.
- **Publishing & Reading Layer**: Publora (`lib/publora_client.py`) for publishing/scheduling; Apify (`lib/apify_client.py`) for reading without cookies.

---

## 2. Antigravity & Gemini Workflows

### Daily Automated Post Generation & Slack Dispatch
To trigger an automated LinkedIn draft dispatch to Slack, Antigravity or the user can run:
```bash
# Generate using Google Gemini and dispatch to Slack
python3 scripts/run_slack_pipeline.py --topic "Why small AI teams beat 50-person agencies"

# Auto-rotate from the founder topic bank
python3 scripts/run_slack_pipeline.py --auto-generate

# Dry-run preview without sending to Slack
python3 scripts/run_slack_pipeline.py --dry-run
```

### Recurring Antigravity Schedule (`/schedule`)
You can automate the pipeline on a recurring schedule directly within Antigravity:
```
/schedule CronExpression="0 9 * * 1-5" Prompt="Run python3 scripts/run_slack_pipeline.py --auto-generate to draft today's post and send it to Slack for approval."
```

### Slack Button Interaction Listener
To process live button clicks (`Approve & Schedule` / `Reject`) from Slack:
```bash
python3 scripts/slack_listener.py --port 5050
```

### Dossier Career Radar & Slack Job Approvals
To trigger career radar updates, job evaluations, and send interactive approval cards to Slack:
```bash
# Check connectivity across Google Gemini, Sheets, Drive, Gmail, Notion, Slack
python3 scripts/sync_dossier.py --status

# Dispatch top priority job approval card to Slack for 1-tap approval
python3 scripts/sync_dossier.py --dispatch-jobs

# Send executive Career Radar digest to Slack
python3 scripts/sync_dossier.py --digest

# Run full unified sync (scoring, sheets, drive, gmail, notion) + Slack cards
python3 scripts/sync_dossier.py --all
```

---

## 3. Voice & 2026 Feed Standards

Whenever Gemini or Antigravity generates or modifies LinkedIn copy:
1. **Em dashes (`—`)**: Maximum 1 per 100 words (0-2 max per post).
2. **Vocabulary Blacklist**: Never use *leverage, utilize, facilitate, streamline, robust, seamless, delve, navigate, unlock, harness, foster, cultivate, fundamentally, essentially, ultimately, landscape, ecosystem, paradigm, game-changer, deep dive, in today's fast-paced world*.
3. **Length**: Optimal sweet spot is **900–1,300 characters** (LinkedIn hard limit is 3,000 characters).
4. **Formatting**: 1–2 sentence paragraphs with white space for mobile scannability.
5. **Hook Formulas**: First 2–3 lines must follow one of the 20 canonical formulas (`references/hook-formulas.md`).

---

## 4. Environment Variables (`.env`)

```bash
# Gemini API Key (for dynamic AI generation)
GEMINI_API_KEY=AIzaSy...

# Slack Incoming Webhook (for approval cards)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...

# Publora (for automatic publishing on approval)
PUBLORA_API_KEY=sk_...
LINKEDIN_PLATFORM_ID=linkedin-...

# Apify (for scraping & thread reading)
APIFY_TOKEN=apify_api_...
```

---

## 5. Testing & Validation

Before pushing any changes:
```bash
# Run unit tests (including Slack integration)
python3 -m unittest discover -s tests

# Verify Slack setup
python3 scripts/test_slack_setup.py

# Sync Codex package mirror
python3 scripts/sync_codex_marketplace.py
```

---

## 6. Antigravity Autonomy vs. High-Priority Human Review Gate

**Author Mandate (Aryan Sharma)**: Antigravity is officially granted autonomous operational authority under Aryan's command. Repetitive technical tasks and background automations are delegated to Antigravity, while editorial taste remains with Aryan. Every automated action must be reported to Slack.

To maximize velocity and eliminate cognitive load:
- **Antigravity Fully Autonomous (Zero Friction / No Interruption)**:
  - Automate all repetitive tasks without prompting: running test suites, background scripts, terminal executions, package synchronizations (`scripts/sync_codex_marketplace.py`), queue checks, slot capacity promotions, and API verifications.
  - Automatically promote locally queued posts into Publora as cloud capacity frees up.
  - Automatically heal or restart disconnected tunnels and sync live URLs.
  - Do not ask for confirmation on routine technical operations or local plumbing.
- **Mandatory Slack Reporting (100% Real-Time Visibility)**:
  - **Every automated action must report to Slack**: Post promotions, schedule changes, live publications, daily queue digests, and system restarts must fire clean Block Kit cards directly to Aryan's Slack channel.
  - Aryan controls the system from mobile Slack with zero requirement to open a terminal.
- **Human Taste Gate (High-Priority Only)**:
  - The user only intervenes for:
    1. **Content Review & Approval**: Editorial sign-off on new LinkedIn posts and high-leverage comments (via interactive Slack cards or mobile Studio).
    2. **Irreversible / Destructive Decisions**: High-stakes strategic operations that cannot be undone.
  - Maintain the separation: **Antigravity handles automated execution; the human controls editorial taste.**

---

## 7. Direct LinkedIn REST API & Protocol Conventions

- **Author URN Format**: `POST /v2/ugcPosts` requires `author: "urn:li:member:<numeric_id>"` or `"urn:li:company:<id>"`.
- **OAuth Product & Scopes**:
  - The "Share on LinkedIn" developer product authorizes `w_member_social`.
  - Adding "Sign In with LinkedIn using OpenID Connect" provides `openid`, allowing automatic member ID discovery via `/v2/userinfo`.
  - Without OpenID, set `LINKEDIN_AUTHOR_URN=urn:li:member:<numeric_id>` in `testing/linkedin_credentials.env`.
- **Local Hostname Resolution**:
  - macOS Safari/WebKit does not resolve `0.0.0.0` as a valid hostname. Always expose and bind local dashboards to `http://127.0.0.1:5050` or `http://localhost:5050`.
- **Publishing Hierarchy**:
  - Direct LinkedIn REST API is primary for immediate, latency-free publishing without third-party queue limits.
  - Publora remains the multi-platform scheduling fallback.



