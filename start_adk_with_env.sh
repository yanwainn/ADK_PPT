#!/bin/bash

echo "🚀 Starting ADK Server with Environment Variables..."

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "🔑 Loading environment variables from .env..."
    export $(cat .env | xargs)
    echo "✅ GOOGLE_API_KEY loaded: ${GOOGLE_API_KEY:0:20}..."
else
    echo "⚠️ No .env file found, API features may not work"
fi

# Activate virtual environment
source agentic-venv/bin/activate

# Change to adk-evaluation directory
cd adk-evaluation

# Start ADK server with environment variables
echo "🤖 Starting ADK server with Gemini API access..."
adk web --port 8001

echo "✅ ADK server started successfully!" 