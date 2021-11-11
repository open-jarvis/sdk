"""
Copyright (c) 2021 Philipp Scheer
"""


import json
import datetime

from jarvis_sdk import Logger

from http.server import HTTPServer, SimpleHTTPRequestHandler


class Router:
    routes = {}
    
    @staticmethod
    def on(route: str, **kwargs):
        def decor(func):
            def wrap(*args, **kwargs):
                res = func(*args, **kwargs)
                return res
            Router.routes[route] = {
                "fn": wrap,
                "kwargs": kwargs
            }
            return wrap
        return decor

    @staticmethod
    def execute(route: str, default_value=None):
        try:
            if route in Router.routes:
                return Router.routes[route]["fn"](**Router.routes[route]["kwargs"])
        except:
            pass
        return default_value


class PluginServerHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print("%s %s %s" % (datetime.datetime.now(), self.client_address[0], format%args))

    def do_GET(self):
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"success": False, "error": "GET parameter not supported. Use POST instead"}).encode("utf-8"))
        self.wfile.flush()

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        res = Router.execute(self.path[1:], None)
        rsp = { "success": False }

        if res is None:				rsp = { "success": False }
        elif isinstance(res, bool):	rsp = { "success": res }
        else:						rsp = { "success": True, "result": res }

        self.wfile.write(json.dumps(rsp).encode("utf-8"))
        self.wfile.flush()


class PluginServer:
    running = True
    logger: Logger = None

    def __init__(self, port, logger: Logger) -> None:
        self.httpd = HTTPServer(("localhost", port), PluginServerHandler)
        self.logger = logger
        PluginServer.logger = logger

    def handle_one_request(self):
        self.httpd.handle_request()

    def handle_requests(self):
        while PluginServer.running:
            self.handle_one_request()

    def stop(self):
        self.logger.info("Stopping PluginServer")
        PluginServer.running = False


@Router.on("logs")
def on_logs():
    if PluginServer.logger:
        with open(PluginServer.logger.f.name, "r") as f:
            return f.readlines()
    return None

@Router.on("stop")
def on_stop():
    PluginServer.running = False
