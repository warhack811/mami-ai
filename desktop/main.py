import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from desktop.app.core.client import DesktopClient

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "wss://localhost:8000/api/v1/chat/ws/desktop")
CLIENT_ID = os.getenv("CLIENT_ID", "desktop_client_01")
SECRET_KEY = os.getenv("DESKTOP_CLIENT_SECRET", "change_this_shared_secret")

def validate_url(url: str):
    """
    Ensures that the SERVER_URL uses a secure protocol (wss://).
    Allows ws:// only for local development (localhost or 127.0.0.1).
    """
    parsed = urlparse(url)
    if parsed.scheme == "ws":
        is_local = parsed.hostname in ("localhost", "127.0.0.1")
        if not is_local:
            raise ValueError(
                f"Insecure WebSocket (ws://) is not allowed for remote host: {parsed.hostname}. "
                "Please use wss:// for secure communication."
            )
    elif parsed.scheme != "wss":
        raise ValueError(f"Invalid WebSocket protocol '{parsed.scheme}'. Use wss:// or ws:// (local only).")

if __name__ == "__main__":
    validate_url(SERVER_URL)
    client = DesktopClient(SERVER_URL, CLIENT_ID, SECRET_KEY)
    client.run()
