from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from typing import List, Optional
from chromadb import HttpClient

class VectorStore:
    def __init__(self, persist_directory: str, collection_name: str = "pdfs", model_name: str = "nomic-embed-text",
                 chroma_client_type: str = "persistent", chroma_host: str = "0.0.0.0", chroma_port: int = 3020):

        self.embeddings = OllamaEmbeddings(model=model_name)
        
        if chroma_client_type == "http":
            chroma_client = HttpClient(host=chroma_host, port=chroma_port)
            self.vector_store = Chroma(
                client=chroma_client,
                collection_name=collection_name,
                embedding_function=self.embeddings,

            )
        elif chroma_client_type == "persistent":
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
    
    async def add_document(self, documents: List[Document]) -> List[str]:
        split_ids = await self.vector_store.aadd_documents(documents=documents)
        return split_ids
    
    async def delete_documents(self, document_ids: List[str]) -> None:
        if document_ids:
            self.vector_store.delete(document_ids)
    
    async def search_documents(self, query: str, session_id: Optional[str] = None, k: int = 2) -> List[dict]:
        try:
            if session_id:
                docs = self.vector_store.similarity_search(
                    query, 
                    k=k,
                    filter={"session_id": session_id}
                )
            else:
                docs = self.vector_store.similarity_search(query, k=k)
                
            return docs
        except Exception as e:
            print(f"Error in search_documents: {str(e)}")
            return [] 