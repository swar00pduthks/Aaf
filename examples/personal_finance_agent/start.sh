#!/bin/bash

echo "=================================="
echo "Personal Finance Agent - Full Stack"
echo "=================================="
echo ""
echo "Starting backend and frontend..."
echo ""

# Start backend in background
echo "Starting backend API (port 5001)..."
cd "$(dirname "$0")"
python finance_api.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Start frontend
echo "Starting frontend (port 5000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=================================="
echo "✅ Full stack running!"
echo "=================================="
echo ""
echo "🌐 Frontend: http://localhost:5000"
echo "🔌 Backend:  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=================================="

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
