from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Message(BaseModel):
    """
    Model for a chat message.
    """
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatSession(BaseModel):
    """
    Model for a chat session.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    title: Optional[str] = None

    def add_message(self, role: str, content: str) -> Message:
        """
        Add a message to the chat session.
        """
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_message_history(self) -> List[dict]:
        """
        Get the message history in a format suitable for the OpenAI API.
        """
        return [{"role": msg.role, "content": msg.content} for msg in self.messages] 