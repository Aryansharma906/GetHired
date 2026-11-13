# 🚀 LinkedIn Autonomous Thought-Leadership Engine
## Master Documentation & Architecture Manual

**Project Maintainer & Author:** [Aryan Sharma](https://www.linkedin.com/in/aryan-sharma-engineer) (Senior Software Engineer & AI Systems Architect)  
**LinkedIn Platform Channel:** `linkedin-b3JjHLaMii`  
**System Designation:** Autonomous LinkedIn Thought-Leadership & Publishing Engine (v1.0.0)  
**Operational Status:** 🟢 **Active & Live in Production**  

---

## 📌 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Complete System Topology](#2-complete-system-topology)
3. [Documentation Index](#3-documentation-index)
4. [Quick Start & Operations Runbook](#4-quick-start--operations-runbook)
5. [Core Architectural Subsystems](#5-core-architectural-subsystems)
6. [The Tri-Voice Persona & 2026 Feed Rules](#6-the-tri-voice-persona--2026-feed-rules)
7. [Live Production Ledger & Verified URNs](#7-live-production-ledger--verified-urns)
8. [Autonomous Operator Mandate](#8-autonomous-operator-mandate)

---

## 1. Executive Summary

This repository houses an **end-to-end autonomous LinkedIn growth and thought-leadership engine**. It is specifically engineered to resolve the classic creator trade-off between **high shipping velocity** and **human editorial taste**:

- **Heavy Lifting is 100% Automated**: Topic discovery, algorithm-compliant drafting, AI buzzword auditing, persistent deduplication queuing, cloud scheduling, capacity auto-promotion, and real-time telemetry run autonomously under Antigravity.
- **The Human Taste Gate**: The human author (Aryan Sharma) never writes boilerplate, formats line breaks, or copies into third-party tools. Aryan only reviews candidate drafts and gives editorial sign-off via **interactive Slack cards** or a **mobile Approval Studio**.
- **Frontier Quality Standard**: Drafting operates at **Claude 3.7 / Fable 5.1-caliber reasoning**, synthesizing:
  1. *Aryan Sharma*: Concrete distributed systems depth, latency budgets, KV cache mechanics, database lock contention, and production post-mortems.
  2. *Vaibhav Sisinty*: High-tension pattern-interrupt hooks before the "see more" cutoff, 1–2 sentence scannable lines, and structural narrative anchors.
  3. *Raj Shamani*: Raw, behind-the-scenes founder economics, P&L teardowns, consumer behavior, and street-smart business truth.

---

## 2. Complete System Topology

```
 [ 1. Triggers & Sparks ]
    ├── Slack #sparks Voice Notes & Prompts
    ├── iPhone 1-Tap Action Button Shortcut
    ├── Mobile Web Studio (/api/drafts/generate)
    └── Autonomous Peak-Hour Scheduler
           │
           ▼
 [ 2. Frontier AI Content Core ]
    ├── Multi-Model Failover (gemini-flash-latest ➔ 3.5 ➔ 3.1-lite)
    ├── Claude Fable 5.1 Cognitive Depth & Tri-Voice Synthesis
    └── 2026 Feed Auditor (0 banned buzzwords, max 1 em-dash, 1.2k-1.8k chars)
           │
           ▼
 [ 3. Deduplication & Persistent Queue ]
    ├── 25-Word Semantic Prefix Hash Guard (Prevents duplicate posts)
    └── Thread-Safe State Database (testing/drafts_queue.json)
           │
           ▼
 [ 4. Human Taste Review Gate (High Priority Only) ]
    ├── Interactive Block Kit Slack Cards ([Approve & Schedule] / [Reject])
    └── Mobile Approval Studio (Port 5050 via secure tunnel)
           │
      [ Approved ]
           ▼
 [ 5. Cloud Publishing & Scheduling Layer ]
    ├── Publora API Integration (Channel: linkedin-b3JjHLaMii)
    └── Autonomous Capacity Manager (Auto-promotes queued drafts into open cloud slots)
           │
           ▼
 [ 6. Production LinkedIn Feed & Telemetry ]
    ├── Live Post Published on LinkedIn (Aryan Sharma Profile)
    └── Instant Real-Time Alert to Slack (Clickable LinkedIn Post URL)
```

---

## 3. Documentation Index

For deep dives into specific subsystems, see the dedicated guides in this `docs/` folder:

| Document | Description |
| :--- | :--- |
| [**`docs/pipeline_architecture.md`**](pipeline_architecture.md) | In-depth breakdown of the 6 pipeline stages, API contracts, and failure handling. |
| [**`docs/codebase_reference.md`**](codebase_reference.md) | File-by-file technical reference for `lib/`, `studio/`, `skills/`, `scripts/`, and `references/`. |
| [**`docs/operations_and_autonomy.md`**](operations_and_autonomy.md) | Startup commands, shutdown scripts, Slack triggers, and the Autonomous Operator Mandate. |
| [**`docs/production_ledger.md`**](production_ledger.md) | Live post archive with verified LinkedIn Share URNs, scheduled slots, and queue history. |

---

## 4. Quick Start & Operations Runbook

### A. Launching the Platform
To launch the Approval Studio, establish the secure tunnel, sync `.env`, and dispatch the live mobile link to your Slack:
```bash
./scripts/start_studio.sh
```

### B. Stopping the Platform
```bash
./scripts/stop_studio.sh
```

### C. Drafting a Post via CLI
```bash
# Draft a specific topic and send approval card to Slack
python3 scripts/run_slack_pipeline.py --topic "Why small AI teams beat 50-person agencies"

# Auto-rotate from the founder topic bank
python3 scripts/run_slack_pipeline.py --auto-generate
```

### D. Running Verification & Health Checks
```bash
# Run all 107 automated unit tests
python3 -m unittest discover -s tests

# Sync Codex package mirror
python3 scripts/sync_codex_marketplace.py
```

---

## 5. Core Architectural Subsystems

1. **AI Content Engine (`lib/gemini_generator.py`)**:
   - Executes multi-model failover across `gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-3.1-flash-lite`, and `gemini-3.5-flash`.
   - Incorporates Claude Fable 5.1 analytical depth, organic sentence cadence, and the Tri-Voice synthesis.
2. **Write & Cloud Scheduling (`lib/publora_client.py`)**:
   - Manages LinkedIn posts, comments, replies, and reactions via Publora API.
   - Monitors the 3-slot cloud scheduling capacity, auto-promoting queued posts as earlier slots publish.
3. **State & Deduplication (`lib/drafts_store.py`)**:
   - Thread-safe persistent JSON database in `testing/drafts_queue.json`.
   - Normalizes opening 25-word strings to mathematically prevent duplicate content across past, present, and future queues.
4. **Slack Approval Hub (`lib/slack_approver.py`)**:
   - Dispatches rich Block Kit approval cards with interactive `[Approve & Schedule]` and `[Reject]` actions.
   - Fires instant notifications the exact second a post goes live with clickable LinkedIn URLs.
5. **Mobile Approval Studio (`studio/app.py` & `studio/templates/index.html`)**:
   - Responsive web application running on port 5050 and exposed via secure tunnel.
   - Features KPI counters, tabbed status filtering, a Gemini Content Studio prompt creator, and 2026 compliance audits.

---

## 6. The Tri-Voice Persona & 2026 Feed Rules

Every generated post adheres strictly to 2026 feed distribution algorithms:
- **0 Banned Buzzwords**: Never uses *leverage, utilize, facilitate, streamline, robust, seamless, delve, navigate, unlock, harness, foster, cultivate, fundamentally, essentially, ultimately, realm, tapestry, landscape, ecosystem, paradigm, game-changer, deep dive, in today's fast-paced world*.
- **Em-Dashes**: Maximum 1 in the entire post.
- **Length**: Optimal range is **1,200 to 1,800 characters**.
- **Formatting**: Short, scannable 1–2 sentence paragraphs with generous white space for mobile readers.
- **Hooks**: First 2–3 lines must create an irresistible pattern-interrupt curiosity gap before the *"see more"* cutoff.

---

## 7. Live Production Ledger & Verified URNs

To date, the system has successfully published the following live assets on LinkedIn:

| Asset Type | Status | LinkedIn Share URN / ID | Topic |
| :--- | :---: | :--- | :--- |
| **Live Post** | 🚀 **Live** | `urn:li:share:7507061531122266113` | *The 3 Pillars of AI Velocity: Eval Harnesses, Taste Gates, and 5x Shipping* |
| **Live Post** | 🚀 **Live** | `urn:li:share:7507337030243110912` | *Why synthetic benchmarks are misleading AI engineering teams (94% MMLU Vanity Metric)* |
| **Live Post** | 🚀 **Live** | `urn:li:share:7507337283558195200` | *The Illusion of Privacy in the AI Digital Era (Latent Space & Vector Inversion)* |
| **Live Post** | 🚀 **Live** | `urn:li:share:7507423486806646784` | *The Token Unit-Economics Trap in AI SaaS (Sunday Peak Window)* |
| **Live Post** | 🚀 **Live** | `urn:li:share:7507649864638476289` | *The Vibe-Coding Hangover: Scaling Cursor Prototypes to 5,000 Users (Monday Morning Peak)* |
| **Viral Comment** | 🚀 **Live** | `id: 7507050449246633984` | *Technical breakdown under Vaibhav Sisinty's weekly AI recap thread* |

---

## 8. Autonomous Operator Mandate

Per the official author directive:
- **Antigravity Operates Autonomously**: Background scripts, test suites, terminal commands, package syncing (`sync_codex_marketplace.py`), queue checks, slot capacity promotions, and API verifications run with zero user interruption.
- **Mandatory Slack Reporting**: Every single automated milestone—post promotions, schedule triggers, live publications, and system wakeups—reports directly to Aryan's Slack channel.
- **Human Taste Gate**: The human author retains exclusive editorial authority, approving or rejecting candidate drafts with a single tap on mobile Slack.
