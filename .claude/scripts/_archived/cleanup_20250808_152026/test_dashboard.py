#!/usr/bin/env python3
"""Test if basic HTTP server works"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

class TestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Dashboard Test - Server is working!</h1>")

try:
    server = HTTPServer(('localhost', 3000), TestHandler)
    print("Test server running at http://localhost:3000")
    print("Press Ctrl+C to stop")
    server.serve_forever()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)