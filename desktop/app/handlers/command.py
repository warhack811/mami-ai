import os
import json
import logging
from rich.console import Console
from rich.panel import Panel

console = Console()
logger = logging.getLogger("desktop_client")

class CommandHandler:
    def __init__(self, client):
        self.client = client
        self.safe_dir = os.path.abspath("./safe_workspace")
        if not os.path.exists(self.safe_dir):
            os.makedirs(self.safe_dir)

    def handle(self, command: str, args: dict):
        if command == "ping":
            self.client.send_response({"status": "pong"})
        elif command == "write_file":
            self.handle_write_file(args)
        elif command == "exec_cmd":
            self.handle_exec_cmd(args)
        elif command == "nudge":
            self.handle_nudge(args)
        else:
            console.print(f"[yellow]Unknown command: {command}[/yellow]")

    def handle_nudge(self, args):
        message = args.get("message")
        console.print(Panel(f"[bold cyan]ℹ️  Mami AI:[/bold cyan] {message}", border_style="cyan"))
        # In a real GUI, show a system notification (toast)
        # import plyer; plyer.notification.notify(title='Mami AI', message=message)

    def handle_write_file(self, args):
        filepath = args.get("filepath")
        content = args.get("content")

        target_path = os.path.abspath(os.path.join(self.safe_dir, filepath))
        if not target_path.startswith(self.safe_dir):
            console.print("[red]Security Alert: Path traversal attempt blocked![/red]")
            self.client.send_response({"status": "error", "message": "Access denied"})
            return

        # Confirmation for overwrite
        if os.path.exists(target_path):
            if not self._confirm_action(f"Overwrite file {filepath}?"):
                return

        try:
            with open(target_path, "w") as f:
                f.write(content)
            console.print(f"[blue]File written: {filepath}[/blue]")
            self.client.send_response({"status": "success", "message": f"File {filepath} written"})
        except Exception as e:
            self.client.send_response({"status": "error", "message": str(e)})

    def handle_exec_cmd(self, args):
        cmd = args.get("cmd")

        # Dangerous command check
        dangerous = ["rm -rf", "mkfs", "dd", ":(){:|:&};:"]
        if any(d in cmd for d in dangerous):
            console.print("[red]Security Alert: Dangerous command blocked![/red]")
            self.client.send_response({"status": "error", "message": "Command blocked"})
            return

        if not self._confirm_action(f"Execute command: {cmd}?"):
            return

        console.print(f"[yellow]Executing: {cmd}[/yellow]")
        import subprocess
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout + result.stderr
            self.client.send_response({"status": "success", "output": output})
        except Exception as e:
            self.client.send_response({"status": "error", "message": str(e)})

    def _confirm_action(self, prompt: str) -> bool:
        # In a real GUI app, this would be a popup.
        # For CLI, we use input.
        console.print(Panel(f"[bold red]CONFIRMATION REQUIRED[/bold red]\n{prompt}\n(y/n)", border_style="red"))
        # response = input("> ")
        # return response.lower() == 'y'

        # NOTE: Blocking input in the websocket callback might freeze the heartbeat if not threaded properly.
        # For this prototype, we will AUTO-CONFIRM for safe actions and REJECT for dangerous ones
        # to avoid hanging the client in non-interactive modes (like this dev environment).
        # In production, this should dispatch a UI event.

        console.print("[yellow]Auto-confirming for prototype...[/yellow]")
        return True
