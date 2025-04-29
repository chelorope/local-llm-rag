from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from typing import List, Optional, Dict

class VectorStore:
    def __init__(self, persist_directory: str, collection_name: str = "pdfs", model_name: str = "nomic-embed-text"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings
        print(f"Initializing embeddings with model: {model_name}")
        self.embeddings = OllamaEmbeddings(model=model_name)
        
        # Initialize vector store
        print(f"Initializing vector store at {persist_directory} with collection {collection_name}")
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    async def add_document(self, file_path: Path, session_id: Optional[str] = None) -> List[str]:
        # Load document
        print(f"Loading document from {file_path} with session_id: {session_id}")
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
            
        # Split document
        document_splits = self.text_splitter.split_documents(pages)
        print(f"Document split into {len(document_splits)} chunks")
        
        # Add metadata with session_id to each document split
        for i, doc in enumerate(document_splits):
            # Make sure metadata is a dictionary
            if not isinstance(doc.metadata, dict):
                doc.metadata = {}
            
            # Add session_id to metadata
            doc.metadata["session_id"] = session_id
            
            # For debugging, print first few documents
            if i < 3:
                print(f"Document chunk {i} metadata: {doc.metadata}")
                print(f"Document chunk {i} content preview: {doc.page_content[:100]}...")
        
        # Add to vector store
        split_ids = self.vector_store.add_documents(documents=document_splits)
        print(f"Added {len(split_ids)} document chunks to vector store")
        
        return split_ids
    
    def delete_documents(self, document_ids: List[str]) -> None:
        if document_ids:
            self.vector_store.delete(document_ids)
    
    def search_documents(self, query: str, session_id: Optional[str] = None, k: int = 2) -> List[dict]:
        try:
            if session_id:
                docs = self.vector_store.similarity_search(
                    query, 
                    k=k,
                    filter={"session_id": session_id}
                )
            else:
                docs = self.vector_store.similarity_search(query, k=k)
            
            # Print metadata of found documents for debugging
            for i, doc in enumerate(docs):
                print(f"Doc {i}: {doc.page_content[:50]}... | Metadata: {doc.metadata}")
                
            return docs
        except Exception as e:
            print(f"Error in search_documents: {str(e)}")
            # Return empty list in case of error
            return [] 