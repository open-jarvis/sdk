"""
Copyright (c) 2021 Philipp Scheer
"""


import copy
import time
import json
import random
import asyncio
import traceback
import threading
import websocket
from threading import Thread


class Connection:
    _requests = {}

    def __init__(self, device_id: str, host: str = "jarvis.fipsi.at", port: int = 5522) -> None:
        self.id = device_id
        self._h = host
        self._p = port
        self._can_send = False
        self._ws = None
        self.on_open = None
        self.on_message = None
        self.on_close = None
        self._run()

    def request(self, endpoint: str, payload: dict = {}, callback = None) -> None:
        if self._can_send and self._ws is not None:
            id = ''.join(random.choice("abcdef0123456789") for i in range(64))
            self._ws.send(json.dumps({
                **payload,
                "$endpoint": endpoint,
                "$devid": self.id,
                "$reqid": id
            }))
            if callable(callback):
                Connection._requests[id] = callback

    def stream(self, endpoint: str) -> None:
        def _streaming_callback(data):
            self.request(endpoint, data)
        return _streaming_callback

    def _run(self):
        def ws_in_thread(loop):
            asyncio.set_event_loop(loop)
            async def _run_forever():
                self._ws = websocket.WebSocketApp(f"ws://{self._h}:{self._p}",
                                                    on_open=self._on_open,
                                                    on_message=self._on_message,
                                                    on_close=self._on_close)
                self._ws.run_forever()
            loop.run_until_complete(_run_forever())
        loop = asyncio.get_event_loop()
        t = threading.Thread(target=ws_in_thread, args=(loop,))
        t.start()

    def _on_open(self, ws):
        self._can_send = True
        if callable(self.on_open):
            self.on_open()

    def _on_message(self, ws, message):
        try:
            message = json.loads(message)
            id = message.get("$reqid", "")
            cb = Connection._requests.get(id, None)
            if callable(cb):
                cb(message)
        except Exception:
            traceback.print_exc()
        if callable(self.on_message):
            self.on_message(message)

    def _on_close(self, ws, close_status_code, status_text):
        self._can_send = False
        if callable(self.on_close):
            self.on_close(close_status_code)


class Highway:
    _callbacks = []

    def __init__(self) -> None:
        pass

    @staticmethod
    def on(lane: str, callback) -> None:
        Highway._callbacks.append({
            "lane": lane,
            "callback": callback
        })
    
    @staticmethod
    def send(lane: str, data: any = True) -> None:
        for cb in Highway._callbacks:
            if cb["lane"] == lane and callable(cb["callback"]):
                cb["callback"](data)
