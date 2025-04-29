import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # MongoDB Settings
    mongo_uri: str = Field(default="mongodb://localhost:27017/")
    mongo_db_name: str = Field(default="pdf_assistant")
    mongo_documents_collection: str = Field(default="documents")
    mongo_message_history_collection: str = Field(default="message_history")

    # ChromaDB Settings
    chroma_client_type: str = Field(default="persistent")
    chroma_host: str = Field(default="0.0.0.0")
    chroma_port: int = Field(default=3020)
    
    # File Storage Settings
    documents_dir: Path = Field(default=Path(os.path.dirname(os.path.dirname(__file__))) / "documents")
    
    # Vector Store Settings
    vector_store_dir: Path = Field(default=Path(os.path.dirname(os.path.dirname(__file__))) / "chroma_langchain_db")
    vector_collection_name: str = Field(default="pdfs")
    
    # LLM Settings
    embedding_model: str = Field(default="nomic-embed-text")
    llm_model: str = Field(default="llama3.2")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8001)

    # Document Processing Settings
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    
    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "extra": "ignore",
    }

settings = Settings() 