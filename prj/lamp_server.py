# lamp_server.py

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class LampRequestHandler(BaseHTTPRequestHandler):
    receiver_instance = None  # Reference ke instance ScaleReceiver

    def do_OPTIONS(self):
        # Handle CORS Preflight request dari browser
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
            data = json.loads(body or "{}")

            status_type = data.get("status")
            code = data.get("code")
            message = data.get("message")

            if LampRequestHandler.receiver_instance:
                # Panggil handler lampu di thread terpisah agar HTTP response tidak delay
                threading.Thread(
                    target=LampRequestHandler.receiver_instance.trigger_lamp_from_html,
                    args=(status_type, code, message),
                    daemon=True
                ).start()

            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Private-Network', 'true')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'{{"error":"{str(e)}"}}'.encode('utf-8'))

    def log_message(self, format, *args):
        return  # Matikan log HTTP server bawaan di terminal

def start_lamp_server(receiver_instance, host='127.0.0.1', port=5000):
    LampRequestHandler.receiver_instance = receiver_instance
    server = HTTPServer((host, port), LampRequestHandler)
    print(f"🌐 HTTP Server Lampu berjalan di http://{host}:{port}")
    server.serve_forever()