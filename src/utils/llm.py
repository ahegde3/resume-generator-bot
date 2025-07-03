import openai
from typing import List, Dict, Any
from src.utils.config import get_settings

class LLMHandler:
    """
    Handler for LLM interactions.
    """
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)
    
    async def get_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1000, 
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Get a chat completion from the LLM.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return {
                "message": {
                    "role": response.choices[0].message.role,
                    "content": response.choices[0].message.content
                },
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"Error communicating with LLM: {str(e)}")

# Create a singleton instance
llm_handler = LLMHandler() 