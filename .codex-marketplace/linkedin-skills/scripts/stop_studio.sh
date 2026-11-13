#!/usr/bin/env bash
# Stop LinkedIn Approval Studio & ngrok
echo "Stopping Approval Studio and ngrok..."
pkill -f "python3 studio/app.py" || true
pkill -f "ngrok http 5050" || true
echo "Stopped."
