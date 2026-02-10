from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.settings import SystemSettings
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user # Need to implement/expose this dependency
from pydantic import BaseModel

router = APIRouter()

class SettingUpdate(BaseModel):
    key: str
    value: str

class SettingOut(BaseModel):
    key: str
    value: str
    description: str

@router.get("/", response_model=List[SettingOut])
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    settings = db.query(SystemSettings).all()
    # Mask secrets
    return [
        SettingOut(
            key=s.key,
            value="********" if s.is_secret else s.value,
            description=s.description or ""
        ) for s in settings
    ]

@router.post("/")
def update_setting(
    setting_in: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    setting = db.query(SystemSettings).filter(SystemSettings.key == setting_in.key).first()
    if not setting:
        # Create new (assuming known keys or flexible schema)
        setting = SystemSettings(key=setting_in.key, value=setting_in.value)
        db.add(setting)
    else:
        setting.value = setting_in.value

    db.commit()
    return {"status": "success"}

# Initialize Default Settings
def init_settings(db: Session):
    defaults = {
        "AI_MODEL_ROUTER": "llama-3.1-8b-instant",
        "AI_MODEL_CODER": "llama-3.1-70b-versatile",
        "AI_MODEL_CHAT": "gemini-1.5-flash",
        "OLLAMA_BASE_URL": "http://host.docker.internal:11434" # Access host localhost from docker
    }
    for key, value in defaults.items():
        if not db.query(SystemSettings).filter(SystemSettings.key == key).first():
            db.add(SystemSettings(key=key, value=value, description="Default AI Model"))
    db.commit()
