from src.file_handler import FileHandler
from src.vector_store import VectorStore
from src.document_store import DocumentStore
from src.assistant import PDFAssistant
from config.settings import settings
from src.document_processors import DocumentProcessor

class ComponentFactory:
    """Factory class for creating application components with configurations."""
    
    @staticmethod
    def create_file_handler(documents_dir=settings.documents_dir) -> FileHandler:
        """Create a FileHandler instance with the provided configuration."""
        return FileHandler(documents_dir)
    
    @staticmethod
    def create_vector_store(
        persist_directory=str(settings.vector_store_dir),
        collection_name=settings.vector_collection_name,
        model_name=settings.embedding_model,
        chroma_client_type=settings.chroma_client_type,
        chroma_host=settings.chroma_host,
        chroma_port=settings.chroma_port
    ) -> VectorStore:
        """Create a VectorStore instance with the provided configuration."""
        return VectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
            model_name=model_name,
            chroma_client_type=chroma_client_type,
            chroma_host=chroma_host,
            chroma_port=chroma_port
        )
    
    @staticmethod
    def create_document_store(
        mongo_uri=settings.mongo_uri,
        db_name=settings.mongo_db_name,
        collection_name=settings.mongo_documents_collection
    ) -> DocumentStore:
        """Create a DocumentStore instance with the provided configuration."""
        return DocumentStore(
            mongo_uri=mongo_uri,
            db_name=db_name,
            collection_name=collection_name
        )
    
    @staticmethod
    def create_assistant(
        persist_directory=str(settings.vector_store_dir),
        model_name=settings.llm_model,
        mongo_uri=settings.mongo_uri,
        mongo_db_name=settings.mongo_db_name,
        mongo_message_history_collection=settings.mongo_message_history_collection
    ) -> PDFAssistant:
        """Create a PDFAssistant instance with the provided configuration."""
        return PDFAssistant(
            persist_directory=persist_directory,
            model_name=model_name,
            mongo_uri=mongo_uri,
            mongo_db_name=mongo_db_name,
            mongo_message_history_collection=mongo_message_history_collection
        ) 
    
    @staticmethod
    def create_document_processor(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    ) -> DocumentProcessor:
        """Create a DocumentProcessor instance with the provided configuration."""
        return DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )