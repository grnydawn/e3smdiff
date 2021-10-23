
from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys, threading, webbrowser, time
from e3smdiff.html import index
from e3smdiff.js import resizable as rejs
from e3smdiff.css import resizable as recss

_cache = {}

class handler(BaseHTTPRequestHandler):

    def get_path(self, path):

        if path == "/":
            _cache[path] = (index, "text/html")

    def get_js(self, path):

        if path == "/resizable.js":
            _cache[path] = (rejs, "application/javascript")

    def get_css(self, path):

        if path == "/resizable-style.css":
            _cache[path] = (recss, "text/css")

    def do_GET(self):

        root, ext = os.path.splitext(self.path)

        if ext == "":
            self.get_path(self.path)

        elif ext == ".html":
            self.get_html(self.path)

        elif ext == ".js":
            self.get_js(self.path)

        elif ext == ".css":
            self.get_css(self.path)

        msg, ctype = _cache.get(self.path, (None, None))

        if msg and ctype:
            self.send_response(200)
            self.send_header('Content-type',ctype)
        else:
            self.send_response(404)
            msg = "404 Not Found"

        self.end_headers()

        #import pdb; pdb.set_trace()

        self.wfile.write(bytes(msg, "utf8"))

    def do_POST(self):
        import pdb; pdb.set_trace()

        
def start_server():

    with HTTPServer(('', 8000), handler) as server:
        server.serve_forever()

def main():
    x = threading.Thread(target=start_server, args=tuple())
    x.start()
    url = 'http://127.0.0.1:8000'
    webbrowser.open_new(url)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
