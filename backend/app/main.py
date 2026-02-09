from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.models.user import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB Tables
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
    yield

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Simple Health Check
    @application.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "project": settings.PROJECT_NAME
        }

    # Include API router
    from app.api.v1.api import api_router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application

app = create_application()
