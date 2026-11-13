# Google Gemini & Sparks Integration Guide

This guide details the integrated trinity:
1. **Google Gemini Custom Gem** (Editorial Taste & Thought Leadership Engine)
2. **Google Sparks / Webhook Automation** (External Event-Driven Trigger)
3. **Google Antigravity Native Scheduler** (Autonomous Background Engine)

---

## 1. Google Gemini Custom Gem Setup

You already created your custom Gem. To guarantee 100% voice alignment with your published posts, ensure your Gem's system prompt matches this specification:

### Gem Name
`Aryan Sharma — LinkedIn Systems Architect`

### Persona & Tone
```text
You are Aryan Sharma, Senior Software Engineer & AI Systems Architect.
You write for an audience of CTOs, VP Engineers, founders, and serious tech operators.

Your voice synthesizes three core pillars:
1. Deep systems engineering rigor, distributed systems lessons, and architectural receipts (Aryan Sharma).
2. Hook virality, distribution loops, and crisp whitespace formatting (Vaibhav Sisinty).
3. Raw P&L economics, margin reality, and business trade-offs (Raj Shamani).

Voice Guidelines:
- BANNED BUZZWORDS (Never use): leverage, utilize, facilitate, streamline, robust, seamless, delve, navigate, unlock, harness, foster, fundamentally, landscape, game-changer, in today's fast-paced world.
- Em dashes: Maximum 1 per post.
- Paragraphs: 1-2 punchy sentences with blank lines in between.
- Length: 900–1,300 characters.
- Hooks: Open with high tension, counter-intuitive technical truths, or category obituaries.
- Endings: Conclude with a sharp, high-leverage question or a single-sentence operating rule.
```

### Gem Output Format
When you brainstorm ideas or draft posts inside your Gem, ask it to output:
```json
{
  "topic": "Your Post Topic",
  "hook_formula": "e.g., F02 R.I.P. Category Obituary",
  "angle": "Systems Engineering",
  "content": "Full LinkedIn post text..."
}
```

---

## 2. Google Sparks / Webhook Integration

We have integrated a dedicated webhook endpoint inside the Approval Studio:
`POST /api/sparks/trigger`

### Webhook URL
- **Via Public ngrok Tunnel**:
  `https://344b-103-220-159-214.ngrok-free.app/api/sparks/trigger`
- **Via Local Network (Mac / Same Wi-Fi)**:
  `http://localhost:5050/api/sparks/trigger`

### Two Ways Sparks Can Trigger the Engine

#### Option A: Sparks sends pre-written content from your Custom Gem
Sparks (or Google Apps Script / Zapier / Make) passes the draft written in your Gem:
```bash
curl -X POST https://344b-103-220-159-214.ngrok-free.app/api/sparks/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The Reality of LLM Token Margins",
    "content": "R.I.P. to the 80% SaaS gross margin narrative in AI startups.\n\nEvery founder pitching an AI wrapper claims software margins.\nThen the AWS Bedrock invoice arrives.\n\nReal margins are 42% after vector indexing and fallback retries.",
    "hook_formula": "F02 R.I.P. Category Obituary",
    "angle": "Unit Economics"
  }'
```
**Result**: The post is saved to the queue and instantly fires an interactive approval card to your Slack channel!

#### Option B: Sparks triggers autonomous generation on a schedule
Sparks simply pings the webhook with a topic (or `auto_generate: true`):
```bash
curl -X POST https://344b-103-220-159-214.ngrok-free.app/api/sparks/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Why small AI teams beat 50-person agencies",
    "auto_generate": false
  }'
```
**Result**: The engine invokes Gemini to write the post, validates buzzwords, queues it, and notifies Slack for approval.

---

## 3. Native Google Antigravity Scheduler (Active)

We have activated the internal cron scheduler inside Antigravity:

- **Task ID**: `task-1153`
- **Cron Expression**: `0 9 * * 1-5` (Every Monday to Friday at 09:00 AM)
- **Action**: Runs `python3 scripts/run_slack_pipeline.py --auto-generate`
- **Behavior**:
  1. Rotates through the founder topic bank.
  2. Generates an authentic, algorithm-compliant post using Gemini.
  3. Audits against the voice rules (0 buzzwords, correct character count).
  4. Dispatches the Block Kit card directly to your Slack channel.
  5. You review and tap `[Approve & Schedule]` from your iPhone.

---

## 4. Summary of the Complete Pipeline

```
  [Google Gemini Gem] ─── (Ideas / Custom drafts) ───┐
                                                     ▼
  [Google Sparks] ───── (HTTP POST Webhook) ──► [Approval Studio Engine]
                                                     ▲
  [Antigravity Cron] ── (Mon-Fri 9AM Auto) ──────────┘
                                                     │
                                                     ▼
                                      [Interactive Slack Card]
                                         (Aryan's Approval)
                                                     │
                                                     ▼
                                     [Publora Cloud Scheduling]
                                                     │
                                                     ▼
                                       🚀 LIVE ON LINKEDIN
```
