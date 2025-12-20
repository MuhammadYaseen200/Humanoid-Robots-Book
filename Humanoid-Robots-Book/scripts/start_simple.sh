#!/bin/bash
# Simple Launch Script - No health checks, just start both servers

echo "🚀 Starting Physical AI Textbook Platform (Simple Mode)..."
echo ""

# Start backend in background
echo "🔌 Starting Backend (Port 8000)..."
cd backend
uvicorn src.main:app --reload --port 8000 &
cd ..

# Wait a bit for backend to initialize
echo "⏳ Waiting 10 seconds for backend to initialize..."
sleep 10

# Start frontend (foreground)
echo ""
echo "🎨 Starting Frontend (Port 3000)..."
echo "👉 Navigate to: http://localhost:3000"
echo "👉 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop (you'll need to manually kill backend)"
echo ""

npm start
