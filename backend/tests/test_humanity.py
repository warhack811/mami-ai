import pytest
from app.services.sentiment import analyze_sentiment
from app.models.goal import Goal
from app.services.memory import consolidate_memory_task
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_sentiment_analysis():
    # We patch the 'chain' object in the module directly
    with patch("app.services.sentiment.chain") as mock_chain:
        # Mocking async method requires AsyncMock or setting side_effect to async func
        mock_chain.ainvoke = AsyncMock(return_value={
            "mood": "Angry",
            "urgency": "High",
            "suggested_tone": "Apologetic and Quick"
        })

        result = await analyze_sentiment("I am furious right now! Fix this immediately!")
        assert result.mood == "Angry"
        assert result.urgency == "High"

@patch("app.services.memory.neo4j_client")
@patch("app.services.memory.SessionLocal")
@patch("app.services.memory.chain")
def test_goal_extraction(mock_chain, mock_session, mock_neo4j):
    # Mock LLM Output
    mock_chain.invoke.return_value = {
        "entities": [],
        "relations": [],
        "goals": [{
            "title": "Finish Project",
            "description": "Complete the Mami AI backend",
            "due_date_str": "2024-12-31"
        }]
    }

    # Mock DB
    mock_db = MagicMock()
    mock_session.return_value = mock_db

    consolidate_memory_task(1, "I need to Finish Project by 2024-12-31.")

    # Verify Goal Save
    mock_db.add.assert_called_once()
    args, _ = mock_db.add.call_args
    saved_goal = args[0]
    assert isinstance(saved_goal, Goal)
    assert saved_goal.title == "Finish Project"
