# backend/app/routes/chat_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, ai_chat
from app.auth.oauth2 import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/send", response_model=schemas.ChatMessageResponse)
def send_message(
    msg: schemas.ChatMessageCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Save user message
    user_message = models.ChatMessage(
        user_id=current_user.id, sender="user", message=msg.message
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Get AI response
    ai_reply = ai_chat.get_ai_response(msg.message)

    ai_message = models.ChatMessage(
        user_id=current_user.id, sender="ai", message=ai_reply
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return ai_message


@router.get("/history", response_model=list[schemas.ChatMessageResponse])
def get_chat_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == current_user.id)
        .order_by(models.ChatMessage.timestamp.asc())
        .all()
    )
    return messages

# backend/app/routes/chat_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database, models, ai_chat
from app.auth.oauth2 import get_current_user

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.post("/send")
def send_message(payload: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    user_message = payload.get("message")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    db.add(models.ChatMessage(user_id=current_user.id, role="user", content=user_message))
    db.commit()

    ai_reply = ai_chat.generate_ai_response(db, current_user.id, user_message)
    return {"reply": ai_reply}
