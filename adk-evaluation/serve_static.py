#!/usr/bin/env python3
"""
Simple static file server for serving presentations
"""

import http.server
import socketserver
import os
import threading
from pathlib import Path

def start_static_server(port=8002, directory="static"):
    """Start a simple HTTP server to serve static files"""
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            print(f"🌐 Static file server running on http://localhost:{port}")
            print(f"📁 Serving files from: {os.path.abspath(directory)}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"⚠️  Port {port} is already in use")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    # Ensure static directory exists
    os.makedirs("static/presentations", exist_ok=True)
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_static_server, daemon=True)
    server_thread.start()
    
    print("Static file server started. Press Ctrl+C to stop.")
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n🛑 Stopping static file server...") 