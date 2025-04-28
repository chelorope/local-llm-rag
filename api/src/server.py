from typing import Annotated
from fastapi import FastAPI, HTTPException, UploadFile, Header, status
import os
from pydantic import BaseModel
from pathlib import Path
from config.settings import DOCUMENTS_DIR

from src.chain import get_chain
from src.file_handler import FileHandler
from src.vector_store import VectorStore
from src.document_store import DocumentStore

class ChatRequest(BaseModel):
    message: str

app = FastAPI(title="Joke Generator API")

file_handler = FileHandler(DOCUMENTS_DIR)
vector_store = VectorStore(persist_directory="./chroma_langchain_db")
document_store = DocumentStore()

@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def post_documents(file: UploadFile, session_id: Annotated[str | None, Header()] = None):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        content = await file.read()
        file_path = await file_handler.save_file(content, extension="pdf")

        # Add document to vector store
        splits_ids = await vector_store.add_document(file_path)
        print(f"Document splits: {splits_ids}")

        # Add document to MongoDB through DocumentStore
        document_id = document_store.add_document(
            file_path=file_path,
            filename=file.filename,
            splits_ids=splits_ids,
            session_id=session_id
        )
        
        return {"message": "Document uploaded successfully", "id": document_id}, 201
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/documents")
async def delete_documents(session_id: Annotated[str | None, Header()] = None):
    try:
        print(f"Deleting documents for session: {session_id}")
        documents = document_store.get_documents(session_id)
        
        for doc in documents:
            file_path = Path(doc["file_path"])
            file_handler.delete_file(file_path)
            
            if "document_splits" in doc:
                vector_store.delete_documents(doc["document_splits"])
        
        deleted_count = document_store.delete_documents(session_id)
        
        return {"message": f"Successfully deleted {deleted_count} documents"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents(session_id: Annotated[str | None, Header()] = None):
    print(f"Getting documents for session: {session_id}")
    try:
        document_names = document_store.get_document_names(session_id)
        return {"documents": document_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages")
async def get_messages():
    # Placeholder for get messages functionality
    return {"messages": []}

@app.delete("/messages")
async def delete_messages():
    # Placeholder for delete messages functionality
    return {"message": "Delete messages functionality not implemented."}

@app.post("/chat")
async def chat(request: ChatRequest):
    message = request.model_dump_json()['message']
    chain = get_chain()
    try:
        response = chain.invoke({"text": message})
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Chat functionality not implemented."}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
