import websocket

class BLEWebSocketClient:
    def __init__(self, uri, on_message_callback):
        self.uri = uri
        self.on_message_callback = on_message_callback

    def start(self):
        def on_message(ws, message):
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            if not isinstance(message, str):
                print("[WebSocket] Error: Must be string, not", type(message))
                return

            msg = str(message).strip()
            print(f"[WebSocket] Received: {msg}")
            self.on_message_callback(msg)

        def on_error(ws, error):
            print("[WebSocket] Error:", error)

        def on_close(ws, code, msg):
            print("[WebSocket] Closed")

        def on_open(ws):
            print("[WebSocket] Connected")

        self.ws = websocket.WebSocketApp(
            self.uri,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        self.ws.run_forever()
