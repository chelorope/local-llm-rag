from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from pathlib import Path
import uuid

from src.chain import get_chain, Joke

app = FastAPI(title="Joke Generator API")

class JokeRequest(BaseModel):
    topic: str

@app.post("/documents")
async def post_documents(file: UploadFile):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        documents_dir = Path("documents")
        documents_dir.mkdir(exist_ok=True)
        
        filename = f"{uuid.uuid4()}.pdf"
        file_path = documents_dir / filename
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {"message": "Document uploaded successfully", "filename": filename}, 201
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/documents")
async def delete_documents():
    # Placeholder for delete functionality
    return {"message": "Delete functionality not implemented."}

@app.get("/documents")
async def get_documents():
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
async def chat():
    # Placeholder for chat functionality
    return {"message": "Chat functionality not implemented."}
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
