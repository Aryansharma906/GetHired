# FrontierPilot 2.0 — Master Test Plan

This document establishes the test inventory, quality gates, test execution matrix, and verification standards.

---

## 1. Test Levels & Strategy

```
                                 [E2E / Playwright]
                           Cross-Viewport Responsive Matrix
                            (1440, 1280, 1024, 768, 390, 375, 320)
                                        │
                                        ▼
                               [Integration Tests]
                          Flask APIs ──> SQLite WAL ──> Slack
                                        │
                                        ▼
                                  [Unit Tests]
                      139 Tests across Models, Scrapers,
                         State Machine & Invariants
```

---

## 2. Test Execution Inventory

### 2.1 Unit & Contract Tests (`tests/`)
- `tests/test_slack_integration.py`: Validates Block Kit layout, character bounds, and approval callbacks.
- `tests/test_frontierpilot_creator_studio.py`: Validates draft CRUD, optimistic concurrency, and authentication.
- `tests/test_vaibhav_growth_engine.py`: Validates all 5 Vaibhav tools with live model cascade.
- `tests/test_job_hunter_engine.py`: Validates Google XYZ tailoring, match scoring, and bundle packaging.
- `tests/test_frontierpilot_integrator.py`: Validates cloud reconciliation, CSV generation, and hash signatures.
- `tests/test_client_behaviour.py`: Validates Apify and Publora client error handling and backoffs.
- `tests/test_response_shapes.py`: Validates schema conformance against documented API responses.
- `tests/test_instruction_integrity.py`: Enforces voice rules, word blacklist, and character limits.

### 2.2 End-to-End Responsive Suite (`scripts/full_ux_audit_suite.js`)
- Runs Playwright headless across 7 viewports:
  - Desktop 1440 × 900
  - Laptop 1280 × 800
  - Tablet Landscape 1024 × 768
  - Tablet Portrait 768 × 1024
  - Mobile iPhone 390 × 844
  - Mobile SE 375 × 667
  - Narrow Mobile 320 × 568
- Evaluates:
  - Horizontal overflow (`scrollWidth > innerWidth`)
  - Sub-44px touch targets
  - Form control accessibility (`aria-label` coverage)
  - Color contrast and focus indicator visibility
  - Modal backdrop lifecycle and body lock cleanup

### 2.3 Repository Integrity & Compliance Suite
- `scripts/check_no_secrets.py`: Scans 1,340+ tracked files for private credentials.
- `scripts/check_frontmatter.py`: Validates that all 12 skills declare name & description ($\le 400$ chars, zero em-dashes).
- `scripts/check_config.py --offline`: Verifies offline configuration shapes.
- `scripts/check_actor_inputs.py`: Validates Apify actor input schemas against official contracts.

---

## 3. Quality Gate Thresholds
- **Unit Test Pass Rate**: 100% (0 failures, 0 errors).
- **Tracked Secrets**: 0.
- **Skill Invariant**: Exactly 12 skills in `skills/`.
- **Horizontal Overflow**: 0px across all 7 viewports.
- **Master PIN Security**: Constant-time comparison + 5-attempt/300s progressive lockout.
- **Slack Signature**: Valid HMAC-SHA256 required on public webhooks.
