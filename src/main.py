from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
from pathlib import Path

from src.api.chat import router as chat_router
from src.utils.config import get_settings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="LLM Chatbot",
    description="A simple chatbot application that allows you to interact with an LLM model.",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(chat_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the main chat interface.
    """
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "LLM Chatbot"}
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True) 