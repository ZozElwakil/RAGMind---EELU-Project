"""
Stats Routes.
API endpoints for global statistics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from backend.database import get_db
from backend.database.models import Project, Asset, Chunk

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/")
async def get_global_stats(db: AsyncSession = Depends(get_db)):
    """Get global statistics."""
    try:
        # Count projects
        projects_query = select(func.count(Project.id))
        projects_count = await db.scalar(projects_query)
        
        # Count documents
        documents_query = select(func.count(Asset.id))
        documents_count = await db.scalar(documents_query)
        
        # Count chunks
        chunks_query = select(func.count(Chunk.id))
        chunks_count = await db.scalar(chunks_query)
        
        return {
            "projects": projects_count or 0,
            "documents": documents_count or 0,
            "chunks": chunks_count or 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
