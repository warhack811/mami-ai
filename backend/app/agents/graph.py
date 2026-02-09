from langgraph.graph import StateGraph, END
from app.agents.nodes import AgentState, router_node, chat_node, coder_node, analyst_node

# Define the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("chat", chat_node)
workflow.add_node("coder", coder_node)
workflow.add_node("analyst", analyst_node)

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

workflow.add_edge("chat", END)
workflow.add_edge("coder", END)
workflow.add_edge("analyst", END)

# Compile the graph
app_graph = workflow.compile()
