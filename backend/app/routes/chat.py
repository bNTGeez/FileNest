from fastapi import APIRouter, Depends, HTTPException
from app.utils.gpt import generate_response
from app.auth import get_current_user
from app import models
from pydantic import BaseModel

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

@router.post("/chat")
async def chat(
    chat_message: ChatMessage,
    current_user: models.User = Depends(get_current_user)
):
    try:
        response = generate_response(chat_message.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 