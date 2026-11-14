# Hermes Agent Autonomous Integration & Operations Manual
**FrontierPilot 2.0 & LinkedIn Autonomous Creator Studio**

---

## 1. System Overview

**FrontierPilot 2.0** is deployed 24/7 on **Netlify Edge and Serverless Functions** (`https://frontierpilot-studio.netlify.app`). It runs continuously in the cloud, completely independent of local hardware or whether any computer is turned on or off.

This integration allows **Hermes Agent** (developed by Nous Research) to:
1. **Discover & Execute Skills**: Dynamically load and invoke the 12 LinkedIn marketing skills and FrontierPilot career automation tools.
2. **Dispatch Autonomous Tasks**: Generate LinkedIn founder posts with Google Gemini 2.0, evaluate executive AI opportunities, and send interactive Block Kit cards to Slack.
3. **Continuous Iteration & Auto-Redeployment**: Make code changes, add new skills, commit to GitHub, and have Netlify automatically rebuild and redeploy the platform without human friction.

---

## 2. Serverless 24/7 Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `https://frontierpilot-studio.netlify.app/api/health` | `GET` | Health check, uptime mode, and active cloud services. |
| `https://frontierpilot-studio.netlify.app/api/hermes/status` | `GET` | Hermes Agent bridge status, capabilities, and registered tools. |
| `https://frontierpilot-studio.netlify.app/api/hermes/skills` | `GET` | Full catalog of 12 LinkedIn skills + career radar tools in tool-calling format. |
| `https://frontierpilot-studio.netlify.app/api/hermes/dispatch` | `POST` | Dispatches autonomous tasks (`draft_post`, `slack_alert`, etc.). |
| `https://frontierpilot-studio.netlify.app/api/hermes/redeploy` | `POST` | Registers redeploy triggers or confirms active deployment state. |
| `https://frontierpilot-studio.netlify.app/api/frontierpilot/status` | `GET` | Cloud sync status across Gemini, Sheets, Drive, Notion, and Slack. |
| `https://frontierpilot-studio.netlify.app/api/frontierpilot/jobs` | `GET` | High-priority executive AI & systems engineering opportunities. |
| `https://frontierpilot-studio.netlify.app/api/drafts` | `GET, POST` | Post creation, generation, and approval queue. |

---

## 3. Hermes Agent Tool & Function Calling

Hermes Agent can query `GET /api/hermes/skills` to receive tool schemas directly.

### Example: Dispatching a Post Generation Task
```bash
curl -X POST https://frontierpilot-studio.netlify.app/api/hermes/dispatch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hermes_live_frontierpilot_autonomy_9956" \
  -d '{
    "action": "draft_post",
    "params": {
      "topic": "Why single-developer AI startups outship 50-person engineering teams",
      "hook_formula": "Contrarian Truth"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "action": "draft_post",
  "content": "Most engineering leaders think adding more developers speeds up delivery...\n\nThe real moat in 2026 isn't headcount. It's leverage per engineer.",
  "slack_dispatched": true,
  "timestamp": "2026-11-14T03:54:00.000Z"
}
```

---

## 4. How Hermes Agent Modifies Code and Auto-Redeploys

### A. Git-Driven Continuous Deployment (Recommended)
1. **Hermes Agent clones or updates the repo**:
   ```bash
   git pull origin main
   ```
2. **Hermes Agent makes improvements**:
   - Updates frontend in `docs/`
   - Adds or refines a skill in `skills/`
   - Enhances serverless functions in `netlify/functions/`
3. **Hermes Agent validates and pushes**:
   ```bash
   python3 scripts/check_frontmatter.py
   python3 scripts/check_no_secrets.py
   git commit -am "feat(hermes): add new skill or optimize UI"
   git push origin main
   ```
4. **Instant Netlify Redeployment**:
   - Netlify detects the push on `main`.
   - Runs `npm run build`.
   - Atomically deploys to `https://frontierpilot-studio.netlify.app` within 15 seconds.

### B. Direct Netlify CLI / MCP Deployment
Hermes Agent can deploy directly via the Netlify MCP proxy or Netlify CLI:
```bash
npx -y @netlify/mcp@latest --site-id 76740519-e8cf-4a61-9349-84e4f679ad7d
```

---

## 5. Security & Authentication

- **Bearer Token**: Requests to protected `/api/hermes/*` endpoints should pass:
  `Authorization: Bearer <HERMES_API_KEY>` or `X-Hermes-Key: <HERMES_API_KEY>`.
- **Environment Isolation**: Secrets (`GEMINI_API_KEY`, `SLACK_WEBHOOK_URL`, `PUBLORA_API_KEY`) are encrypted on Netlify and never exposed to the client-side bundle.

---

## 6. Verification Checklist for Hermes Agent

- [x] 24/7 Always-On URL: `https://frontierpilot-studio.netlify.app`
- [x] Zero Local Machine Dependency (runs in Netlify Cloud)
- [x] Serverless Gemini 2.0 Flash / Pro post generator
- [x] Slack Interactive Approval Hub connection
- [x] 12 LinkedIn skills + FrontierPilot Career Radar registered
- [x] Continuous deployment on every git commit
