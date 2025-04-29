from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from pathlib import Path

class DocumentStore:
    def __init__(self, mongo_uri: str, 
                 db_name: str,
                 collection_name: str):
        """Initialize MongoDB connection and collection"""
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.documents_collection = self.db[collection_name]
    
    def add_document(self, file_path: Path, filename: str, splits_ids: List[str], 
                     session_id: Optional[str] = None) -> str:
        document_entry = {
            "file_path": str(file_path),
            "filename": filename,
            "document_splits": splits_ids,
            "session_id": session_id
        }
        
        document_id = self.documents_collection.insert_one(document_entry).inserted_id
        return str(document_id)
    
    def get_documents(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        documents = list(self.documents_collection.find({"session_id": session_id}))
        return documents
    
    def get_document_names(self, session_id: Optional[str] = None) -> List[str]:
        documents = self.get_documents(session_id)
        return [doc["filename"] for doc in documents]
    
    def delete_documents(self, session_id: Optional[str] = None) -> int:
        result = self.documents_collection.delete_many({"session_id": session_id})
        return result.deleted_count 