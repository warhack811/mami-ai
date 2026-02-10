import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.models.user import Base
from app.models.settings import SystemSettings # Ensure table creation
from app.models.goal import Goal # Ensure table creation
from app.api.v1.endpoints.admin import init_settings
from app.core.rate_limit import limiter, RateLimitExceeded, _rate_limit_exceeded_handler
from app.services.proactive import proactive_loop
import asyncio

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mami_ai")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Log Request
        logger.info(f"Request started: {request.method} {request.url.path} ID={request_id}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log Response
            logger.info(f"Request finished: {request.method} {request.url.path} ID={request_id} Status={response.status_code} Duration={process_time:.4f}s")

            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path} ID={request_id} Error={str(e)} Duration={process_time:.4f}s")
            raise e

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB Tables
    try:
        Base.metadata.create_all(bind=engine)
        SystemSettings.metadata.create_all(bind=engine)
        Goal.metadata.create_all(bind=engine)

        # Init Default Settings
        db = SessionLocal()
        init_settings(db)
        db.close()

        logger.info("Database tables created/verified.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

    # Start Proactive Loop
    asyncio.create_task(proactive_loop())

    yield

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Middleware
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_middleware(StructuredLoggingMiddleware)

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Global Exception Handler
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global Exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An internal error occurred. Please try again later.", "detail": str(exc)},
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
