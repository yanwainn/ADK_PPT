#!/usr/bin/env python3
"""
Static file server for serving generated presentations.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def serve_static_files():
    """Start a static file server for presentations."""
    
    # Set up directories
    base_dir = Path(__file__).parent
    static_dir = base_dir / "static"
    presentations_dir = static_dir / "presentations"
    
    # Create directories if they don't exist
    static_dir.mkdir(exist_ok=True)
    presentations_dir.mkdir(exist_ok=True)
    
    # Change to static directory to serve files
    os.chdir(static_dir)
    
    # Set up the server
    PORT = 8002
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🚀 Presentation server running on http://localhost:{PORT}")
            print(f"📂 Serving static files from: {static_dir}")
            print(f"📊 Presentations available at: http://localhost:{PORT}/presentations/")
            print(f"📁 Files in presentations directory:")
            
            # List available presentations
            for file in presentations_dir.glob("*.html"):
                print(f"   📄 http://localhost:{PORT}/presentations/{file.name}")
            
            print(f"\n🔄 Server ready - waiting for requests...")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Static server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use. Please stop the existing server first.")
        else:
            print(f"❌ Server error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    serve_static_files() 