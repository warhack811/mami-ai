import os
from dotenv import load_dotenv
from desktop.app.core.client import DesktopClient

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "ws://localhost:8000/api/v1/chat/ws/desktop")
CLIENT_ID = os.getenv("CLIENT_ID", "desktop_client_01")
SECRET_KEY = os.getenv("DESKTOP_CLIENT_SECRET", "change_this_shared_secret")

if __name__ == "__main__":
    client = DesktopClient(SERVER_URL, CLIENT_ID, SECRET_KEY)
    client.run()
