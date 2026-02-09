from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from app.core.config import settings

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
def file_operation(action: str, filepath: str, content: str = ""):
    """
    Perform a file operation on the user's desktop via the secure client.
    actions: 'read', 'write', 'delete' (requires confirmation)
    """
    # In a real implementation, this would send a WebSocket message to the connected client.
    # For now, we simulate the instruction which the Agent will emit.
    return f"Desktop Action Request: {action} on {filepath}"

tools = [web_search, file_operation]
