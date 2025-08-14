import socket
import json
import threading
from datetime import datetime

class SimpleHTTPServer:
    def __init__(self, host='127.0.0.1', port=6000):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
        # Sample data
        self.sales_data = [
            {"id": 1, "producto": "Laptop", "precio": 1500.00, "estado": "completada"},
            {"id": 2, "producto": "Mouse", "precio": 25.00, "estado": "pendiente"}
        ]
    
    def create_response(self, status_code, content_type, body):
        """Create HTTP response"""
        response = f"HTTP/1.1 {status_code} OK\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += "Access-Control-Allow-Origin: *\r\n"
        response += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        response += "Access-Control-Allow-Headers: Content-Type\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += body
        return response.encode('utf-8')
    
    def handle_request(self, client_socket):
        """Handle individual client request"""
        try:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                return
                
            lines = request.split('\r\n')
            if not lines:
                return
                
            # Parse request line
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) < 2:
                return
                
            method = parts[0]
            path = parts[1]
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {method} {path}")
            
            # Handle OPTIONS for CORS
            if method == "OPTIONS":
                response = self.create_response("200", "text/plain", "OK")
                client_socket.send(response)
                return
            
            # Route handling
            if path == '/' or path == '':
                data = {
                    "message": "Raw Socket Sales API v1.0",
                    "status": "funcionando",
                    "server": "raw-socket",
                    "time": datetime.now().isoformat()
                }
                response_body = json.dumps(data, indent=2)
                response = self.create_response("200", "application/json", response_body)
                
            elif path == '/health':
                data = {"status": "healthy", "server": "raw-socket"}
                response_body = json.dumps(data)
                response = self.create_response("200", "application/json", response_body)
                
            elif path == '/ventas':
                response_body = json.dumps(self.sales_data, indent=2)
                response = self.create_response("200", "application/json", response_body)
                
            elif path == '/test':
                data = {"test": "success", "socket_server": True, "data": [1, 2, 3]}
                response_body = json.dumps(data)
                response = self.create_response("200", "application/json", response_body)
                
            else:
                data = {"error": "Not found", "path": path}
                response_body = json.dumps(data)
                response = self.create_response("404", "application/json", response_body)
            
            client_socket.send(response)
            
        except Exception as e:
            print(f"Error handling request: {e}")
            error_response = self.create_response("500", "text/plain", f"Server Error: {e}")
            try:
                client_socket.send(error_response)
            except:
                pass
        finally:
            client_socket.close()
    
    def start(self):
        """Start the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            
            self.running = True
            
            print("="*60)
            print("RAW SOCKET HTTP SERVER")
            print("="*60)
            print(f"Server running on: http://{self.host}:{self.port}")
            print(f"Health check: http://{self.host}:{self.port}/health")
            print(f"Test endpoint: http://{self.host}:{self.port}/test")
            print(f"Sales data: http://{self.host}:{self.port}/ventas")
            print("="*60)
            print("Press Ctrl+C to stop")
            print("="*60)
            
            while self.running:
                try:
                    client_socket, addr = self.socket.accept()
                    print(f"Connection from: {addr}")
                    
                    # Handle each request in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_request,
                        args=(client_socket,),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                        break
                        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("Server stopped")

if __name__ == "__main__":
    server = SimpleHTTPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()