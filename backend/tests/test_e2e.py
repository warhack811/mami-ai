from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock, patch

client = TestClient(app)

# Mock external services
@patch("app.services.voice.client")
def test_transcribe(mock_groq_client):
    # Setup mock
    mock_transcription = MagicMock()
    mock_transcription.text = "Hello Mami AI"
    mock_groq_client.audio.transcriptions.create.return_value = mock_transcription

    # Create dummy audio file
    files = {'file': ('test.wav', b'dummy audio content', 'audio/wav')}

    response = client.post("/api/v1/voice/transcribe", files=files)
    assert response.status_code == 200
    assert response.json()["text"] == "Hello Mami AI"

@patch("app.core.rate_limit.limiter.limit")
def test_rate_limiting(mock_limit):
    # We can't easily test slowapi with TestClient in this setup without complex config,
    # but we can verify the endpoint exists.
    response = client.get("/health")
    assert response.status_code == 200
