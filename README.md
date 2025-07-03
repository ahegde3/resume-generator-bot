# Resume Generator LLM Application

A FastAPI application that allows users to interact with LLM models for resume generation and analysis.

## System Prompts

This application supports configuring the LLM's behavior through predefined system prompts. System prompts are instructions given to the LLM that guide its responses and behavior.

### Available Prompt Types

The following prompt types are available:

- `default`: Basic helpful assistant behavior
- `professional`: Formal, detailed responses with professional tone
- `concise`: Brief, to-the-point responses
- `creative`: Imaginative responses with creative perspectives
- `resume_expert`: Specialized in resume writing and career advice
- `technical`: Technical assistant with programming knowledge

### Using Prompt Types

#### Environment Configuration

Set the default prompt type in your `.env` file:

```
DEFAULT_PROMPT_TYPE=resume_expert
```

#### API Usage

1. When starting a new chat session, you can specify the prompt type:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "messages": [{"role": "user", "content": "Help me improve my resume"}],
        "prompt_type": "resume_expert"
    }
)
```

2. Change the prompt type for an existing session:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/sessions/YOUR_SESSION_ID/prompt-type",
    json={"prompt_type": "professional"}
)
```

3. View all available prompt types:

```python
import requests

response = requests.get("http://localhost:8000/api/prompt-types")
prompt_types = response.json()
```

### Creating Custom Prompt Types

To create custom prompt types, edit the `src/utils/prompts.py` file and add your prompt to the `SYSTEM_PROMPTS` dictionary:

```python
SYSTEM_PROMPTS = {
    # ... existing prompts ...

    "your_custom_prompt": """
    Your detailed instructions for the LLM here.
    Multiple lines of text can be included.
    Be specific about the desired behavior.
    """
}
```

## Running the Application

1. Install dependencies:

```
poetry install
```

2. Start the server:

```
poetry run uvicorn src.main:app --reload
```

3. Access the web interface at http://localhost:8000 or use the API endpoints directly.

## Features

- FastAPI backend for handling requests
- Support for multiple LLM providers (OpenAI, Claude, Gemini)
- System prompts for controlling LLM behavior
- File upload and processing
- Chat session management

## Project Structure

- `src/` - Main application code
  - `api/` - API endpoints
  - `models/` - Data models
  - `utils/` - Utility functions and configuration
- `static/` - Static assets (CSS, JS)
- `templates/` - HTML templates
- `uploads/` - Uploaded files storage
