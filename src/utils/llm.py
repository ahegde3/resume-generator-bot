from typing import List, Dict, Any, Optional
from src.utils.config import get_settings
import os
from pathlib import Path
import mimetypes
import PyPDF2
import docx
import csv
import json
import aiofiles

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import tiktoken

class LLMHandler:
    """
    Handler for LLM interactions using LangChain with support for multiple providers.
    """
    def __init__(self, provider: Optional[str] = None):
        self.settings = get_settings()
        self.provider = provider or self.settings.default_llm_provider
        self._initialize_model()
        self._initialize_tokenizer()
    
    def _initialize_model(self):
        """Initialize the appropriate LLM model based on settings."""
        if self.provider == "openai":
            self.model = init_chat_model(
                self.settings.openai_model_name,
                api_key=self.settings.openai_api_key
            )
        elif self.provider == "claude":
            self.model = init_chat_model(
                self.settings.anthropic_model_name,
                api_key=self.settings.anthropic_api_key
            )
        elif self.provider == "gemini":
            # Use ChatGoogleGenerativeAI directly instead of init_chat_model
            self.model = ChatGoogleGenerativeAI(
                model=self.settings.gemini_model_name,
                google_api_key=self.settings.gemini_api_key
            )
        else:
            # Default to OpenAI if provider not recognized
            self.provider = "openai"  # Set to default
            self.model = init_chat_model(
                self.settings.openai_model_name,
                api_key=self.settings.openai_api_key
            )
    
    def _initialize_tokenizer(self):
        """Initialize tokenizer for token counting."""
        try:
            # Use tiktoken for OpenAI models (works for most use cases)
            if self.provider == "openai":
                self.tokenizer = tiktoken.encoding_for_model(self.settings.openai_model_name)
            else:
                # Default to cl100k_base for non-OpenAI models (approximate)
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback if tiktoken fails
            self.tokenizer = None
    
    def switch_provider(self, provider: str) -> bool:
        """
        Switch to a different LLM provider.
        
        Args:
            provider: The provider to switch to ("openai", "claude", or "gemini")
            
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if provider not in ["openai", "claude", "gemini"]:
            return False
            
        if provider == self.provider:
            return True  # Already using this provider
            
        self.provider = provider
        self._initialize_model()
        self._initialize_tokenizer()
        return True
    
    def get_current_provider(self) -> str:
        """Get the name of the currently active provider."""
        return self.provider
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using the appropriate tokenizer."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback approximation (1 token ≈ 4 characters for English text)
            return len(text) // 4
    
    async def extract_file_content(self, file_path: str, max_length: int = 10000) -> str:
        """
        Extract content from a file based on its type.
        
        Args:
            file_path: Path to the file
            max_length: Maximum length of content to extract
            
        Returns:
            String containing the extracted content
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Text files
        if mime_type in ['text/plain', 'text/markdown', 'application/json', 'text/html', 'text/css', 'text/javascript'] or file_path.suffix in ['.txt', '.md', '.json', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.ts', '.tsx', '.jsx']:
            async with aiofiles.open(file_path, 'r', errors='ignore') as f:
                content = await f.read()
                return content[:max_length]
        
        # PDF files
        elif mime_type == 'application/pdf' or file_path.suffix == '.pdf':
            try:
                text = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text.append(page.extract_text())
                        
                        # Check if we've reached the max length
                        content = "\n\n".join(text)
                        if len(content) >= max_length:
                            return content[:max_length]
                            
                return "\n\n".join(text)
            except Exception as e:
                return f"Error extracting PDF content: {str(e)}"
        
        # Word documents
        elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] or file_path.suffix in ['.doc', '.docx']:
            try:
                doc = docx.Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])
                return content[:max_length]
            except Exception as e:
                return f"Error extracting Word document content: {str(e)}"
        
        # CSV files
        elif mime_type == 'text/csv' or file_path.suffix == '.csv':
            try:
                rows = []
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        rows.append(",".join(row))
                        if len("\n".join(rows)) >= max_length:
                            break
                return "\n".join(rows)[:max_length]
            except Exception as e:
                return f"Error extracting CSV content: {str(e)}"
        
        # Images and other binary files
        else:
            return f"[File content not extracted: {file_path.name} is a {mime_type or 'binary'} file]"
    
    async def get_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1000, 
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Get a chat completion from the LLM using LangChain.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in the response
            temperature: Temperature for response generation
            
        Returns:
            Dictionary with response message and usage statistics
        """
        try:
            # Convert messages to LangChain format
            lc_messages = []
            prompt_tokens = 0
            
            for msg in messages:
                content = msg["content"]
                prompt_tokens += self._count_tokens(content)
                
                if msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=content))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=content))
            
            # Configure model parameters
            model = self.model.with_config(
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Create chain and invoke
            chain = model | StrOutputParser()
            response_text = await chain.ainvoke(lc_messages)
            
            # Count completion tokens
            completion_tokens = self._count_tokens(response_text)
            
            # Format response similar to the original format
            return {
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }
        except Exception as e:
            raise Exception(f"Error communicating with LLM: {str(e)}")

# Create a singleton instance
llm_handler = LLMHandler() 