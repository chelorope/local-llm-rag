from typing import Annotated
from fastapi import FastAPI, HTTPException, UploadFile, Header, status
from pydantic import BaseModel
from pathlib import Path

from src.factories import ComponentFactory
from config.settings import settings

class ChatRequest(BaseModel):
    message: str

app = FastAPI(title="PDF Assistant API")

file_handler = ComponentFactory.create_file_handler()
vector_store = ComponentFactory.create_vector_store()
document_store = ComponentFactory.create_document_store()
assistant = ComponentFactory.create_assistant()
document_processor = ComponentFactory.create_document_processor()

SUPPORTED_FILE_EXTENSION = "pdf"

@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def post_documents(file: UploadFile, session_id: Annotated[str | None, Header()] = None):
    if not file.filename.endswith(SUPPORTED_FILE_EXTENSION):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    file_path = await file_handler.save_file(content, extension=SUPPORTED_FILE_EXTENSION)
    document_splits = await document_processor.process(file_path, session_id)
    splits_ids = await vector_store.add_document(document_splits)

    document_id = document_store.add_document(
        file_path=file_path,
        filename=file.filename,
        splits_ids=splits_ids,
        session_id=session_id
    )
    
    return {"message": "Document uploaded successfully", "id": document_id}
    
@app.delete("/documents")
async def delete_documents(session_id: Annotated[str | None, Header()] = None):
    print(f"Deleting documents for session: {session_id}")
    documents = document_store.get_documents(session_id)
    
    for doc in documents:
        file_path = Path(doc["file_path"])
        await file_handler.delete_file(file_path)
        
        if "document_splits" in doc:
            await vector_store.delete_documents(doc["document_splits"])
    
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
    assistant_message = await assistant.ask(request.message, session_id)
    return assistant_message
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
