import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.agents.nodes import router_node, AgentState
from langchain_core.messages import HumanMessage
from app.services.sentiment import SentimentResult

# Mock dependencies
@pytest.fixture
def mock_retrieve_context():
    with patch("app.agents.nodes.retrieve_context") as mock:
        mock.return_value = "Mocked Context"
        yield mock

@pytest.fixture
def mock_analyze_sentiment():
    with patch("app.agents.nodes.analyze_sentiment", new_callable=AsyncMock) as mock:
        mock.return_value = SentimentResult(mood="Neutral", urgency="Low", suggested_tone="Helpful")
        yield mock

@pytest.mark.asyncio
async def test_router_code_keyword(mock_retrieve_context, mock_analyze_sentiment):
    state: AgentState = {
        "messages": [HumanMessage(content="Can you write some python code for me?")],
        "user_id": 1,
        "next_step": "",
        "context": "",
        "retry_count": 0,
        "sentiment": {}
    }

    result = await router_node(state)
    assert result["next_step"] == "coder"
    assert result["context"] == "Mocked Context"

@pytest.mark.asyncio
async def test_router_file_keyword(mock_retrieve_context, mock_analyze_sentiment):
    state: AgentState = {
        "messages": [HumanMessage(content="Please read this file.")],
        "user_id": 1,
        "next_step": "",
        "context": "",
        "retry_count": 0,
        "sentiment": {}
    }

    result = await router_node(state)
    assert result["next_step"] == "coder"

@pytest.mark.asyncio
async def test_router_search_keyword(mock_retrieve_context, mock_analyze_sentiment):
    state: AgentState = {
        "messages": [HumanMessage(content="Search for the latest news.")],
        "user_id": 1,
        "next_step": "",
        "context": "",
        "retry_count": 0,
        "sentiment": {}
    }

    result = await router_node(state)
    assert result["next_step"] == "coder"

@pytest.mark.asyncio
async def test_router_analyze_keyword(mock_retrieve_context, mock_analyze_sentiment):
    state: AgentState = {
        "messages": [HumanMessage(content="Analyze the results.")],
        "user_id": 1,
        "next_step": "",
        "context": "",
        "retry_count": 0,
        "sentiment": {}
    }

    result = await router_node(state)
    assert result["next_step"] == "analyst"

@pytest.mark.asyncio
async def test_router_chat_keyword(mock_retrieve_context, mock_analyze_sentiment):
    state: AgentState = {
        "messages": [HumanMessage(content="Hello, how are you today?")],
        "user_id": 1,
        "next_step": "",
        "context": "",
        "retry_count": 0,
        "sentiment": {}
    }

    result = await router_node(state)
    assert result["next_step"] == "chat"

@pytest.mark.asyncio
async def test_router_mixed_keywords_priority(mock_retrieve_context, mock_analyze_sentiment):
    # "code" keyword has priority over "analyze" based on current implementation
    state: AgentState = {
        "messages": [HumanMessage(content="Analyze this code snippet.")],
        "user_id": 1,
        "next_step": "",
        "context": "",
        "retry_count": 0,
        "sentiment": {}
    }

    result = await router_node(state)
    assert result["next_step"] == "coder"

@pytest.mark.asyncio
async def test_router_mixed_file_analyze(mock_retrieve_context, mock_analyze_sentiment):
    # "file" keyword has priority over "analyze"
    state: AgentState = {
        "messages": [HumanMessage(content="Please analyze this file.")],
        "user_id": 1,
        "next_step": "",
        "context": "",
        "retry_count": 0,
        "sentiment": {}
    }

    result = await router_node(state)
    assert result["next_step"] == "coder"
