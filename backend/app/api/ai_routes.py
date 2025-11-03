from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import generate_ai_response

router = APIRouter(prefix="/ai", tags=["AI"])

class AIRequest(BaseModel):
    prompt: str

@router.post("/chat")
def chat_with_ai(request: AIRequest):
    response = generate_ai_response(request.prompt)
    if response.startswith("Error"):
        raise HTTPException(status_code=500, detail=response)
    return {"response": response}
