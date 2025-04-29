from typing import Annotated
from fastapi import FastAPI, HTTPException, UploadFile, Header, status
from pydantic import BaseModel
from pathlib import Path
from config.settings import DOCUMENTS_DIR

from src.file_handler import FileHandler
from src.vector_store import VectorStore
from src.document_store import DocumentStore
from src.assistant import PDFAssistant

class ChatRequest(BaseModel):
    message: str

app = FastAPI(title="PDF Assistant API")

file_handler = FileHandler(DOCUMENTS_DIR)
vector_store = VectorStore(persist_directory="./chroma_langchain_db")
document_store = DocumentStore()
assistant = PDFAssistant()

@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def post_documents(file: UploadFile, session_id: Annotated[str | None, Header()] = None):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    file_path = await file_handler.save_file(content, extension="pdf")

    # Add document to vector store
    splits_ids = await vector_store.add_document(file_path, session_id=session_id)
    print(f"Document splits: {splits_ids}")

    # Add document to MongoDB through DocumentStore
    document_id = document_store.add_document(
        file_path=file_path,
        filename=file.filename,
        splits_ids=splits_ids,
        session_id=session_id
    )
    
    return {"message": "Document uploaded successfully", "id": document_id}, 201
    
@app.delete("/documents")
async def delete_documents(session_id: Annotated[str | None, Header()] = None):
    print(f"Deleting documents for session: {session_id}")
    documents = document_store.get_documents(session_id)
    
    for doc in documents:
        file_path = Path(doc["file_path"])
        file_handler.delete_file(file_path)
        
        if "document_splits" in doc:
            vector_store.delete_documents(doc["document_splits"])
    
    deleted_count = document_store.delete_documents(session_id)
    
    return {"message": f"Successfully deleted {deleted_count} documents"}

@app.get("/documents")
async def get_documents(session_id: Annotated[str | None, Header()] = None):
    print(f"Getting documents for session: {session_id}")
    document_names = document_store.get_document_names(session_id)
    return {"documents": document_names}

@app.get("/messages")
async def get_messages(session_id: Annotated[str | None, Header()] = None):
    messages = assistant.get_message_history(session_id)
    return {"messages": messages}

@app.delete("/messages")
async def delete_messages(session_id: Annotated[str | None, Header()] = None):
    assistant.delete_message_history(session_id)
    return {"message": "Messages deleted successfully"}

@app.post("/chat")
async def chat(request: ChatRequest, session_id: Annotated[str | None, Header()] = None):
    assistante_message = assistant.ask(request.message, session_id)
    print("response", assistante_message)
    return assistante_message
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
