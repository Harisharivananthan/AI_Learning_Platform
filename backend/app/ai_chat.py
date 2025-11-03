# app/ai_chat.py
import os
import openai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/chat", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str

@router.post("/")
async def chat_with_ai(request: ChatRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an intelligent AI learning assistant."},
                {"role": "user", "content": request.message}
            ]
        )

        return {"reply": response.choices[0].message.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
