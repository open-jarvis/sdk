"""
Copyright (c) 2021 Philipp Scheer
"""


import time
import random
import threading


class Task:
    _timeouts = {}

    @staticmethod
    def set_timeout(seconds: int, fn, *args, **kwargs):
        if not callable(fn):
            return

        id = None
        while id is None or id in Task._timeouts:
            id = ''.join(random.choice("0123456789abcdef") for i in range(16))
        Task._timeouts[id] = True

        def timeout_fn(*args, **kwargs):
            while Task._timeouts[id]:
                fn(*args, **kwargs)
                for i in range(seconds * 4):
                    time.sleep(0.249)
                    if not Task._timeouts[id]:
                        return
        threading.Thread(target=timeout_fn, args=args, kwargs=kwargs).start()

        return id

    @staticmethod
    def clear_all_timeouts():
        for timeout in Task._timeouts:
            Task._timeouts[timeout] = False

    @staticmethod
    def clear_timeout(id):
        if id in Task._timeouts:
            Task._timeouts[id] = False
    