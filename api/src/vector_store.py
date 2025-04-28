from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from typing import List, Optional

class VectorStore:
    def __init__(self, persist_directory: str, collection_name: str = "example_collection", model_name: str = "llama3.2"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(model=model_name)
        
        # Initialize vector store
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    async def add_document(self, file_path: Path) -> List[str]:
        # Load document
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
            
        # Split document
        document_splits = self.text_splitter.split_documents(pages)
        
        # Add to vector store
        split_ids = self.vector_store.add_documents(documents=document_splits)
        
        return split_ids
    
    def delete_documents(self, document_ids: List[str]) -> None:
        if document_ids:
            self.vector_store.delete(document_ids)
    
    def search_documents(self, query: str, k: int = 4) -> List[dict]:
        docs = self.vector_store.similarity_search_with_relevance_scores(query, k=k)
        return docs 