"""
Text Chunking Service.
Handles splitting text into chunks using LangChain.
"""
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """Service for chunking text documents."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize chunking service.
        
        Args:
            chunk_size: Size of each chunk (defaults to settings)
            chunk_overlap: Overlap between chunks (defaults to settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info(f"Chunking service initialized (size={self.chunk_size}, overlap={self.chunk_overlap})")
    
    async def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Text to chunk
            metadata: Optional base metadata for all chunks
            
        Returns:
            List of chunk dictionaries with 'content' and 'metadata'
        """
        try:
            # Split text
            text_chunks = self.text_splitter.split_text(text)
            
            # Create chunk objects with metadata
            chunks = []
            base_metadata = metadata or {}
            
            for i, chunk_text in enumerate(text_chunks):
                chunk_metadata = {
                    **base_metadata,
                    'chunk_index': i,
                    'total_chunks': len(text_chunks),
                    'chunk_size': len(chunk_text)
                }
                
                chunks.append({
                    'content': chunk_text,
                    'metadata': chunk_metadata
                })
            
            logger.info(f"Created {len(chunks)} chunks from text ({len(text)} characters)")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise
    
    async def chunk_document(
        self,
        text: str,
        document_name: str,
        additional_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk document with automatic metadata.
        
        Args:
            text: Document text
            document_name: Name of document
            additional_metadata: Optional additional metadata
            
        Returns:
            List of chunks with metadata
        """
        metadata = {
            'document_name': document_name,
            **(additional_metadata or {})
        }
        
        return await self.chunk_text(text, metadata)
