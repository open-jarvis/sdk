"""
Copyright (c) 2021 Philipp Scheer
"""


import json
import random
import traceback
import threading
import websocket


class Connection:
    _requests = {}

    def __init__(self, device_id: str, host: str = "jarvis.fipsi.at", port: int = 5522, debug: bool = False) -> None:
        self.id = device_id
        self._h = host
        self._p = port
        self._can_send = False
        self._ws = None
        self.on_control_message = None
        self.on_open = None
        self.on_message = None
        self.on_close = None
        self.debug = debug
        self.loop = None
        self._run()

    def request(self, endpoint: str, payload: dict = {}, callback = None) -> None:
        if self._can_send and self._ws is not None:
            id = ''.join(random.choice("abcdef0123456789") for i in range(64))
            data = json.dumps({
                **payload,
                "$endpoint": endpoint,
                "$devid": self.id,
                "$reqid": id
            })
            if self.debug:
                print(">", data)
            self._ws.send(data)
            if callable(callback):
                Connection._requests[id] = callback

    def stream(self, endpoint: str) -> None:
        def _streaming_callback(data):
            self.request(endpoint, data)
        return _streaming_callback

    def _run(self):
        self._ws = websocket.WebSocketApp(f"ws://{self._h}:{self._p}",
                                            on_open=self._on_open,
                                            on_message=self._on_message,
                                            on_close=self._on_close)
        self._ws.keep_running = True
        t = threading.Thread(target=self._ws.run_forever)
        t.daemon = True
        t.start()

    def reconnect(self, cb=None):
        if self._ws:
            self._ws.keep_running = False
        self._run()
        self.on_open = cb

    def disconnect(self):
        if self._ws:
            self._ws.keep_running = False

    def _on_open(self, ws):
        self._can_send = True
        if callable(self.on_open):
            self.on_open()

    def _on_message(self, ws, message):
        if self.debug:
            print("<", message)
        try:
            message = json.loads(message)
            print(message)
            if message.get("$control", None):
                if callable(self.on_control_message):
                    self.on_control_message(message)
                return
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
