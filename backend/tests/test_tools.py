import os
from unittest.mock import patch

# Set dummy environment variables to pass Settings validation and API wrapper validation
os.environ["SECRET_KEY"] = "test_secret"
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_password"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
os.environ["REDIS_HOST"] = "localhost"
os.environ["CHROMA_DB_HOST"] = "localhost"
os.environ["SERPER_API_KEY"] = "test_serper_key"
os.environ["GROQ_API_KEY"] = "test_groq_key"

# Now import the module under test
from app.tools.definitions import web_search

def test_web_search_success():
    """Test that web_search returns the search result on success."""
    # Mock the search object in the module
    with patch("app.tools.definitions.search") as mock_search:
        mock_search.run.return_value = "Search result"

        # Invoke the tool
        result = web_search.invoke({"query": "test query"})

        # Verify
        assert result == "Search result"
        mock_search.run.assert_called_once_with("test query")

def test_web_search_error():
    """Test that web_search handles exceptions gracefully."""
    # Mock the search object to raise an exception
    with patch("app.tools.definitions.search") as mock_search:
        mock_search.run.side_effect = Exception("Network error")

        # Invoke the tool
        result = web_search.invoke({"query": "test query"})

        # Verify the error message format
        assert result == "Error searching web: Network error"
        mock_search.run.assert_called_once_with("test query")
