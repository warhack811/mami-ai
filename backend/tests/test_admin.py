import pytest
from app.main import app
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db

# Override dependency
mock_user = MagicMock()
mock_user.is_superuser = True
app.dependency_overrides[get_current_user] = lambda: mock_user

# Mock DB Session
mock_db = MagicMock()
app.dependency_overrides[get_db] = lambda: mock_db

client = TestClient(app)

def test_admin_settings_flow():
    # Setup Mock DB Query for Update
    mock_setting = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None # Simulate not found initially

    # 1. Update Setting
    response = client.post("/api/v1/admin/", json={"key": "AI_MODEL_CHAT", "value": "test-model-v1"})
    assert response.status_code == 200

    # Setup Mock DB Query for Get
    mock_setting_obj = MagicMock()
    mock_setting_obj.key = "AI_MODEL_CHAT"
    mock_setting_obj.value = "test-model-v1"
    mock_setting_obj.description = "Test"
    mock_setting_obj.is_secret = False
    mock_db.query.return_value.all.return_value = [mock_setting_obj]

    # 2. Verify Update
    response = client.get("/api/v1/admin/")
    assert response.status_code == 200
    settings = response.json()
    model_setting = next((s for s in settings if s["key"] == "AI_MODEL_CHAT"), None)
    assert model_setting["value"] == "test-model-v1"
