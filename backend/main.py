"""
Main FastAPI Application.
Entry point for the RAGMind backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
# Configure logging
from backend.config import settings
import logging

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from backend.database import init_db, close_db
from backend.routes import projects, documents, query, health, stats, bot_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting RAGMind API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAGMind API...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    RAGMind - Retrieval Augmented Generation System
    
    A powerful document processing and question-answering API using:
    - Google Gemini 2.5 Flash for LLM capabilities
    - PostgreSQL with pgvector for vector storage
    - LangChain for document processing
    
    ## Features
    - Project-based document organization
    - Multi-format document support (PDF, TXT, DOCX)
    - Automatic text chunking and embedding
    - Vector similarity search
    - AI-powered question answering
    - Multi-language support (Arabic/English)
    """,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(projects.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(stats.router)
app.include_router(bot_config.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
