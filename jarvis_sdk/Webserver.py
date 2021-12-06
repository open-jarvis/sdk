"""
Copyright (c) 2021 Philipp Scheer
"""


import os
import json
import mimetypes

from functools import wraps
from http.server import BaseHTTPRequestHandler, HTTPServer


class Router:
    def __init__(self) -> None:
        self.routes = []
    
    def on(self, route):
        def decorator(func):
            self.routes.append({
                "route": route,
                "callback": func
            })
        return decorator

    def execute(self, route, default, *args, **kwargs):
        for route_entry in self.routes:
            if route_entry.get("route") == route:
                return route_entry.get("callback", lambda: None)(*args, **kwargs)
        return default


class Server(BaseHTTPRequestHandler):
    router: Router = None
    basedir = "."

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")

    def do_GET(self):
        path = self.path[1:]
        data = self.rfile.read(int(self.headers['Content-Length'] or 0)).decode("utf-8")
        absolute = f"{Server.basedir}/{path}"
        if absolute.endswith("/"):
            absolute += "index.html"
        if os.path.isfile(absolute):
            try:
                with open(absolute, "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type", mimetypes.guess_type(absolute)[0])
                    self.end_headers()
                    self.wfile.write(f.read())
            except Exception:
                self.send_response(403)
                self.end_headers()
        else:
            out = Server.router.execute(path, None, data)
            if out is None:
                self.send_response(404)
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                try:
                    self.wfile.write(json.dumps(out).encode("utf-8"))
                except TypeError:
                    self.wfile.write(out)

    def do_POST(self):
        self.do_GET()


class Webserver:
    def __init__(self, bind="0.0.0.0", port=8080, root=".", router=None) -> None:
        assert isinstance(router, Router), "Router object required"
        self.bind = bind
        self.port = port
        self.root = root
        Server.router = router
        Server.basedir = self.root
        self.server = HTTPServer((bind, port), Server)
    
    def handle_one_request(self):
        self.server.handle_request()
    
    def serve_forever(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()
