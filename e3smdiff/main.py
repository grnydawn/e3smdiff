
import os, sys, threading, webbrowser, time, json

from http.server import BaseHTTPRequestHandler, HTTPServer
from e3smdiff.html import index
from e3smdiff.js import resizable as rejs, tree as treejs
from e3smdiff.css import resizable as recss, tree as treecss

_globals = {}
_cache = {}

jstype = "application/javascript"
jsontype = "application/json"
htmltype = "text/html"
csstype = "text/css"

class handler(BaseHTTPRequestHandler):

    def path_to_dict(self, path):
        d = {'name': os.path.basename(path)}
        if os.path.isdir(path):
            d['type'] = "directory"
            d['children'] = [self.path_to_dict(os.path.join(path,x)) for x in
                             os.listdir (path)]
        else:
            d['type'] = "file"

        return d

    def get_path(self, path):

        if path == "/":
            _cache[path] = (index, htmltype)

        elif path == "/case1":
            if "cases" in _globals and len(_globals["cases"]) > 0:
                casepath = _globals["cases"][0]
                files = self.path_to_dict(casepath) 
                _cache[path] = (json.dumps(files), jsontype)

        elif path == "/case2":
            if "cases" in _globals and len(_globals["cases"]) > 0:
                casepath = _globals["cases"][1]
                files = self.path_to_dict(casepath) 
                _cache[path] = (json.dumps(files), jsontype)

    def get_js(self, path):

        if path == "/resizable.js":
            _cache[path] = (rejs, jstype)

        elif path == "/tree.js":
            _cache[path] = (treejs, jstype)

    def get_css(self, path):

        if path == "/resizable-style.css":
            _cache[path] = (recss, csstype)

        elif path == "/tree.css":
            _cache[path] = (treecss, csstype)

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

        else:
            self.send_response(404)
            msg, ctype = "404 Not Found", htmltype

        self.send_header('Content-type',ctype)

        self.end_headers()

        #import pdb; pdb.set_trace()

        if ctype in (htmltype, jstype, csstype, jsontype):
            self.wfile.write(bytes(msg, "utf8"))

        else:
            import pdb; pdb.set_trace()

    def do_POST(self):
        import pdb; pdb.set_trace()

        
def start_server():

    with HTTPServer(('', 8000), handler) as server:
        server.serve_forever()

def main():

    if len(sys.argv)< 3:
        print("Usage: e3smdiff case1 case2")
        return -1

    _globals["cases"] = sys.argv[1:3]

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
