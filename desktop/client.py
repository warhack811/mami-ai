import os
import json
import websocket
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "ws://localhost:8000/api/v1/chat/ws/desktop")
CLIENT_ID = os.getenv("CLIENT_ID", "desktop_client_01")
SECRET_KEY = os.getenv("DESKTOP_CLIENT_SECRET", "change_this_shared_secret")

console = Console()

class DesktopClient:
    def __init__(self):
        self.ws_url = f"{SERVER_URL}/{CLIENT_ID}"
        self.ws = None
        self.reconnect_delay = 5

    def on_message(self, ws, message):
        console.print(Panel(f"Received: {message}", title="Server Message", border_style="green"))
        try:
            data = json.loads(message)
            command = data.get("command")
            args = data.get("args", {})

            if command == "ping":
                self.send_response({"status": "pong"})
            elif command == "write_file":
                self.handle_write_file(args)
            elif command == "exec_cmd":
                self.handle_exec_cmd(args)
            else:
                console.print(f"[yellow]Unknown command: {command}[/yellow]")
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON received[/red]")

    def on_error(self, ws, error):
        console.print(f"[red]Error: {error}[/red]")

    def on_close(self, ws, close_status_code, close_msg):
        console.print("[red]### Connection Closed ###[/red]")

    def on_open(self, ws):
        console.print("[green]### Connected to Mami AI Server ###[/green]")
        # Send auth/handshake
        auth_payload = {"type": "auth", "secret": SECRET_KEY}
        ws.send(json.dumps(auth_payload))

    def send_response(self, data):
        if self.ws:
            self.ws.send(json.dumps(data))

    def handle_write_file(self, args):
        filepath = args.get("filepath")
        content = args.get("content")

        # Security: Prevent Path Traversal
        safe_dir = os.path.abspath("./safe_workspace")
        if not os.path.exists(safe_dir):
            os.makedirs(safe_dir)

        target_path = os.path.abspath(os.path.join(safe_dir, filepath))
        if not target_path.startswith(safe_dir):
            console.print("[red]Security Alert: Path traversal attempt blocked![/red]")
            self.send_response({"status": "error", "message": "Access denied"})
            return

        try:
            with open(target_path, "w") as f:
                f.write(content)
            console.print(f"[blue]File written: {filepath}[/blue]")
            self.send_response({"status": "success", "message": f"File {filepath} written"})
        except Exception as e:
            self.send_response({"status": "error", "message": str(e)})

    def handle_exec_cmd(self, args):
        cmd = args.get("cmd")

        # Security: Blacklist dangerous commands
        dangerous = ["rm -rf", "mkfs", "dd", ":(){:|:&};:"]
        if any(d in cmd for d in dangerous):
            console.print("[red]Security Alert: Dangerous command blocked![/red]")
            self.send_response({"status": "error", "message": "Command blocked"})
            return

        console.print(f"[yellow]Executing: {cmd}[/yellow]")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout + result.stderr
            self.send_response({"status": "success", "output": output})
        except Exception as e:
            self.send_response({"status": "error", "message": str(e)})

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

if __name__ == "__main__":
    client = DesktopClient()
    client.run()
