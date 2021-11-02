
import os, sys, threading, webbrowser, time, json, urllib, tempfile, shutil

from http.server import BaseHTTPRequestHandler, HTTPServer
from e3smdiff.html import index
from e3smdiff.js import resizable as rejs, tree as treejs, diff_table as diffjs
from e3smdiff.css import resizable as recss, tree as treecss, diff_table as diffcss
from e3smdiff.builders import Vimdiff 

_globals = {"default_builder": Vimdiff}
_cache = {}

jstype = "application/javascript"
jsontype = "application/json"
htmltype = "text/html"
csstype = "text/css"

_pathmap = {
}

_extmap = {
}

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

    def gen_default(self, left, right, use_left=True):
        lpath = os.path.join(_globals["cases"][0], *left)
        rpath = os.path.join(_globals["cases"][1], *right)

        if use_left:
            pathid = os.sep.join(left)

        else:
            pathid = os.sep.join(right)

        if pathid in _pathmap:
            import pdb; pdb.set_trace()

        else:
            diff = _globals["default_builder"](lpath, rpath, workdir=_globals["tempdir"])
            data, ctype = diff.get_data()

        return (data, ctype)

    def gen_diff(self, left, right):
        # data, type

        lbase, lext = os.path.splitext(left[-1])
        rbase, rext = os.path.splitext(right[-1])

        if lbase:
            if rbase:
                # both
                if len(left) == len(right) and all(l==r for l, r in zip(left[1:], right[1:])):
                    # matched ext
                    if lext:
                        # matched ext
                        if lext in _extmap:
                            import pdb; pdb.set_trace()

                        else:
                            return self.gen_default(left[1:], right[1:])

                    else:
                        # no ext
                        return self.gen_default(left[1:], right[1:])
                else:
                    # not matched
                    return self.gen_default(left[1:], right[1:])
            else:
                # left only
                return self.gen_default(left[1:], right[1:])
        elif rbase:
            # right only
            return self.gen_default(left[1:], right[1:])

        else:
            # not of them
            import pdb; pdb.set_trace()

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

        elif path.startswith("/diff"):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            leftpath = query.get("LEFT", [""])[0].split(" - ")
            rightpath = query.get("RIGHT", [""])[0].split(" - ")
            diffdata, ctype = self.gen_diff(leftpath, rightpath)
            _cache[path] = (json.dumps(diffdata), ctype)


    def get_js(self, path):

        if path == "/resizable.js":
            _cache[path] = (rejs, jstype)

        elif path == "/tree.js":
            _cache[path] = (treejs, jstype)

        elif path == "/difftable.js":
            _cache[path] = (diffjs, csstype)

    def get_css(self, path):

        if path == "/resizable-style.css":
            _cache[path] = (recss, csstype)

        elif path == "/tree.css":
            _cache[path] = (treecss, csstype)

        elif path == "/difftable.css":
            _cache[path] = (diffcss, csstype)

    def do_GET(self):

        root, ext = os.path.splitext(self.path)

        if ext == ".html":
            self.get_html(self.path)

        elif ext == ".js":
            self.get_js(self.path)

        elif ext == ".css":
            self.get_css(self.path)

        else:        
            self.get_path(self.path)

        msg, ctype = _cache.get(self.path, (None, None))

        if msg and ctype:
            self.send_response(200)

        else:
            self.send_response(404)
            msg, ctype = "404 Not Found", htmltype
            #import pdb; pdb.set_trace()

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

    tempdir = tempfile.mkdtemp()
    _globals["tempdir"] = tempdir

    x = threading.Thread(target=start_server, args=tuple())
    x.start()
    url = 'http://127.0.0.1:8000'
    webbrowser.open_new(url)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            shutil.rmtree(tempdir)
            sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
