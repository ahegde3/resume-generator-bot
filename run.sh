#!/bin/bash

# Run the application using Poetry
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 