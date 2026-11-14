# FrontierPilot 2.0 — Complete API Inventory

**Total Registered Endpoints**: 82  
**Base URL**: `http://127.0.0.1:5050`  
**Authentication**: Session Cookie (`authenticated=True`) or `Bearer <FRONTIER_MASTER_PIN>`

---

## 1. Authentication & Session Gatekeeper

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | None (Rate Limited) | PIN verification with 5-attempt/300s lockout protection. |
| `GET` | `/api/auth/status` | None | Returns active authentication state and user identity. |
| `POST` | `/api/auth/request_slack_access` | None | Triggers 1-tap push notification to Aryan's Slack for remote unlock. |
| `GET, POST` | `/api/auth/approve_slack/<req_id>` | None (Token bound) | Approves pending login request from Slack button. |
| `GET` | `/api/auth/check_approval/<req_id>` | None | Long-polling endpoint for browser to check Slack push status. |
| `GET` | `/login` | None | Renders Master PIN entry screen. |
| `GET` | `/logout` | Session | Clears session cookie and redirects to `/login`. |

---

## 2. LinkedIn Creator Studio & Draft Lifecycle

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/drafts` | Yes | List all drafts in SQLite WAL, optionally filtered by `?status=`. |
| `POST` | `/api/drafts` | Yes | Create new draft with deduplication guard. |
| `POST` | `/api/drafts/create` | Yes | Alias for draft creation. |
| `POST` | `/api/drafts/generate` | Yes | Generate dynamic draft via Gemini cascade and save to queue. |
| `POST, PUT` | `/api/drafts/<draft_id>` | Yes | Update draft content or schedule time (optimistic locking). |
| `DELETE` | `/api/drafts/<draft_id>` | Yes | Remove draft from database. |
| `POST` | `/api/drafts/<draft_id>/approve`| Yes | Approve draft and schedule/publish via Publora. |
| `POST` | `/api/drafts/<draft_id>/reject` | Yes | Mark draft as rejected. |
| `POST` | `/api/drafts/<draft_id>/restore`| Yes | Restore rejected draft back to pending. |
| `POST` | `/api/drafts/repurpose` | Yes | Repurpose career achievement into viral post. |
| `POST` | `/api/sparks/trigger` | Yes | Spontaneous thought capture and instant post drafting. |

---

## 3. Career Opportunities & Radar

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `GET, POST` | `/api/opportunities` | Yes | List or create career opportunities. |
| `POST, PUT` | `/api/opportunities/<opp_id>`| Yes | Update opportunity stage, match score, or notes. |
| `DELETE` | `/api/opportunities/<opp_id>`| Yes | Delete tracked opportunity. |
| `POST` | `/api/opportunities/<opp_id>/score` | Yes | Run AI match evaluation and gap analysis via Gemini. |
| `POST` | `/api/opportunities/<opp_id>/resume`| Yes | Generate tailored ATS resume matching JD keywords. |
| `GET` | `/api/opportunities/<opp_id>/pitch` | Yes | Generate 3-sentence founder DM pitch. |
| `GET` | `/api/opportunities/<opp_id>/interview_prep`| Yes | Generate tactical interview questions and talking points. |
| `GET` | `/api/opportunities/<opp_id>/bundle` | Yes | Download zipped application dossier (Resume, Cover Letter, Pitch). |
| `POST` | `/api/opportunities/<opp_id>/send_slack` | Yes | Dispatch interactive Block Kit approval card for this role to Slack. |

---

## 4. Vaibhav Sisinty Growth Studio (5 Tools)

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/frontierpilot/vaibhav/gps` | Yes | GPS Framework Auditor (Gaslight, Pushback, Stress-Test). |
| `POST` | `/api/frontierpilot/vaibhav/xyz` | Yes | Google XYZ Bullet Formula rewriter. |
| `POST` | `/api/frontierpilot/vaibhav/prd` | Yes | 90-Day Tactical Proof-of-Work PRD generator. |
| `POST` | `/api/frontierpilot/vaibhav/dm` | Yes | 3-Sentence Direct Founder Outreach DM engine. |
| `POST` | `/api/frontierpilot/vaibhav/video_short` | Yes | 60-Second Video Short Script generator. |

---

## 5. Multi-Cloud Synchronisation

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/frontierpilot/sync` | Yes | Full sync across Notion, Google Sheets, Drive, and Wix. |
| `GET` | `/api/frontierpilot/status` | Yes | Health check and connector readiness status. |
| `GET, POST` | `/api/frontierpilot/notion-pull`| Yes | Reconcile opportunities from live Notion database. |
| `GET, POST` | `/api/frontierpilot/wix-sync` | Yes | Sync staged content to Wix CMS staging collection. |
| `POST` | `/api/frontierpilot/send_digest` | Yes | Send executive career radar summary to Slack. |
| `GET` | `/api/frontierpilot/export/<kind>` | Yes | Export pipeline data as CSV, Markdown, or JSON. |

---

## 6. Slack Interactive Webhooks & Events

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/slack/interactions` | HMAC Signature | Receives button clicks (`approve`, `reject`) with replay defense. |
| `POST` | `/slack/events` | HMAC Signature | Receives Slack app mentions and conversational messages. |

---

## 7. PWA Shell & Static Assets

| Method | Endpoint | Auth Required | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/`, `/frontierpilot`, `/gethired`, `/dossier` | Yes | Serves primary 10-tab cosmic single-page cockpit. |
| `GET` | `/sw.js`, `/manifest.json` | None | PWA service worker and installation manifest. |
| `GET` | `/assets/<path>` | None | Static CSS, JS, and font vendor libraries. |
| `GET` | `/media/<path>` | None | Generated screenshots and media assets. |
