from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.db.session import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String) # Encrypted or JSON string
    is_secret = Column(Boolean, default=False)
    description = Column(String, nullable=True)

    # Example Keys:
    # "AI_MODEL_ROUTER" -> "llama-3.1-8b-instant"
    # "AI_MODEL_CODER" -> "openai/gpt-4"
    # "GROQ_API_KEY" -> "gsk_..."
