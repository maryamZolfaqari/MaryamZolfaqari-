# triangle_api.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math

class TriangleHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # اجازه برای HTML
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        lat1 = float(data.get('lat1', 0))
        lon1 = float(data.get('lon1', 0))
        lat2 = float(data.get('lat2', 0))
        lon2 = float(data.get('lon2', 0))
        lat3 = float(data.get('lat3', 0))
        lon3 = float(data.get('lon3', 0))

        def distance(x1, y1, x2, y2):
            return math.sqrt((x2-x1)**2 + (y2-y1)**2)

        d12 = distance(lat1, lon1, lat2, lon2)
        d23 = distance(lat2, lon2, lat3, lon3)
        d31 = distance(lat3, lon3, lat1, lon1)

        perimeter = d12 + d23 + d31

        self._set_headers()
        self.wfile.write(json.dumps({'perimeter': perimeter}).encode('utf-8'))

if __name__ == "__main__":
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, TriangleHandler)
    print("Server running on http://localhost:5000")
    httpd.serve_forever()
