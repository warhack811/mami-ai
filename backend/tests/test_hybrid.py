from unittest.mock import patch, MagicMock
from app.agents.nodes import get_llm
from app.core.config import settings

@patch("app.agents.nodes.SessionLocal")
@patch("app.agents.nodes.ChatOllama")
def test_hybrid_model_selection(mock_chat_ollama, mock_session):
    # Setup Mock DB to return ollama model
    mock_db = MagicMock()
    mock_session.return_value = mock_db

    # Mock Settings Query
    def side_effect(query):
        mock_query = MagicMock()
        if "AI_MODEL_TEST" in str(query): # Not easy to match exact query object logic
            pass
        return mock_query

    # Easier approach: Mock get_system_setting
    with patch("app.agents.nodes.get_system_setting") as mock_get_setting:
        # Case 1: Ollama Model
        mock_get_setting.side_effect = lambda db, key, default: "ollama/llama3" if key == "AI_MODEL_TEST" else "http://localhost:11434"

        llm = get_llm("AI_MODEL_TEST", "default")

        # Verify ChatOllama was initialized
        mock_chat_ollama.assert_called_once()
        assert llm == mock_chat_ollama.return_value
