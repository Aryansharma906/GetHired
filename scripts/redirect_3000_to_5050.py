#!/usr/bin/env python3
"""Redirects port 3000 traffic directly to port 5050 FrontierPilot Cockpit."""
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        target = "http://127.0.0.1:5050/frontierpilot"
        self.send_header("Location", target)
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(b"Redirecting to FrontierPilot Unified Cockpit on port 5050...")

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        pass

def run():
    try:
        server = HTTPServer(('127.0.0.1', 3000), RedirectHandler)
        print("Redirect server listening on http://127.0.0.1:3000 -> 5050")
        server.serve_forever()
    except Exception as e:
        print(f"Port 3000 redirect server notice: {e}")

if __name__ == '__main__':
    run()
