#!/usr/bin/env python3
"""
Simple HTTP server to serve the upload test interface
"""
import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 3000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Starting test server at http://localhost:{PORT}")
        print(f"📁 Serving from: {Path(__file__).parent}")
        print(f"🌐 Opening test interface in browser...")
        print()
        print("📋 Test Instructions:")
        print("1. Make sure your Django server is running on port 8001")
        print("2. Use the web interface to login (testuser@example.com / testpass123)")
        print("3. Upload a PDF resume")
        print("4. Check the analysis status")
        print()
        print("Press Ctrl+C to stop the server")
        
        # Open browser
        try:
            webbrowser.open(f'http://localhost:{PORT}/test_upload_interface.html')
        except:
            print("Could not open browser automatically")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
