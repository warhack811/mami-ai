from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from app.core.config import settings
from app.services.connection_manager import manager
import asyncio

# Initialize Serper Wrapper
search = GoogleSerperAPIWrapper(serper_api_key=settings.SERPER_API_KEY)

@tool
def web_search(query: str):
    """Search the web for current information, news, or technical documentation."""
    try:
        return search.run(query)
    except Exception as e:
        return f"Error searching web: {e}"

@tool
async def file_operation(action: str, filepath: str, content: str = ""):
    """
    Perform a file operation on the user's desktop via the secure client.
    actions: 'write_file', 'exec_cmd' (mapped from 'write', 'execute')
    """
    # Map high-level intent to protocol commands
    command = "write_file" if action == "write" else "exec_cmd"
    if action == "write":
        args = {"filepath": filepath, "content": content}
    else:
        # Assuming filepath is cmd for exec
        args = {"cmd": filepath} # Lazy mapping for prototype
        command = "exec_cmd"

    # Send to specific client (Hardcoded ID for prototype, ideally passed in context)
    client_id = "desktop_client_01"

    result = await manager.send_command(client_id, command, args)
    return f"Desktop Response: {result}"

tools = [web_search, file_operation]
