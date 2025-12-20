#!/bin/bash
# Physical AI Textbook Platform - Unified Launch Script
# Feature: 003-better-auth + Full Platform Startup
#
# This script starts both the backend (FastAPI) and frontend (Docusaurus) servers
# and performs health checks to ensure everything is running correctly.

set -e  # Exit on any error

echo "🚀 Starting Physical AI Textbook Platform..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Store the root directory
ROOT_DIR=$(pwd)

# Create logs directory if it doesn't exist
mkdir -p logs

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "${GREEN}✅ Backend stopped${NC}"
    fi
    exit 0
}

# Trap Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM EXIT

# 1. Start Backend in Background
echo ""
echo "${BLUE}🔌 Launching Backend (FastAPI on Port 8000)...${NC}"
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > "$ROOT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$ROOT_DIR"

# 2. Verify Backend Health
echo "${YELLOW}⏳ Waiting for Backend to be healthy...${NC}"
for i in {1..10}; do
    sleep 1
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "${GREEN}✅ Backend is ONLINE at http://localhost:8000${NC}"
        echo "${GREEN}   📚 API Docs: http://localhost:8000/docs${NC}"
        break
    fi

    if [ $i -eq 10 ]; then
        echo "${RED}❌ Backend failed to start after 10 seconds.${NC}"
        echo "${RED}   Check logs/backend.log for errors.${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi

    echo "   Attempt $i/10..."
done

# 3. Start Frontend
echo ""
echo "${BLUE}🎨 Launching Frontend (Docusaurus on Port 3000)...${NC}"
echo "${GREEN}👉 Access the platform at: http://localhost:3000${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Start frontend (this will run in foreground)
npm start

# Note: The cleanup function will be called automatically when npm start is terminated
