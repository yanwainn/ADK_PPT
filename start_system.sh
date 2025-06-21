#!/bin/bash

echo "🚀 Starting Enhanced AI Presentation System..."

# Kill any existing servers
echo "🔄 Stopping existing servers..."
pkill -f "serve_static.py" 2>/dev/null || true
pkill -f "adk web" 2>/dev/null || true
sleep 2

# Start static file server
echo "📁 Starting static file server..."
cd adk-evaluation
python serve_static.py &
STATIC_PID=$!
echo "✅ Static server started (PID: $STATIC_PID) on http://localhost:8002"

# Start ADK server
echo "🤖 Starting ADK server..."
source adk-venv/bin/activate
adk web --port 8001 &
ADK_PID=$!
echo "✅ ADK server started (PID: $ADK_PID) on http://localhost:8001"

# Wait a moment for servers to start
sleep 3

echo ""
echo "🎉 System Ready!"
echo "📊 ADK Web Interface: http://localhost:8001/dev-ui/"
echo "📄 Generated Presentations: http://localhost:8002/presentations/"
echo ""
echo "💡 To stop servers: pkill -f serve_static && pkill -f adk"
echo ""

# Keep script running
wait 