# LLM Chatbot

A simple chatbot application that allows you to interact with an LLM model.

## Features

- Chat interface to communicate with an LLM model
- FastAPI backend for handling requests
- Support for OpenAI's API

## Setup

1. Clone this repository
2. Install dependencies using Poetry:

   ```
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```
   poetry run uvicorn src.main:app --reload
   ```
5. Open your browser and navigate to `http://localhost:8000`

## Project Structure

- `src/` - Main application code
  - `api/` - API endpoints
  - `models/` - Data models
  - `utils/` - Utility functions
- `static/` - Static assets (CSS, JS)
- `templates/` - HTML templates
