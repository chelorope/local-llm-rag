from typing import Annotated
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import FastAPI, HTTPException, UploadFile, Header, Request
from pymongo import MongoClient
import os
from pydantic import BaseModel
from pathlib import Path
from config.settings import DOCUMENTS_DIR, MONGO_URI, MONGO_DB_NAME, MONGO_DOCUMENTS_COLLECTION_NAME
import uuid

from src.chain import get_chain

class ChatRequest(BaseModel):
    message: str

app = FastAPI(title="Joke Generator API")

documents_dir = Path(DOCUMENTS_DIR)
embeddings = OllamaEmbeddings(model="llama3.2")
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]
collection = db[MONGO_DOCUMENTS_COLLECTION_NAME]

@app.post("/documents")
async def post_documents(file: UploadFile, session_id: Annotated[str | None, Header()] = None):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        file_path = documents_dir / f"{uuid.uuid4().hex}.pdf"
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        document_splits = text_splitter.split_documents(pages)
        splits_ids = vector_store.add_documents(documents=document_splits)
        print(f"Document splits: {splits_ids}")

        # Create document entry
        document_entry = {
            "file_path": str(file_path),
            "filename": file.filename,
            "document_splits": splits_ids,
            "session_id": session_id
        }
        
        # Insert into MongoDB
        document_id = collection.insert_one(document_entry).inserted_id
        return {"message": "Document uploaded successfully", "id": str(document_id)}, 201
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/documents")
async def delete_documents():
    # Placeholder for delete functionality
    return {"message": "Delete functionality not implemented."}

@app.get("/documents")
async def get_documents(session_id: Annotated[str | None, Header()] = None):
    
    # Placeholder for get functionality
    return {"documents": []}

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
