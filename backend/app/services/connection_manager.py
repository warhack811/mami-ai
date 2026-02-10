from typing import List, Optional
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.pending_commands: dict[str, asyncio.Future] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client {client_id} disconnected")
        if client_id in self.pending_commands:
            del self.pending_commands[client_id]

    async def send_command(self, client_id: str, command: str, args: dict, timeout: int = 10):
        if client_id not in self.active_connections:
            return {"status": "error", "message": "Client not connected"}

        # Create a unique command ID (simple correlation via future)
        future = asyncio.get_event_loop().create_future()
        self.pending_commands[client_id] = future

        try:
            await self.active_connections[client_id].send_json({"command": command, "args": args})
            print(f"Sent command to {client_id}: {command}")
            result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Command timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            if client_id in self.pending_commands:
                del self.pending_commands[client_id]

    def handle_response(self, client_id: str, data: dict):
        print(f"Handling response from {client_id}: {data}")
        if client_id in self.pending_commands:
            future = self.pending_commands[client_id]
            if not future.done():
                future.set_result(data)

manager = ConnectionManager()
