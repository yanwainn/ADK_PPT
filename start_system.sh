#!/bin/bash

echo "🚀 Starting Enhanced AI Presentation System..."

# Kill any existing servers
echo "🔄 Stopping existing servers..."
pkill -f "serve_static.py" 2>/dev/null || true
pkill -f "adk web" 2>/dev/null || true
sleep 2

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "🔑 Loading environment variables from .env..."
    export $(cat .env | xargs)
    echo "✅ GOOGLE_API_KEY loaded: ${GOOGLE_API_KEY:0:20}..."
else
    echo "⚠️ No .env file found, API features may not work"
fi

# Start static file server
echo "📁 Starting static file server..."
cd adk-evaluation
python serve_static.py &
STATIC_PID=$!
echo "✅ Static server started (PID: $STATIC_PID) on http://localhost:8002"

# Start ADK server with environment variables
echo "🤖 Starting ADK server with API configuration..."
source ../agentic-venv/bin/activate
export GOOGLE_API_KEY=${GOOGLE_API_KEY}
adk web --port 8001 &
ADK_PID=$!
echo "✅ ADK server started (PID: $ADK_PID) on http://localhost:8001"

# Wait a moment for servers to start
sleep 3

echo ""
echo "🎉 System Ready!"
echo "📊 ADK Web Interface: http://localhost:8001"
echo "📄 Generated Presentations: http://localhost:8002/presentations/"
echo "🔑 Gemini API: $([ -n "$GOOGLE_API_KEY" ] && echo "✅ Configured" || echo "❌ Not configured")"
echo ""
echo "💡 To stop servers: pkill -f serve_static && pkill -f adk"

# Keep script running to show any immediate errors
sleep 5

# Check if servers are still running
if ! pgrep -f "serve_static" > /dev/null; then
    echo "⚠️ Static server may have crashed"
fi

if ! pgrep -f "adk web" > /dev/null; then
    echo "⚠️ ADK server may have crashed"
fi 