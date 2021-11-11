"""
Copyright (c) 2021 Philipp Scheer
"""


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