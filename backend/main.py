from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API Routers
from app.api.analyze import router as analyze_router
from app.core.config import get_settings
from app.database.session import Base, get_engine
from app.models.incident_record import IncidentRecord

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database schema when the application starts."""

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized", extra={"tables": [IncidentRecord.__tablename__]})
    yield


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI Reasoning Agent for Intelligent Incident Response",
    version=settings.api_version,
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(analyze_router)


@app.get("/")
def home():
    return {
        "project": "IncidentIQ",
        "message": "Welcome to IncidentIQ 🚀",
        "status": "Backend is running successfully!"
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "server": "Running",
        "version": "1.0.0"
    }
