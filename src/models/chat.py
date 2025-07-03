from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from src.utils.prompts import get_system_prompt

class Message(BaseModel):
    """
    Model for a chat message.
    """
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class FileAttachment(BaseModel):
    """
    Model for a file attachment.
    """
    filename: str
    file_path: str
    message: Optional[str] = None
    upload_time: datetime = Field(default_factory=datetime.now)
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ChatSession(BaseModel):
    """
    Model for a chat session.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []
    files: List[FileAttachment] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    title: Optional[str] = None
    prompt_type: str = "default"

    def add_message(self, role: str, content: str) -> Message:
        """
        Add a message to the chat session.
        """
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def add_file(self, filename: str, file_path: str, message: Optional[str] = None) -> FileAttachment:
        """
        Add a file attachment to the chat session.
        """
        file_attachment = FileAttachment(
            filename=filename,
            file_path=file_path,
            message=message
        )
        self.files.append(file_attachment)
        self.updated_at = datetime.now()
        return file_attachment
    
    def get_message_history(self) -> List[dict]:
        """
        Get the message history in a format suitable for the LLM API.
        Includes system prompt based on the prompt_type.
        """
        history = []
        
        # Add system message based on prompt_type
        system_prompt = get_system_prompt(self.prompt_type)
        history.append({"role": "system", "content": system_prompt})
            
        # Add regular messages
        history.extend([{"role": msg.role, "content": msg.content} for msg in self.messages])
        
        return history 