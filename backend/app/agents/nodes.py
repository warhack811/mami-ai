from typing import Annotated, Literal, TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings, get_system_setting
from app.services.vector_store import vector_store
from app.graph.client import neo4j_client
from app.tools.definitions import tools
from app.db.session import SessionLocal

# Define the state of the graph
class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_id: int
    next_step: str
    context: str
    retry_count: int

# Initialize Models Dynamically
def get_llm(model_key: str, default_model: str, api_key: str = None):
    # Fetch from DB Settings
    db = SessionLocal()
    model_name = get_system_setting(db, model_key, default_model)
    db.close()

    # We assume Groq for simplicity, but logic could switch provider based on model name
    return ChatGroq(model=model_name, api_key=api_key or settings.GROQ_API_KEY)

# Helper function for context retrieval (Existing)
def retrieve_context(user_id: int, query: str) -> str:
    try:
        # Vector Search
        vector_results = vector_store.query(str(user_id), query)
        vector_context = "\n".join([doc for sublist in vector_results.get('documents', []) for doc in sublist])

        # Graph Search
        graph_query = """
        MATCH (u:User {id: $uid})-[:KNOWS]->(e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($query) OR toLower(e.type) CONTAINS toLower($query)
        RETURN e.name as entity, e.description as description LIMIT 5
        """
        graph_data = neo4j_client.query(graph_query, {"uid": user_id, "query": query})
        graph_context = "\n".join([f"{record.get('entity')}: {record.get('description', '')}" for record in graph_data])

        return f"Vector Memory:\n{vector_context}\n\nGraph Memory:\n{graph_context}"
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ""

# Router Agent
def router_node(state: AgentState):
    messages = state['messages']
    last_message = messages[-1].content
    user_id = state['user_id']

    # Retrieve Context
    context = retrieve_context(user_id, last_message)
    state['context'] = context
    state['retry_count'] = 0 # Reset retry count

    if "code" in last_message.lower() or "file" in last_message.lower() or "search" in last_message.lower():
        return {"next_step": "coder", "context": context}
    elif "analyze" in last_message.lower():
        return {"next_step": "analyst", "context": context}
    else:
        return {"next_step": "chat", "context": context}

# Chat Agent
def chat_node(state: AgentState):
    messages = state['messages']
    context = state.get('context', '')

    # Dynamic Model Loading
    llm = get_llm("AI_MODEL_CHAT", "gemini-1.5-flash", settings.GEMINI_API_KEY) # Use Gemini client if available
    # Using Groq fallback for uniform interface in this prototype if Gemini fails setup
    # But let's assume we use ChatGoogleGenerativeAI if key is present
    if settings.GEMINI_API_KEY:
         llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)

    system_prompt = SystemMessage(content=f"""You are Mami AI, a helpful and friendly personal assistant.
    Use the following context to personalize your response:
    {context}
    """)

    response = llm.invoke([system_prompt] + messages)
    return {"messages": [response]}

# Coder Agent (Now with Self-Healing!)
def coder_node(state: AgentState):
    messages = state['messages']
    context = state.get('context', '')
    retry_count = state.get('retry_count', 0)

    # Dynamic Model Loading
    llm = get_llm("AI_MODEL_CODER", "llama-3.1-70b-versatile")
    llm_with_tools = llm.bind_tools(tools)

    system_prompt_content = f"""You are a senior software engineer and autonomous agent.
    You have access to tools: web_search, file_operation.
    Use them when necessary.
    Context:
    {context}
    """

    if retry_count > 0:
        system_prompt_content += f"\nWARNING: You failed previously. Analyze the last tool output error and fix your approach. Retry count: {retry_count}"

    system_prompt = SystemMessage(content=system_prompt_content)

    response = llm_with_tools.invoke([system_prompt] + messages)
    return {"messages": [response]}

# Analyst Agent
def analyst_node(state: AgentState):
    messages = state['messages']
    response = AIMessage(content="Analyst agent processing... (Placeholder for now)")
    return {"messages": [response]}
