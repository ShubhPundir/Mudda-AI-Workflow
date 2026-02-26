"""
FastAPI application for Mudda AI Workflow system
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from sessions.database import engine
from models import Base
from sqlalchemy import text
from routers import component_router, workflow_router, workflow_stream_router, health_router

# Create database tables
# Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        print("DEBUG: Application starting - creating database schema and tables...")
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS workflow"))
        await conn.run_sync(Base.metadata.create_all)
        print("DEBUG: Database initialization complete.")
    yield
    # NOTE: don't use this for now


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered workflow generation for civic issue resolution",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
    # lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(component_router)
app.include_router(workflow_router)
app.include_router(workflow_stream_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )