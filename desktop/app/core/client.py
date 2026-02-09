import os
import json
import time
import websocket
import logging
from rich.console import Console
from rich.panel import Panel
from desktop.app.handlers.command import CommandHandler

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("desktop_client")

class DesktopClient:
    def __init__(self, server_url, client_id, secret_key):
        self.ws_url = f"{server_url}/{client_id}"
        self.secret_key = secret_key
        self.ws = None
        self.reconnect_delay = 5
        self.handler = CommandHandler(self)

    def on_message(self, ws, message):
        console.print(Panel(f"Received: {message}", title="Server Message", border_style="green"))
        try:
            data = json.loads(message)
            command = data.get("command")
            args = data.get("args", {})
            self.handler.handle(command, args)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON received[/red]")

    def on_error(self, ws, error):
        console.print(f"[red]Error: {error}[/red]")

    def on_close(self, ws, close_status_code, close_msg):
        console.print("[red]### Connection Closed ###[/red]")

    def on_open(self, ws):
        console.print("[green]### Connected to Mami AI Server ###[/green]")
        auth_payload = {"type": "auth", "secret": self.secret_key}
        ws.send(json.dumps(auth_payload))

    def send_response(self, data):
        if self.ws:
            self.ws.send(json.dumps(data))

    def run(self):
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                self.ws.run_forever()
            except Exception as e:
                console.print(f"[red]Connection failed: {e}[/red]")

            console.print(f"Reconnecting in {self.reconnect_delay} seconds...")
            time.sleep(self.reconnect_delay)
