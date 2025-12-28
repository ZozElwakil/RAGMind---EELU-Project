"""
Query Controller.
Business logic for query processing and answer generation.
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.query_service import QueryService
from backend.services.answer_service import AnswerService
import logging

logger = logging.getLogger(__name__)


class QueryController:
    """Controller for query operations."""
    
    def __init__(self):
        """Initialize query controller."""
        self.query_service = QueryService()
        self.answer_service = AnswerService()
    
    async def answer_query(
        self,
        db: AsyncSession,
        project_id: int,
        query: str,
        top_k: int = 5,
        language: str = "ar",
        asset_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process query and generate answer.
        
        Args:
            db: Database session
            project_id: Project ID to search in
            query: User question
            top_k: Number of chunks to retrieve
            language: Response language ('ar' or 'en')
            asset_id: Optional specific document to search
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Search for relevant chunks
            logger.info(f"Processing query for project {project_id}: {query[:50]}...")
            
            similar_chunks = await self.query_service.search_similar_chunks(
                query=query,
                project_id=project_id,
                top_k=top_k,
                asset_id=asset_id
            )
            
            if not similar_chunks:
                return {
                    'answer': 'لم أتمكن من العثور على معلومات ذات صلة في المستندات.' if language == 'ar' 
                             else 'Could not find relevant information in the documents.',
                    'sources': [],
                    'context_used': 0
                }
            
            # Generate answer
            result = await self.answer_service.generate_answer(
                query=query,
                context_chunks=similar_chunks,
                language=language,
                include_sources=True
            )
            
            logger.info(f"Generated answer for query (used {result['context_used']} chunks)")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
