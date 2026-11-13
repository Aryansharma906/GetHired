# 🏗️ Pipeline Architecture & Subsystem Specification

This document details the internal mechanics, failure handling, and communication contracts across each stage of the LinkedIn automation engine.

---

## 1. Trigger & Spark Ingestion Layer

The system supports four distinct trigger vectors:

### A. Mobile Web Studio (`POST /api/drafts/generate`)
- **Endpoint**: Hosted on port 5050 and exposed via ngrok tunnel.
- **Payload**:
  ```json
  {
    "topic": "The Token Unit-Economics Trap",
    "style": "Aryan x Vaibhav Sisinty",
    "length": "long",
    "hook_formula": "F04 Time-Anchor Confession",
    "instructions": "Focus on context window bloat and quantized SLMs"
  }
  ```
- **Execution**: Validates inputs, calls `generate_post_with_gemini`, inserts the draft into `testing/drafts_queue.json`, and triggers `send_draft_to_slack`.

### B. Mobile iPhone Voice Shortcut (Action Button)
- Uses Apple Shortcuts to capture dictated speech.
- Sends an instant HTTP `POST` request to the active Studio URL.
- Bypasses the need to open any web browser or terminal.

### C. Terminal CLI Runner (`scripts/run_slack_pipeline.py`)
- For scheduled batch operations or on-demand local generation.
- Supports `--topic "..."`, `--file draft.txt`, `--auto-generate`, and `--dry-run`.

### D. Autonomous Weekly Batch Scheduler
- Can be configured via cron or Antigravity's `/schedule` to automatically draft the upcoming week's peak-hour drops and queue them for review.

---

## 2. Frontier AI Content Core (`lib/gemini_generator.py`)

### A. Multi-Model Failover Architecture
To eliminate HTTP 503 high-demand spikes and 404 endpoint deprecations, the engine cycles through candidate models:
1. `gemini-flash-latest` (Primary, ~2.5s response time)
2. `gemini-flash-lite-latest` (Secondary, ~1.3s response time)
3. `gemini-3.1-flash-lite` (Tertiary fallback)
4. `gemini-3.5-flash` (Final fallback)

Each request enforces a strict **15-second timeout**. If a model stalls or errors, the generator immediately promotes the payload to the next candidate model.

### B. Claude Fable 5.1 Cognitive Calibration
The generation prompt is anchored in frontier-grade reasoning principles:
- **Internal Mechanics First**: Unpacks why the status quo fails (e.g. latency budgets, memory bandwidth, vector inversion, cash burn).
- **Rhythmic Sentence Cadence**: Varies sentence length deliberately to create natural intellectual momentum.
- **Rhetorical Hygiene**: Permanently bans empty filler words (*"let's face it"*, *"the truth is"*, *"at the end of the day"*).

### C. Tri-Voice Synthesis Matrix
- **Aryan Sharma (40%)**: Hard technical receipts, database locks, telemetry leaks, p99 latency, vector database security, client-side SLM edge clusters.
- **Vaibhav Sisinty (35%)**: High-tension pattern-interrupt hooks before the "see more" cutoff, 1–2 sentence mobile-scannable paragraphs, bold contrasting realities.
- **Raj Shamani (25%)**: Raw business teardowns, founder P&L economics, behind-the-scenes reality, and street-smart analogies.

---

## 3. Persistent State & Deduplication Engine (`lib/drafts_store.py`)

- **Storage Backend**: `testing/drafts_queue.json` (thread-safe, gitignored).
- **Deduplication Sentinel**:
  ```python
  clean_content = content.strip()
  norm_content = " ".join(clean_content.split()[:25]).lower()
  for existing in drafts:
      existing_norm = " ".join(existing.get("content", "").split()[:25]).lower()
      if norm_content == existing_norm:
          return existing  # Blocks duplicate creation
  ```
- **State Machine**:
  - `pending_approval`: Draft created, waiting for Aryan's review.
  - `approved`: Marked approved by Aryan.
  - `scheduled`: Active in Publora cloud queue or queued for the next open slot.
  - `published`: Confirmed live on LinkedIn with a verified `postedId`.
  - `rejected`: Archived.

---

## 4. Cloud Publishing & Scheduling Layer (`lib/publora_client.py`)

- **Platform Connection**: Connected to Aryan's official LinkedIn profile via `LINKEDIN_PLATFORM_ID=linkedin-b3JjHLaMii`.
- **Publora Endpoints**:
  - `POST /create-post`: Accepts `content`, `platforms`, and optional `scheduledTime`.
  - `GET /get-post/<id>`: Queries real-time status and live `postedId` / `permalink`.
  - `PUT /update-post/<id>`: Patches content or timestamps.
  - `DELETE /delete-post/<id>`: Cancels scheduled posts before dispatch.
  - `POST /linkedin-comments`: Publishes top-level comments and nested replies.
- **Cloud Slot Capacity Management**:
  - Publora's Starter plan permits up to **3 concurrently active scheduled posts** in their cloud worker.
  - The engine tracks active cloud slots. Posts exceeding capacity stay in the local queue with their target timestamp and **autonomously promote into Publora** the second an earlier post publishes.

---

## 5. Telemetry & Slack Feedback Loop (`lib/slack_approver.py`)

- **Approval Dispatch**: Dispatches interactive Block Kit cards containing the post preview, character counts, 2026 checklist, and one-tap action buttons.
- **Live Publishing Alerts**: When a post is published, `send_published_notification` fires an immediate card to Slack with direct `[ 🔗 View Live on LinkedIn ]` buttons.
- **Studio URL Discovery**: Automatically resolves active ngrok URLs and sends announcement cards on startup.
