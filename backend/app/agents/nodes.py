from typing import Annotated, Literal, TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.services.vector_store import vector_store
from app.graph.client import neo4j_client

# Define the state of the graph
class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_id: int
    next_step: str
    context: str

# Initialize Models
llm_router = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)
llm_coder = ChatGroq(model="llama-3.1-70b-versatile", api_key=settings.GROQ_API_KEY)
llm_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)

# Helper function for context retrieval
def retrieve_context(user_id: int, query: str) -> str:
    try:
        # Vector Search
        vector_results = vector_store.query(str(user_id), query)
        vector_context = "\n".join([doc for sublist in vector_results.get('documents', []) for doc in sublist])

        # Graph Search (Simple keyword match or entity extraction could be better)
        # Here we just fetch recent interactions or relevant entities if we had entity extraction
        graph_query = """
        MATCH (u:User {id: $uid})-[:KNOWS]->(e:Entity)
        RETURN e.name as entity, e.description as description LIMIT 5
        """
        graph_data = neo4j_client.query(graph_query, {"uid": user_id})
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

    # Simple keyword based routing
    if "code" in last_message.lower() or "function" in last_message.lower() or "script" in last_message.lower():
        return {"next_step": "coder", "context": context}
    elif "analyze" in last_message.lower() or "report" in last_message.lower():
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

# Coder Agent
def coder_node(state: AgentState):
    messages = state['messages']
    context = state.get('context', '')

    system_prompt = SystemMessage(content=f"""You are a senior software engineer. Write clean, efficient code.
    Use the following context if relevant:
    {context}
    """)

    response = llm_coder.invoke([system_prompt] + messages)
    return {"messages": [response]}

# Analyst Agent
def analyst_node(state: AgentState):
    messages = state['messages']
    response = AIMessage(content="Analyst agent processing... (Placeholder)")
    return {"messages": [response]}
