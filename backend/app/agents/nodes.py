from typing import Annotated, Literal, TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.services.vector_store import vector_store
from app.graph.client import neo4j_client
from app.tools.definitions import tools

# Define the state of the graph
class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_id: int
    next_step: str
    context: str

# Initialize Models with Tool Binding
llm_router = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)
llm_coder = ChatGroq(model="llama-3.1-70b-versatile", api_key=settings.GROQ_API_KEY)
llm_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)

# Bind tools to the coder agent (and potentially router if it decides to search directly)
llm_coder_with_tools = llm_coder.bind_tools(tools)

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
        # Simple keyword match on graph
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

    # Enhanced Routing Logic (could use LLM here too)
    system_prompt = SystemMessage(content="You are a routing agent. Decide if the user needs a Coder (for technical tasks, file ops), an Analyst (for deep reasoning, reports), or just a Chat.")
    # For speed, we stick to heuristic + lightweight LLM check if needed.

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

    system_prompt = SystemMessage(content=f"""You are Mami AI, a helpful and friendly personal assistant.
    Use the following context to personalize your response:
    {context}
    """)

    response = llm_chat.invoke([system_prompt] + messages)
    return {"messages": [response]}

# Coder Agent (Now with Tools!)
def coder_node(state: AgentState):
    messages = state['messages']
    context = state.get('context', '')

    system_prompt = SystemMessage(content=f"""You are a senior software engineer and autonomous agent.
    You have access to tools: web_search, file_operation.
    Use them when necessary.
    Context:
    {context}
    """)

    # We invoke the model bound with tools
    response = llm_coder_with_tools.invoke([system_prompt] + messages)
    return {"messages": [response]}

# Analyst Agent
def analyst_node(state: AgentState):
    messages = state['messages']
    response = AIMessage(content="Analyst agent processing... (Placeholder for now)")
    return {"messages": [response]}
