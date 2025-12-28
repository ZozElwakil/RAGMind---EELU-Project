"""
Embedding Service.
Handles generating embeddings using LLM provider.
"""
from typing import List
from backend.providers.llm.factory import LLMProviderFactory
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings."""
    
    def __init__(self):
        """Initialize embedding service with LLM provider."""
        self.llm_provider = LLMProviderFactory.create_provider()
        logger.info(f"Embedding service initialized with {self.llm_provider.get_model_name()}")
    
    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 10
    ) -> List[List[float]]:
        """
        Generate embeddings for list of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []
            
            embeddings = await self.llm_provider.generate_embeddings(
                texts=texts,
                batch_size=batch_size
            )
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Text string
            
        Returns:
            Embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def get_embedding_dimension(self) -> int:
        """
        Get the embedding vector dimension.
        
        Returns:
            Dimension size
        """
        return self.llm_provider.get_embedding_dimension()
