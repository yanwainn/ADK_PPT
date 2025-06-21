#!/bin/bash

echo "🚀 Starting PowerPoint Generation Servers..."

# Navigate to the correct directory
cd "$(dirname "$0")"

# Activate ADK environment
source adk-venv/bin/activate

# Start static file server in background
echo "📁 Starting static file server on port 8002..."
python serve_static.py > static_server.log 2>&1 &
STATIC_PID=$!

# Wait a moment for static server to start
sleep 2

# Start ADK server
echo "🤖 Starting ADK server on port 8001..."
adk web --port 8001 > adk.log 2>&1 &
ADK_PID=$!

# Wait for servers to start
sleep 5

echo ""
echo "✅ Servers started successfully!"
echo ""
echo "🌐 ADK Web UI:      http://localhost:8001/dev-ui/"
echo "📁 Static Files:    http://localhost:8002/"
echo "🎯 Agent:           simple_ppt_agent"
echo ""
echo "📊 Generated presentations will be available at:"
echo "   http://localhost:8002/presentations/[filename].html"
echo ""
echo "🛑 To stop servers: pkill -f 'adk web' && pkill -f 'serve_static.py'"
echo ""

# Keep script running
echo "Press Ctrl+C to stop all servers..."
trap 'echo "Stopping servers..."; kill $STATIC_PID $ADK_PID 2>/dev/null; exit' INT
wait 