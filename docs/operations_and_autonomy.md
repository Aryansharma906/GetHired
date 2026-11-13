# 🕹️ Operations & Autonomy Runbook

This document details the operational commands, daily workflows, and the official autonomous mandate governing Antigravity and Aryan Sharma.

---

## 1. Daily Operations & Quick Commands

### A. Booting the Studio & Webhooks
```bash
./scripts/start_studio.sh
```
**What happens automatically:**
1. Verifies if port 5050 is listening. If not, launches `python3 studio/app.py`.
2. Verifies if ngrok is active. If not, launches `ngrok http 5050`.
3. Reads the active public tunnel URL from ngrok's local API (`127.0.0.1:4040`).
4. Updates `STUDIO_URL` in `.env`.
5. Dispatches an announcement card to Aryan's Slack channel with the clickable public and local Wi-Fi links.

### B. Stopping the System
```bash
./scripts/stop_studio.sh
```
Terminates both the Flask server and the ngrok tunnel.

### C. Triggering an Automated Post Generation
```bash
# Draft a specific topic and send approval card to Slack
python3 scripts/run_slack_pipeline.py --topic "Why small AI teams beat 50-person agencies"

# Auto-rotate from founder topic bank
python3 scripts/run_slack_pipeline.py --auto-generate

# Dry-run preview without sending to Slack
python3 scripts/run_slack_pipeline.py --dry-run
```

### D. Running Verification & Sync
```bash
# Run the complete 107-test unit suite
python3 -m unittest discover -s tests

# Synchronize Codex marketplace package
python3 scripts/sync_codex_marketplace.py
```

---

## 2. The Autonomous Operator Mandate

Per the official author directive:
> **"You are an autonomous agent under my command. I am giving you some control and report everything on Slack."**  
> — *Aryan Sharma*

### A. Antigravity Operates Autonomously (Zero Interruption)
To maximize velocity and eliminate cognitive load, Antigravity executes routine technical tasks without asking for user confirmation:
- Running test discovery and validation suites.
- Synchronizing packages and manifests (`scripts/sync_codex_marketplace.py`).
- Terminal executions, background process maintenance, and queue checks.
- Code modifications, refactoring, and local plumbing.
- **Autonomous Slot Capacity Management**: Tracking Publora's 3-slot cloud scheduling limit and automatically promoting queued drafts into Publora as earlier posts publish.
- Discovering active ports, recovering tunnels, and syncing live URLs.

### B. Mandatory Real-Time Slack Reporting
Every automated action must report directly to Aryan's Slack channel:
- When a post draft is generated ➔ Interactive Slack approval card dispatched.
- When a post transitions to live ➔ Instant Slack notification with direct LinkedIn share URL.
- When the studio or tunnel restarts ➔ Fresh access links dispatched to Slack.
- When queued drafts are auto-promoted into Publora cloud slots ➔ Confirmation card sent to Slack.

Aryan controls the entire system from mobile Slack with zero requirement to open a terminal.

### C. The Human Taste Gate (High Priority Only)
Aryan only intervenes for:
1. **Content Review & Approval**: Editorial sign-off on new LinkedIn posts and high-leverage comments (via interactive Slack cards or the mobile Approval Studio).
2. **Irreversible / Destructive Decisions**: High-stakes strategic operations that cannot be undone.

---

## 3. Handling Reboots & Session Closures

- **Scheduled Posts on LinkedIn**:
  - Posts already scheduled via Publora reside in **Publora’s cloud infrastructure**. They publish to LinkedIn on schedule even if your laptop is closed, offline, or asleep.
- **Persistent Data**:
  - All drafts, queue states, and logs are saved permanently on disk in `testing/drafts_queue.json`.
- **Approval Studio & Slack Buttons**:
  - The local server and tunnel close when Antigravity closes.
  - To reactivate in 2 seconds upon reopening, simply run:
    ```bash
    ./scripts/start_studio.sh
    ```
    *(or simply message Antigravity: **"start"**)*.
