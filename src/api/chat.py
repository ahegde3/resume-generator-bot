from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict
import openai
from src.utils.config import get_settings, Settings
from src.utils.llm import llm_handler
from src.models.chat import Message, ChatSession

router = APIRouter(tags=["chat"])

# In-memory storage for chat sessions
chat_sessions = {}

class MessageRequest(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageRequest]
    session_id: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    message: Dict[str, str]
    usage: Dict[str, int]
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, settings: Settings = Depends(get_settings)):
    """
    Send a message to the LLM model and get a response.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )
    
    try:
        # Get or create a chat session
        session_id = request.session_id
        if session_id and session_id in chat_sessions:
            chat_session = chat_sessions[session_id]
        else:
            chat_session = ChatSession()
            chat_sessions[chat_session.id] = chat_session
            session_id = chat_session.id
        
        # Add user messages to the session
        for msg in request.messages:
            if msg.role == "user":  # Only add new user messages
                chat_session.add_message(msg.role, msg.content)
        
        # Get message history for the LLM
        message_history = chat_session.get_message_history()
        
        # Call the LLM
        response = await llm_handler.get_chat_completion(
            messages=message_history,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Add the assistant's response to the session
        chat_session.add_message(
            response["message"]["role"], 
            response["message"]["content"]
        )
        
        # Return the response with the session ID
        return ChatResponse(
            message=response["message"],
            usage=response["usage"],
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error communicating with LLM: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(session_id: str):
    """
    Get a chat session by ID.
    """
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {session_id} not found"
        )
    
    return chat_sessions[session_id] 