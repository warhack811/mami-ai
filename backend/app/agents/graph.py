from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.agents.nodes import AgentState, router_node, chat_node, coder_node, analyst_node
from app.tools.definitions import tools
import json
from langchain_core.messages import ToolMessage

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

def check_tool_output(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]

    # Check if it's a ToolMessage
    if isinstance(last_message, ToolMessage):
        content = last_message.content
        if "error" in content.lower() or "failed" in content.lower():
            # Increment retry
            retry_count = state.get("retry_count", 0) + 1
            state["retry_count"] = retry_count

            if retry_count < 3:
                return "coder" # Retry
            else:
                return END # Give up

    return "coder" # Normal loop back to agent to interpret result

# Edge from Tools back to Coder (with error check interception)
workflow.add_conditional_edges(
    "tools",
    check_tool_output,
    {
        "coder": "coder",
        END: END
    }
)

workflow.add_edge("chat", END)
workflow.add_edge("analyst", END)

# Compile the graph
app_graph = workflow.compile()
