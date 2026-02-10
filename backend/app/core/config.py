from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.orm import Session
# Note: We can't easily inject DB session into Pydantic settings loading at startup without circular imports.
# Strategy: We load base settings from Env, and specific dynamic settings (Models/Keys) are fetched on demand
# via a Helper Service, not this static Config class.

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mami AI"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database (Postgres)
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Graph Database (Neo4j)
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: str = "6379"

    # Vector Database (ChromaDB)
    CHROMA_DB_HOST: str
    CHROMA_DB_PORT: str = "8000"

    # AI Keys (Base / Fallback)
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Helper to fetch dynamic config
def get_system_setting(db: Session, key: str, default: str = None) -> str:
    from app.models.settings import SystemSettings
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    return setting.value if setting else default
