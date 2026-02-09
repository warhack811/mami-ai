from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.agents.nodes import AgentState, router_node, chat_node, coder_node, analyst_node
from app.tools.definitions import tools

# Create Tool Node
tool_node = ToolNode(tools)

# Define the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("chat", chat_node)
workflow.add_node("coder", coder_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("tools", tool_node)

# Add edges
workflow.set_entry_point("router")

def route_decision(state: AgentState):
    return state["next_step"]

workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "chat": "chat",
        "coder": "coder",
        "analyst": "analyst"
    }
)

def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    # If the last message has tool calls, route to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

workflow.add_conditional_edges(
    "coder",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

# Loop back from tools to the agent that called them (coder)
workflow.add_edge("tools", "coder")

workflow.add_edge("chat", END)
workflow.add_edge("analyst", END)

# Compile the graph
app_graph = workflow.compile()
