from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.chain import get_chain

app = FastAPI(title="Joke Generator API")

class JokeRequest(BaseModel):
    topic: str

class JokeResponse(BaseModel):
    setup: str
    punchline: str

@app.post("/documents", response_model=JokeResponse)
async def generate_joke(request: JokeRequest):
    try:
        chain = get_chain()
        result = chain.invoke({"topic": request.topic})
        return JokeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/documents")
async def delete_documents():
    # Placeholder for delete functionality
    return {"message": "Delete functionality not implemented."}

@app.get("/documents")
async def get_documents():
    # Placeholder for get functionality
    return {"message": "Get functionality not implemented."}

@app.get("/messages")
async def get_messages():
    # Placeholder for get messages functionality
    return {"message": "Get messages functionality not implemented."}

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
