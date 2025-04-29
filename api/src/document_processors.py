from pathlib import Path
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

class DocumentProcessor:
    """Class for processing document files."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
    
    async def process(self, file_path: Path, session_id: Optional[str] = None) -> List:
        """Process a document file and return the processed chunks."""
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
            
        document_splits = self.text_splitter.split_documents(pages)
        
        for i, doc in enumerate(document_splits):
            if not isinstance(doc.metadata, dict):
                doc.metadata = {}
            
            doc.metadata["session_id"] = session_id
            doc.metadata["source"] = str(file_path)
            doc.metadata["page"] = doc.metadata.get("page", i)
        
        return document_splits 