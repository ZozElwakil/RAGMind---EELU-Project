"""
PGVector Provider Implementation.
Uses PostgreSQL with pgvector extension for vector storage.
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.providers.vectordb.interface import VectorDBInterface
from backend.database.models import Chunk, Project
from backend.database.connection import async_session_maker
import logging

logger = logging.getLogger(__name__)


class PGVectorProvider(VectorDBInterface):
    """PostgreSQL pgvector implementation."""
    
    def __init__(self):
        """Initialize PGVector provider."""
        logger.info("PGVector provider initialized")
    
    async def create_collection(
        self,
        collection_name: str,
        dimension: int,
        **kwargs
    ) -> bool:
        """
        Create collection (for pgvector, this is handled by table creation).
        
        Args:
            collection_name: Not used (using chunks table)
            dimension: Vector dimension
            
        Returns:
            True (table already exists from migrations)
        """
        # With pgvector, collections are handled by the chunks table
        # The vector column is already defined in the model
        logger.info(f"Collection '{collection_name}' ready (using chunks table)")
        return True
    
    async def add_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        ids: List[Any],
        metadata: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> bool:
        """
        Add/update vectors in chunks table.
        
        Args:
            collection_name: Project name or identifier
            vectors: List of embeddings
            ids: List of chunk IDs
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            async with async_session_maker() as session:
                for i, (chunk_id, vector) in enumerate(zip(ids, vectors)):
                    # Update chunk with embedding
                    stmt = select(Chunk).where(Chunk.id == chunk_id)
                    result = await session.execute(stmt)
                    chunk = result.scalar_one_or_none()
                    
                    if chunk:
                        chunk.embedding = vector
                
                await session.commit()
                logger.info(f"Added {len(vectors)} vectors to collection '{collection_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Error adding vectors: {str(e)}")
            raise
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Tuple[Any, float, Dict[str, Any]]]:
        """
        Search for similar vectors.
        Falls back to Python-based similarity if pgvector is not available.
        """
        try:
            async with async_session_maker() as session:
                # Build query to get all relevant chunks
                # We fetch the embedding to calculate similarity in Python
                query = select(
                    Chunk.id,
                    Chunk.content,
                    Chunk.extra_metadata,
                    Chunk.asset_id,
                    Chunk.embedding
                ).where(
                    Chunk.embedding.isnot(None)
                )
                
                # Apply filters
                if filter_dict:
                    if 'project_id' in filter_dict:
                        query = query.where(Chunk.project_id == filter_dict['project_id'])
                    if 'asset_id' in filter_dict:
                        query = query.where(Chunk.asset_id == filter_dict['asset_id'])
                
                result = await session.execute(query)
                rows = result.all()
                
                # Calculate similarity in Python
                def cosine_similarity(v1, v2):
                    if not v1 or not v2: return 0.0
                    dot_product = sum(a * b for a, b in zip(v1, v2))
                    norm1 = sum(a * a for a in v1) ** 0.5
                    norm2 = sum(a * a for a in v2) ** 0.5
                    if not norm1 or not norm2: return 0.0
                    return dot_product / (norm1 * norm2)
                
                scored_results = []
                for row in rows:
                    sim = cosine_similarity(query_vector, row.embedding)
                    scored_results.append((
                        row.id,
                        sim,
                        {
                            'content': row.content,
                            'metadata': row.extra_metadata,
                            'asset_id': row.asset_id
                        }
                    ))
                
                # Sort by similarity and take top_k
                scored_results.sort(key=lambda x: x[1], reverse=True)
                results = scored_results[:top_k]
                
                logger.info(f"Found {len(results)} similar chunks using Python fallback")
                return results
                
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise
    
    async def delete_collection(
        self,
        collection_name: str,
        **kwargs
    ) -> bool:
        """
        Delete all chunks for a project.
        
        Args:
            collection_name: Project ID or identifier
            
        Returns:
            True if successful
        """
        try:
            async with async_session_maker() as session:
                project_id = kwargs.get('project_id')
                if project_id:
                    stmt = delete(Chunk).where(Chunk.project_id == project_id)
                    await session.execute(stmt)
                    await session.commit()
                    logger.info(f"Deleted collection '{collection_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
    
    async def collection_exists(
        self,
        collection_name: str,
        **kwargs
    ) -> bool:
        """
        Check if project exists.
        
        Args:
            collection_name: Project name
            
        Returns:
            True if exists
        """
        try:
            async with async_session_maker() as session:
                project_id = kwargs.get('project_id')
                if project_id:
                    stmt = select(Project).where(Project.id == project_id)
                    result = await session.execute(stmt)
                    return result.scalar_one_or_none() is not None
                return False
                
        except Exception as e:
            logger.error(f"Error checking collection: {str(e)}")
            return False
