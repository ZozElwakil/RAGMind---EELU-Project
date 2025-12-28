"""
Query Routes.
API endpoints for querying documents.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from backend.database import get_db
from backend.controllers.query_controller import QueryController

router = APIRouter(tags=["Query"])
query_controller = QueryController()


# Request/Response Models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    language: str = Field(default="ar", pattern="^(ar|en)$")
    asset_id: Optional[int] = None


class SourceInfo(BaseModel):
    document_name: str
    chunk_index: int
    similarity: float
    asset_id: int


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    context_used: int


# Routes
@router.post("/projects/{project_id}/query", response_model=QueryResponse)
async def query_project(
    project_id: int,
    query_data: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ask a question about project documents.
    Returns AI-generated answer with sources.
    """
    try:
        result = await query_controller.answer_query(
            db=db,
            project_id=project_id,
            query=query_data.query,
            top_k=query_data.top_k,
            language=query_data.language,
            asset_id=query_data.asset_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
