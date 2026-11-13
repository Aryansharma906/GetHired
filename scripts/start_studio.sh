#!/usr/bin/env bash
# Start LinkedIn Approval Studio & ngrok in background
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

# 1. Start Studio App if not already running
if lsof -Pi :5050 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Approval Studio is already running on port 5050."
else
    echo "🚀 Starting Approval Studio on port 5050..."
    nohup python3 studio/app.py > /tmp/linkedin_studio.log 2>&1 &
    sleep 2
fi

# 2. Start ngrok if not already running
if pgrep -x "ngrok" >/dev/null ; then
    echo "✅ ngrok tunnel is already active."
else
    echo "🌐 Starting ngrok tunnel..."
    nohup ngrok http 5050 > /tmp/linkedin_ngrok.log 2>&1 &
    sleep 3
fi

# 3. Fetch active public URL from ngrok API and sync to .env
PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else '')" 2>/dev/null || true)

if [ -n "$PUBLIC_URL" ]; then
    echo "✨ Live Studio URL: $PUBLIC_URL"
    if grep -q "STUDIO_URL=" .env; then
        sed -i '' "s|STUDIO_URL=.*|STUDIO_URL=$PUBLIC_URL|" .env
    else
        echo "STUDIO_URL=$PUBLIC_URL" >> .env
    fi

    # Dispatch active link announcement to Slack
    python3 -c "
from lib.slack_approver import send_studio_online_notification
res = send_studio_online_notification('$PUBLIC_URL')
if res.get('success'):
    print('📢 Dispatched active Studio link directly to your Slack channel!')
"
else
    echo "⚠️ Could not read ngrok public URL yet."
fi
