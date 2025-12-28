"""
Query Service.
Handles query processing and similarity search.
"""
from typing import List, Dict, Any, Optional
from backend.services.embedding_service import EmbeddingService
from backend.providers.vectordb.factory import VectorDBProviderFactory
import logging

logger = logging.getLogger(__name__)


class QueryService:
    """Service for processing queries and searching."""
    
    def __init__(self):
        """Initialize query service."""
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDBProviderFactory.create_provider()
        logger.info("Query service initialized")
    
    async def search_similar_chunks(
        self,
        query: str,
        project_id: int,
        top_k: int = 5,
        asset_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for chunks similar to query.
        
        Args:
            query: Search query
            project_id: Project ID to search within
            top_k: Number of results to return
            asset_id: Optional asset ID to filter by
            
        Returns:
            List of similar chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_single_embedding(query)
            
            # Build filter
            filter_dict = {'project_id': project_id}
            if asset_id:
                filter_dict['asset_id'] = asset_id
            
            # Search vector database
            results = await self.vector_db.search(
                collection_name=f"project_{project_id}",
                query_vector=query_embedding,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            # Format results
            formatted_results = []
            for chunk_id, similarity, metadata in results:
                formatted_results.append({
                    'chunk_id': chunk_id,
                    'similarity': similarity,
                    'content': metadata.get('content', ''),
                    'metadata': metadata.get('metadata', {}),
                    'asset_id': metadata.get('asset_id')
                })
            
            logger.info(f"Found {len(formatted_results)} similar chunks for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching chunks: {str(e)}")
            raise
