#!/bin/bash
# Start both backend and frontend in dev container

echo "🚀 Starting Modelo 720 Development Environment..."
echo ""

# Start backend in background
echo "📦 Starting Backend API on port 8000..."
cd /workspace/backend
python run.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 3

# Start frontend in background
echo "🎨 Starting Frontend Dev Server on port 5173..."
cd /workspace/frontend
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started!"
echo ""
echo "📍 Services:"
echo "   - Backend API:  http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - Frontend:     http://localhost:5173"
echo ""
echo "💡 Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT TERM

# Keep script running
wait
