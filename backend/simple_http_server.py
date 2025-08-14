#!/usr/bin/env python3

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class SalesAPIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Route handling
        if parsed_path.path == '/':
            response = {
                "message": "Sales Backend API v1.0 (HTTP Server)",
                "status": "funcionando",
                "docs": "/docs",
                "server": "Python HTTP Server"
            }
        elif parsed_path.path == '/health':
            response = {"status": "healthy", "server": "simple-http"}
        elif parsed_path.path == '/test':
            response = {"test": "success", "data": [1, 2, 3, 4, 5]}
        elif parsed_path.path == '/ventas':
            response = [
                {"id": 1, "producto": "Laptop", "precio": 1500.00, "estado": "completada"},
                {"id": 2, "producto": "Mouse", "precio": 25.00, "estado": "pendiente"}
            ]
        elif parsed_path.path == '/dashboard/stats':
            response = {
                "ventas_mes": 1545.00,
                "cantidad_ventas": 2,
                "clientes_nuevos": 2,
                "meta_mes": 75
            }
        else:
            response = {"error": "Endpoint not found", "path": parsed_path.path}
        
        # Send JSON response
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"message": "POST request received", "status": "ok"}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8005):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, SalesAPIHandler)
    
    print("="*60)
    print("SIMPLE HTTP SALES API SERVER")
    print("="*60)
    print(f"Server running on: http://127.0.0.1:{port}")
    print(f"Health check: http://127.0.0.1:{port}/health")
    print(f"Test endpoint: http://127.0.0.1:{port}/test")
    print(f"Sales data: http://127.0.0.1:{port}/ventas")
    print("="*60)
    print("Press Ctrl+C to stop")
    print("="*60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()