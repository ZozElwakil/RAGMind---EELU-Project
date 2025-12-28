"""
Qdrant Provider Implementation.
Uses Qdrant standalone vector database.
"""
from typing import List, Dict, Any, Optional, Tuple
from backend.providers.vectordb.interface import VectorDBInterface
import logging

logger = logging.getLogger(__name__)


class QdrantProvider(VectorDBInterface):
    """
    Qdrant vector database implementation.
    Optional provider - requires Qdrant server running.
    """
    
    def __init__(self, url: str = "http://localhost:6333", api_key: str = ""):
        """
        Initialize Qdrant provider.
        
        Args:
            url: Qdrant server URL
            api_key: Optional API key
        """
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct
            
            if url.startswith("path://"):
                path = url.replace("path://", "")
                self.client = QdrantClient(path=path)
                logger.info(f"Qdrant provider initialized with local path: {path}")
            else:
                self.client = QdrantClient(url=url, api_key=api_key if api_key else None)
                logger.info(f"Qdrant provider initialized at {url}")
        except ImportError:
            logger.error("qdrant-client not installed. Install with: pip install qdrant-client")
            raise
    
    async def create_collection(
        self,
        collection_name: str,
        dimension: int,
        **kwargs
    ) -> bool:
        """
        Create Qdrant collection.
        
        Args:
            collection_name: Collection name
            dimension: Vector dimension
            
        Returns:
            True if successful
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=self.VectorParams(
                        size=dimension,
                        distance=self.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection '{collection_name}'")
            else:
                logger.info(f"Qdrant collection '{collection_name}' already exists")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    async def add_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        ids: List[Any],
        metadata: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> bool:
        """
        Add vectors to Qdrant collection.
        
        Args:
            collection_name: Collection name
            vectors: List of embeddings
            ids: List of IDs
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            points = []
            for i, (point_id, vector) in enumerate(zip(ids, vectors)):
                payload = metadata[i] if metadata and i < len(metadata) else {}
                points.append(
                    self.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                )
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} points to Qdrant collection '{collection_name}'")
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
        Search Qdrant for similar vectors.
        
        Args:
            collection_name: Collection name
            query_vector: Query embedding
            top_k: Number of results
            filter_dict: Optional filters
            
        Returns:
            List of (id, score, payload)
        """
        try:
            # Build filter if provided
            search_filter = None
            if filter_dict:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                conditions = []
                for key, value in filter_dict.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                search_filter = Filter(must=conditions)
            
            # Search
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=search_filter
            )
            
            # Format results
            results = []
            for hit in search_result:
                results.append((
                    hit.id,
                    hit.score,
                    hit.payload
                ))
            
            logger.info(f"Found {len(results)} similar points in Qdrant")
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
        Delete Qdrant collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted Qdrant collection '{collection_name}'")
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
        Check if Qdrant collection exists.
        
        Args:
            collection_name: Collection name
            
        Returns:
            True if exists
        """
        try:
            collections = self.client.get_collections().collections
            return any(c.name == collection_name for c in collections)
            
        except Exception as e:
            logger.error(f"Error checking collection: {str(e)}")
            return False
