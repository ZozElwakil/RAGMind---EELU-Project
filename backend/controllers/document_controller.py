"""
Document Controller.
Business logic for document upload and processing.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Asset, Chunk, Project
from backend.database.connection import async_session_maker
from backend.services.file_service import FileService
from backend.services.document_loader import DocumentLoaderService
from backend.services.chunking_service import ChunkingService
from backend.services.embedding_service import EmbeddingService
from backend.providers.vectordb.factory import VectorDBProviderFactory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DocumentController:
    """Controller for document operations."""
    
    def __init__(self):
        """Initialize document controller."""
        logger.info("Initializing DocumentController...")
        self.file_service = FileService()
        self.document_loader = DocumentLoaderService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDBProviderFactory.create_provider()
        logger.info("✅ DocumentController initialized")
    
    async def upload_document(
        self,
        db: AsyncSession,
        project_id: int,
        file_content: bytes,
        filename: str,
        file_size: int
    ) -> Asset:
        """
        Upload document and save metadata.
        
        Args:
            db: Database session
            project_id: Project ID
            file_content: File content bytes
            filename: Original filename
            file_size: File size in bytes
            
        Returns:
            Created asset
            
        Raises:
            ValueError: If validation fails
        """
        try:
            logger.debug(f"Uploading document: {filename} ({file_size} bytes) to project {project_id}")
            
            # Validate file
            is_valid, error_msg = self.file_service.validate_file(filename, file_size)
            if not is_valid:
                logger.warning(f"File validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            # Check project exists
            project_stmt = select(Project).where(Project.id == project_id)
            project_result = await db.execute(project_stmt)
            project = project_result.scalar_one_or_none()
            if not project:
                raise ValueError(f"Project not found: {project_id}")
            
            # Save file
            unique_filename, file_path = await self.file_service.save_upload_file(
                file_content=file_content,
                filename=filename,
                project_id=project_id
            )
            
            # Get file type
            from pathlib import Path
            file_type = Path(filename).suffix.lstrip('.')
            
            # Create asset record
            asset = Asset(
                project_id=project_id,
                filename=unique_filename,
                original_filename=filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                status="uploaded"
            )
            
            db.add(asset)
            await db.commit()
            await db.refresh(asset)
            
            logger.info(f"Uploaded document: {asset.id} - {filename}")
            return asset
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error uploading document: {str(e)}")
            raise
    
    async def process_document(self, asset_id: int) -> bool:
        """
        Process document: extract, chunk, embed, and store.

        Returns:
            True if successful
        """
        logger.info(f"🔄 Starting document processing for asset {asset_id}")
        
        async with async_session_maker() as db:
            # Get asset
            asset_stmt = select(Asset).where(Asset.id == asset_id)
            asset_result = await db.execute(asset_stmt)
            asset = asset_result.scalar_one_or_none()
            
            if not asset:
                raise ValueError(f"Asset not found: {asset_id}")
            
            logger.debug(f"Processing document: {asset.original_filename} ({asset.file_size} bytes)")
            
            # Update status to processing
            asset.status = "processing"
            await db.commit()
            
            try:
                # Extract text
                logger.info(f"📖 Extracting text from {asset.original_filename}")
                text = await self.document_loader.load_document(asset.file_path)
                if not text or not text.strip():
                    raise ValueError("No text extracted from document (empty content).")
                
                logger.debug(f"Extracted {len(text)} characters of text")
                
                # Chunk text
                logger.info(f"✂️ Chunking text ({len(text)} characters)")
                chunks_data = await self.chunking_service.chunk_document(
                    text=text,
                    document_name=asset.original_filename,
                    additional_metadata={
                        'file_type': asset.file_type,
                        'asset_id': asset.id
                    }
                )
                
                logger.debug(f"Created {len(chunks_data)} chunks")
                
                # Create chunk records
                chunk_records = []
                for i, chunk_data in enumerate(chunks_data):
                    chunk = Chunk(
                        project_id=asset.project_id,
                        asset_id=asset.id,
                        content=chunk_data['content'],
                        chunk_index=i,
                        extra_metadata=chunk_data['metadata']
                    )
                    db.add(chunk)
                    chunk_records.append(chunk)
                
                await db.commit()
                
                # Refresh to get IDs
                for chunk in chunk_records:
                    await db.refresh(chunk)
                
                logger.debug(f"Saved {len(chunk_records)} chunks to database")
                
                # Generate embeddings
                logger.info(f"🧠 Generating embeddings for {len(chunk_records)} chunks")
                texts = [chunk.content for chunk in chunk_records]
                embeddings = await self.embedding_service.generate_embeddings(texts)
                
                logger.debug(f"Generated {len(embeddings)} embeddings")

                # Ensure collection exists (needed for Qdrant)
                collection_name = f"project_{asset.project_id}"
                dim = self.embedding_service.get_embedding_dimension()
                exists = await self.vector_db.collection_exists(collection_name, project_id=asset.project_id)
                if not exists:
                    logger.info(f"Creating vector collection: {collection_name}")
                    await self.vector_db.create_collection(collection_name, dimension=dim)
                else:
                    logger.debug(f"Vector collection {collection_name} already exists")

                # Store embeddings in chunks and vector DB
                chunk_ids = [chunk.id for chunk in chunk_records]
                payloads = [
                    {
                        "content": c.content,
                        "metadata": c.extra_metadata,
                        "asset_id": c.asset_id,
                        "project_id": c.project_id,
                    }
                    for c in chunk_records
                ]
                logger.info(f"💾 Storing {len(embeddings)} vectors in database")
                await self.vector_db.add_vectors(
                    collection_name=collection_name,
                    vectors=embeddings,
                    ids=chunk_ids,
                    metadata=payloads
                )
                
                # Update asset status
                asset.status = "completed"
                asset.processed_at = datetime.utcnow()
                await db.commit()
                
                logger.info(f"✅ Completed processing document: {asset.id} - {asset.original_filename}")
                return True
                
            except Exception as e:
                # Mark as failed
                asset.status = "failed"
                asset.error_message = str(e)
                await db.commit()
                logger.error(f"❌ Document processing failed for asset {asset_id}: {str(e)}")
                raise
    
    async def get_document(
        self,
        db: AsyncSession,
        asset_id: int
    ) -> Optional[Asset]:
        """
        Get document by ID.
        
        Args:
            db: Database session
            asset_id: Asset ID
            
        Returns:
            Asset or None
        """
        try:
            stmt = select(Asset).where(Asset.id == asset_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    async def list_project_documents(
        self,
        db: AsyncSession,
        project_id: int
    ) -> List[Asset]:
        """
        List all documents in project.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            List of assets
        """
        try:
            stmt = select(Asset).where(Asset.project_id == project_id).order_by(Asset.created_at.desc())
            result = await db.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
    
    async def delete_document(
        self,
        db: AsyncSession,
        asset_id: int
    ) -> bool:
        """
        Delete document and associated chunks.
        
        Args:
            db: Database session
            asset_id: Asset ID
            
        Returns:
            True if deleted
        """
        try:
            # Get asset
            asset = await self.get_document(db, asset_id)
            if not asset:
                return False
            
            # Delete file
            await self.file_service.delete_file(asset.file_path)
            
            # Delete from database (cascade will delete chunks)
            await db.delete(asset)
            await db.commit()
            
            logger.info(f"Deleted document: {asset_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting document: {str(e)}")
            raise
