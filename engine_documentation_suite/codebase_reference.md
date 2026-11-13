# 📖 Codebase Technical Reference

This guide provides a comprehensive, file-by-file breakdown of every module, client, endpoint, and test suite in the `linkedin-skills` repository.

---

## 1. Core Library (`lib/`)

### `lib/__init__.py`
- Exports the public library interface.
- Implements lazy-loading for HTTP clients (`PubloraClient`, `ApifyClient`, `PixfaroClient`) via PEP 562 `__getattr__` to ensure zero-dependency CLI execution.

### `lib/_env.py`
- Discovers and loads `.env` files across the workspace.
- Caches loaded variables in memory for fast lookup.

### `lib/gemini_generator.py`
- **Main Function**: `generate_post_with_gemini(...)`.
- **Arguments**: `topic`, `hook_preference`, `style`, `instructions`, `length_preset`, `preferred_model`.
- **Reliability**: Iterates through `CANDIDATE_MODELS` with a 15-second timeout per model.
- **Prompting**: Injects `GEMINI_SYSTEM_PROMPT` containing Claude Fable 5.1 cognitive depth and the Tri-Voice synthesis (Aryan x Vaibhav x Raj Shamani).
- **Sanitization**: `_clean_json_text` strips markdown code fences to ensure valid JSON parsing.

### `lib/publora_client.py`
- Direct client for the Publora REST API.
- Implements exponential backoff retries via `@_retry()` decorator.
- Methods: `create_post`, `get_post`, `update_post`, `delete_post`, `create_comment`, `delete_comment`, `create_reaction`, `create_reshare`, `list_platform_connections`.

### `lib/drafts_store.py`
- Thread-safe persistent queue backed by `testing/drafts_queue.json`.
- Implements the 25-word semantic prefix deduplication guard in `create_draft`.
- Provides state transition methods: `update_draft_status`, `list_drafts`, and `get_draft`.

### `lib/slack_approver.py`
- Generates Slack Block Kit UI payloads.
- Methods:
  - `build_slack_approval_blocks(draft)`: Constructs formatted cards with status, copy preview, and action buttons.
  - `send_draft_to_slack(draft)`: Posts the card to `SLACK_WEBHOOK_URL`.
  - `send_published_notification(draft, kind, live_url)`: Posts live LinkedIn links immediately upon publishing.
  - `send_studio_online_notification(public_url, local_url)`: Dispatches active studio links on server start.
  - `process_slack_action(action_value, user_name)`: Dispatches approval or rejection callbacks.

### `lib/backend_selector.py`
- Abstraction layer that routes actions between `publora` (cloud API), `manual` (copy-paste instructions), and `diy` (custom subprocesses).

### `lib/apify_client.py`
- Reads public LinkedIn data without cookies.
- Methods: `fetch_post`, `fetch_post_comments`, `fetch_user_recent_comments`, `fetch_post_engagers`.
- Features an internal 256-entry LRU cache with a 6-hour TTL.

---

## 2. Approval Studio Web Platform (`studio/`)

### `studio/app.py`
- Flask application running on `0.0.0.0:5050`.
- Endpoints:
  - `GET /`: Renders `index.html`.
  - `GET /api/drafts`: Lists drafts filtered by optional status query param.
  - `POST /api/drafts/generate`: Generates a new post using Gemini, queues it, and alerts Slack.
  - `POST /api/drafts/<id>/approve`: Approves and schedules via Publora.
  - `POST /api/drafts/<id>/reject`: Archives draft.
  - `DELETE /api/drafts/<id>`: Permanently removes draft.

### `studio/templates/index.html`
- Responsive mobile web interface built with Bootstrap 5 and Bootstrap Icons.
- Features live KPI metrics, separated status tabs, a Gemini Content Studio form, and real-time character count audits.
- Automatically bypasses ngrok warnings with `ngrok-skip-browser-warning: true` headers.

---

## 3. Operational Scripts (`scripts/`)

- `start_studio.sh`: Boots Flask on port 5050, launches ngrok, updates `.env`, and sends a Slack announcement card.
- `stop_studio.sh`: Terminates background server and tunnel processes.
- `run_slack_pipeline.py`: Automated pipeline CLI for topic drafting and Slack dispatch.
- `slack_listener.py`: Webhook receiver on port 5050 for processing interactive Slack button callbacks.
- `sync_codex_marketplace.py`: Synchronizes root source files into `.codex-marketplace/linkedin-skills`.
- `test_slack_setup.py`: Diagnostics tool verifying webhook URL and Block Kit formatting.

---

## 4. The 12 Canonical Marketing Skills (`skills/`)

The repository adheres to the **agentskills.io** standard with exactly 12 specialized skills:
1. `linkedin-post-writer`: Long-form thought leadership drafting.
2. `linkedin-comment-drafter`: High-leverage contextual commenting on influencer posts.
3. `linkedin-reply-handler`: Engaging replies to comments on your own posts.
4. `linkedin-humanizer`: Audits and scrubs AI buzzwords, em-dash bloat, and robotic tells.
5. `linkedin-hook-extractor`: Deconstructs viral posts into F01-F20 formulas.
6. `linkedin-content-planner`: Content calendar strategy and pillar balancing.
7. `linkedin-engager-analytics`: Profiling commenters and high-affinity connections.
8. `linkedin-thread-monitor`: Real-time monitoring of active engagement spikes.
9. `linkedin-profile-optimizer`: Headline, About, and Experience section tuning.
10. `linkedin-employee-advocacy`: Multi-voice company post amplification.
11. `linkedin-repurposer`: Converting podcasts/talks into scannable text.
12. `linkedin-interviewer`: Extracting authentic founder stories via guided prompts.

---

## 5. Automated Test Suite (`tests/`)

107 automated unit tests verify contract integrity across the entire stack:
- `tests/test_slack_integration.py`: Isolated queue tests and Slack block rendering.
- `tests/test_client_behaviour.py`: Publora and Apify request and error handling.
- `tests/test_response_shapes.py`: Verifies expected JSON schemas from external APIs.
- `tests/test_instruction_integrity.py`: Enforces skill frontmatter and voice rules.
- `tests/test_publora_shapes.py`: Validates cloud post payloads.
