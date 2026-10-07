import http.server
import socketserver
import json
import urllib.parse
import os
import sys

PORT = 8765
STATE_FILE = "C:/Users/User/presentation-digital-marketing/state.json"

if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_slide": 1}, f)

def get_current_slide():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("current_slide", 1)
    except Exception:
        return 1

def set_current_slide(idx):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_slide": idx}, f)

import slides_data
TOTAL_SLIDES = len(slides_data.slides)

class SlideHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        if path == "/api/status":
            current = get_current_slide()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            resp = {
                "current_slide": current,
                "total_slides": TOTAL_SLIDES,
                "slide_data": slides_data.slides[current - 1]
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if path == "/api/slides":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(slides_data.slides).encode("utf-8"))
            return

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("C:/Users/User/presentation-digital-marketing/index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        return super().do_GET()

    def do_POST(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        if path == "/api/next":
            cur = get_current_slide()
            if cur < TOTAL_SLIDES:
                cur += 1
                set_current_slide(cur)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "current_slide": cur}).encode("utf-8"))
            return

        if path == "/api/prev":
            cur = get_current_slide()
            if cur > 1:
                cur -= 1
                set_current_slide(cur)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "current_slide": cur}).encode("utf-8"))
            return

        if path == "/api/goto":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                target = int(data.get("slide", 1))
                if 1 <= target <= TOTAL_SLIDES:
                    set_current_slide(target)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "current_slide": get_current_slide()}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    os.chdir("C:/Users/User/presentation-digital-marketing")
    with ReusableTCPServer(("0.0.0.0", PORT), SlideHandler) as httpd:
        print(f"Server started on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
