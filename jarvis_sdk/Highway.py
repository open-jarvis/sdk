"""
Copyright (c) 2021 Philipp Scheer
"""


import traceback


class Highway:
    roads: list = []

    @staticmethod
    def on(route, callback):
        Highway.roads.append({ "r": route, "cb": callback })
    
    @staticmethod
    def push(route, data):
        for road in Highway.roads:
            if road["r"] == route:
                if callable(road["cb"]):
                    try:
                        road["cb"](data)
                    except Exception:
                        traceback.print_exc()
