from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict
import openai
from src.utils.config import get_settings, Settings
from src.utils.llm import llm_handler
from src.models.chat import Message, ChatSession
from src.utils.prompts import get_system_prompt, SYSTEM_PROMPTS
import json
import os
from pathlib import Path

router = APIRouter(tags=["chat"])

# In-memory storage for chat sessions
chat_sessions = {}

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class MessageRequest(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageRequest]
    session_id: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    prompt_type: Optional[str] = None

class ChatResponse(BaseModel):
    message: Dict[str, str]
    usage: Dict[str, int]
    session_id: str

class FileUploadResponse(BaseModel):
    filename: str
    file_id: str
    session_id: str
    message: str

class PromptTypeRequest(BaseModel):
    prompt_type: str

class PromptTypeResponse(BaseModel):
    session_id: str
    prompt_type: str
    message: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, settings: Settings = Depends(get_settings)):
    """
    Send a message to the LLM model and get a response.
    """
    
    try:
        # Get or create a chat session
        session_id = request.session_id
        if session_id and session_id in chat_sessions:
            chat_session = chat_sessions[session_id]
            
            # Update prompt type if provided in the request
            if request.prompt_type is not None:
                chat_session.prompt_type = request.prompt_type
        else:
            chat_session = ChatSession()
            # Set prompt type from request or use default
            chat_session.prompt_type = request.prompt_type or settings.default_prompt_type
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

@router.post("/sessions/{session_id}/prompt-type", response_model=PromptTypeResponse)
async def update_prompt_type(session_id: str, request: PromptTypeRequest):
    """
    Update the prompt type for an existing session.
    """
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {session_id} not found"
        )
    
    # Validate prompt type
    if request.prompt_type not in SYSTEM_PROMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prompt type: {request.prompt_type}. Available types: {', '.join(SYSTEM_PROMPTS.keys())}"
        )
    
    # Update prompt type
    chat_session = chat_sessions[session_id]
    chat_session.prompt_type = request.prompt_type
    
    return PromptTypeResponse(
        session_id=session_id,
        prompt_type=request.prompt_type,
        message=f"Prompt type updated to '{request.prompt_type}'"
    )

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    message: Optional[str] = Form(""),
    prompt_type: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings)
):
    """
    Upload a file and optionally process it with the LLM.
    """
    try:
        # Get or create a chat session
        if session_id and session_id in chat_sessions:
            chat_session = chat_sessions[session_id]
            # Update prompt type if provided
            if prompt_type:
                chat_session.prompt_type = prompt_type
        else:
            chat_session = ChatSession()
            # Set prompt type from request or use default
            chat_session.prompt_type = prompt_type or settings.default_prompt_type
            chat_sessions[chat_session.id] = chat_session
            session_id = chat_session.id
        
        # Save the file
        file_id = f"{chat_session.id}_{file.filename}"
        file_path = UPLOAD_DIR / file_id
        
        # Write file content
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            await file.seek(0)  # Reset file pointer for potential reuse
        
        # Add file reference to the chat session
        file_message = f"Uploaded file: {file.filename}"
        if message:
            file_message = f"{message}\n\nFile: {file.filename}"
        
        # Store the file in the session
        chat_session.add_file(file.filename, str(file_path), message)
        
        # Add a user message about the file
        chat_session.add_message("user", file_message)
        
        # Process the file with the LLM if there's a message
        if message:
            # Get file content based on type
            file_content = await llm_handler.extract_file_content(file_path)
            
            # Create a message with the file content
            prompt = f"{message}\n\nFile content:\n{file_content}"
            
            # Get LLM response
            message_history = chat_session.get_message_history()
            
            # Replace the last user message with the prompt that includes file content
            if message_history and message_history[-1]["role"] == "user":
                message_history[-1]["content"] = prompt
            
            # Get LLM response
            response = await llm_handler.get_chat_completion(
                messages=message_history,
                max_tokens=settings.max_tokens_default,
                temperature=settings.temperature_default
            )
            
            # Add the assistant's response to the session
            chat_session.add_message(
                response["message"]["role"], 
                response["message"]["content"]
            )
        
        return FileUploadResponse(
            filename=file.filename,
            file_id=file_id,
            session_id=session_id,
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
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

@router.get("/prompt-types", response_model=Dict[str, str])
async def get_prompt_types():
    """
    Get all available prompt types.
    """
    return SYSTEM_PROMPTS 