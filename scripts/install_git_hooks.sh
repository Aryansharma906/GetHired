#!/bin/bash
# Install git hooks to ensure no secrets or private credentials are ever committed.
set -euo pipefail

HOOK_DIR="$(git rev-parse --git-path hooks)"
PRE_COMMIT="$HOOK_DIR/pre-commit"

cat <<'EOF' > "$PRE_COMMIT"
#!/bin/bash
# Pre-commit secret scanning hook
echo "🔒 [Security Guard] Scanning staged files for secrets and credentials..."
python3 scripts/check_no_secrets.py

# Check git status for forbidden files staged
STAGED_ENV=$(git diff --cached --name-only | grep -E '(^|/)\.env(\.[^/]*)?$' | grep -vE '\.env\.(example|sample|template)$' || true)
if [ -n "$STAGED_ENV" ]; then
    echo "❌ [SECURITY ERROR] Attempting to commit private .env file:"
    echo "$STAGED_ENV"
    echo "Aborting commit. Keep private credentials in testing/ or .env.local (ignored)."
    exit 1
fi

echo "✅ [Security Guard] Clean! No credentials found in staged changes."
EOF

chmod +x "$PRE_COMMIT"
echo "✅ Pre-commit security hook installed to $PRE_COMMIT"
