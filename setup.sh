#!/bin/bash

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies using Poetry
echo "Installing dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp env.example .env
    echo "Please edit the .env file to add your OpenAI API key."
fi

echo "Setup complete! You can now run the application with:"
echo "poetry run uvicorn src.main:app --reload" 