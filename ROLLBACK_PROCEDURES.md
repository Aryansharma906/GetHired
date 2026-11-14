# FrontierPilot 2.0 — Disaster Recovery & Rollback Procedures

**Document Target**: Operational Runbooks, Disaster Recovery (DR), and Data Restoration  
**Audience**: DevOps Engineers, SREs, Antigravity Autonomous Agents, Platform Maintainers  
**Document Date**: November 14, 2026  
**Status**: **ACTIVE & CERTIFIED**

---

## 1. Executive Summary

This document specifies standard operating procedures for rolling back application code, restoring database state, recovering from network or tunnel disruptions, and rotating compromised credentials without service interruption or data loss.

---

## 2. Persistence Layer Rollback & Restoration

### Scenario A: SQLite Database Corruption or Failed Migration
If `testing/frontierpilot.db` becomes corrupt or enters an inconsistent state, it can be instantly rebuilt from the atomic JSON mirror files (`testing/drafts_queue.json` and `testing/opportunities_tracker.json`).

#### Step-by-Step Restoration from JSON Mirror:
1. Stop the running Flask application:
   ```bash
   kill $(lsof -ti :5050)
   ```
2. Archive the damaged database file:
   ```bash
   mv testing/frontierpilot.db testing/frontierpilot.db.corrupt.$(date +%s)
   rm -f testing/frontierpilot.db-wal testing/frontierpilot.db-shm
   ```
3. Re-initialize SQLite schema and ingest JSON mirror:
   ```bash
   python3 -c "
   from lib.database import init_db, migrate_json_to_sqlite
   init_db()
   migrate_json_to_sqlite()
   print('Database successfully restored from JSON mirror.')
   "
   ```
4. Verify record integrity:
   ```bash
   sqlite3 testing/frontierpilot.db "SELECT count(*) FROM drafts; SELECT count(*) FROM opportunities;"
   ```
5. Restart Flask service:
   ```bash
   python3 studio/app.py &
   ```

### Scenario B: Restoring from Scheduled Hot Backup
If periodic backups are archived in `testing/backups/`:
```bash
# Locate latest verified backup
LATEST_BACKUP=$(ls -t testing/backups/frontierpilot_backup_*.db | head -1)

# Restore with atomic copy
cp "$LATEST_BACKUP" testing/frontierpilot.db
rm -f testing/frontierpilot.db-wal testing/frontierpilot.db-shm

# Verify integrity
sqlite3 testing/frontierpilot.db "PRAGMA integrity_check;"
```

---

## 3. Codebase & Version Rollback

### Scenario C: Deploy Regression / Broken Feature Rollback
To roll back a bad commit without breaking the repository invariants:
1. Inspect commit history:
   ```bash
   git log --oneline -n 5
   ```
2. Revert the problematic commit:
   ```bash
   git revert <commit-sha> --no-edit
   ```
3. Synchronize the Codex marketplace mirror:
   ```bash
   python3 scripts/sync_codex_marketplace.py
   ```
4. Rebuild the static PWA distribution:
   ```bash
   python3 scripts/build_studio_static.py
   ```
5. Run the test suite:
   ```bash
   python3 -m unittest discover -s tests
   ```

---

## 4. Security & Credential Emergency Rotation Runbook

### Scenario D: Compromised PIN or Leaked API Token

#### 1. Rotating the Master PIN:
1. Open local untracked `.env`:
   ```bash
   # Update PIN value
   FRONTIERPILOT_PIN="new-cryptographically-secure-pin-2026"
   ```
2. Restart the Flask app to invalidate existing active session tokens:
   ```bash
   kill $(lsof -ti :5050)
   python3 studio/app.py &
   ```

#### 2. Rotating Slack Signing Secret:
1. Navigate to Slack API Dashboard $\to$ Basic Information $\to$ App Credentials.
2. Click **Regenerate** under Signing Secret.
3. Update `SLACK_SIGNING_SECRET` in `.env`.
4. The application immediately validates against the new secret without code changes.

#### 3. Rotating Gemini API Key:
1. Navigate to Google AI Studio $\to$ API Keys.
2. Revoke compromised key; generate new key.
3. Update `GEMINI_API_KEY` in `.env`.

---

## 5. Network & Tunnel Recovery Runbook

### Scenario E: Ngrok Tunnel Disconnection or 404
If the mobile tunnel becomes unreachable:
1. Verify if the local Flask app is still healthy:
   ```bash
   curl -s http://127.0.0.1:5050/healthz
   ```
2. Check ngrok process:
   ```bash
   curl -s http://127.0.0.1:4040/api/tunnels
   ```
3. If ngrok has disconnected or crashed:
   ```bash
   kill $(pgrep -f "ngrok http")
   ngrok http 5050 > /dev/null 2>&1 &
   sleep 2
   NEW_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])")
   echo "New tunnel live at: $NEW_URL"
   ```
4. If testing Slack button callbacks, update the Slack App Interactivity Request URL to `$NEW_URL/slack/interactions`.
