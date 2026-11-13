#!/usr/bin/env python3
"""Build and package static distribution for GitHub Pages & Netlify.

Generates:
- docs/index.html (Studio Hub PWA with pre-cached drafts & opportunities)
- docs/dossier.html (Dossier Career Radar & Application Funnel PWA)
- studio/templates/index.html (Local Flask template)
- studio/templates/dossier.html (Local Flask template)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
TEMPLATES_DIR = ROOT / "studio" / "templates"

def build():
    print("🔨 Building Static PWA Distribution for GitHub Pages & Netlify...")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load latest drafts & opportunities
    drafts_path = ROOT / "testing" / "drafts_queue.json"
    drafts = []
    if drafts_path.exists():
        try:
            drafts = json.loads(drafts_path.read_text(encoding="utf-8"))
        except Exception:
            drafts = []

    opps_path = ROOT / "testing" / "opportunities_tracker.json"
    opps = []
    if opps_path.exists():
        try:
            opps = json.loads(opps_path.read_text(encoding="utf-8"))
        except Exception:
            opps = []

    # 2. Read base studio template
    src_studio = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")

    # Inject local assets, PWA manifest, service worker, seed drafts, and Dossier button
    static_studio = src_studio

    # Update stylesheet references to local assets
    static_studio = static_studio.replace(
        '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">',
        '<link rel="manifest" href="./manifest.json">\n  <link rel="icon" type="image/svg+xml" href="./assets/icon.svg">\n  <link rel="stylesheet" href="./assets/bootstrap.min.css">'
    )
    static_studio = static_studio.replace(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">',
        '<link rel="stylesheet" href="./assets/bootstrap-icons.min.css">\n  <script src="./assets/jszip.min.js"></script>'
    )
    static_studio = static_studio.replace(
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>',
        '<script src="./assets/bootstrap.bundle.min.js"></script>'
    )

    # Add Service Worker registration and default drafts seed
    sw_and_seed_code = f"""
<script>
if ('serviceWorker' in navigator) {{
  window.addEventListener('load', () => {{
    navigator.serviceWorker.register('./sw.js').then((reg) => {{
      console.log('[PWA] Service Worker active in Studio:', reg.scope);
    }}).catch(() => {{}});
  }});
}}
const SEED_STATIC_DRAFTS = {json.dumps(drafts, indent=2)};
</script>
"""
    if "SEED_STATIC_DRAFTS" not in static_studio:
        static_studio = static_studio.replace("<script>\nlet activeTab = 'pending_approval';", sw_and_seed_code + "\n<script>\nlet activeTab = 'pending_approval';")

    # Ensure allDrafts initializes from SEED_STATIC_DRAFTS if API fails
    static_studio = static_studio.replace(
        "allDrafts = await res.json();\n    }",
        "allDrafts = await res.json();\n    } else if (typeof SEED_STATIC_DRAFTS !== 'undefined' && Array.isArray(SEED_STATIC_DRAFTS)) {\n      allDrafts = SEED_STATIC_DRAFTS;\n    }"
    )

    # Add getHired Launch Button in navbar if not present
    gethired_btn = '<a href="./gethired.html" class="btn btn-warning btn-sm fw-bold d-flex align-items-center gap-1 shadow-sm"><i class="bi bi-briefcase-fill me-1"></i> getHired Hub</a>'
    if './gethired.html' not in static_studio and './dossier.html' not in static_studio:
        static_studio = static_studio.replace(
            '<div class="d-flex align-items-center gap-2">',
            f'<div class="d-flex align-items-center gap-2">\n        {gethired_btn}'
        )

    # Write docs/index.html
    (DOCS_DIR / "index.html").write_text(static_studio, encoding="utf-8")
    print(f"  • Generated {DOCS_DIR / 'index.html'} ({len(static_studio)} chars)")

    # 3. Synchronize docs/dossier.html, docs/gethired.html, and docs/frontierpilot.html from template
    src_dossier = (TEMPLATES_DIR / "dossier.html").read_text(encoding="utf-8")
    (DOCS_DIR / "dossier.html").write_text(src_dossier, encoding="utf-8")
    (DOCS_DIR / "gethired.html").write_text(src_dossier, encoding="utf-8")
    (DOCS_DIR / "frontierpilot.html").write_text(src_dossier, encoding="utf-8")
    print(f"  • Generated {DOCS_DIR / 'dossier.html'}, {DOCS_DIR / 'gethired.html'} & {DOCS_DIR / 'frontierpilot.html'} ({len(src_dossier)} chars)")

    print("✅ Static Studio & FrontierPilot build complete!")

if __name__ == "__main__":
    build()
