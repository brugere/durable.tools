#!/bin/bash

# Setup and run local development environment with real data
set -e

echo "🚀 Setting up local development environment with real washing machine data..."

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check if Python dependencies are installed
if [ ! -d "backend/.venv" ] && [ ! -d "backend/venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Python virtual environment already exists"
fi

# Activate virtual environment
if [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
elif [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

# Check if database exists and has data
if [ ! -f "backend/duckdb/washing_machines.duckdb" ]; then
    echo "🗄️  Setting up local database with washing machine data..."
    cd backend
    python setup_local_db.py
    cd ..
    echo "✅ Database setup completed!"
else
    echo "✅ Database already exists"
fi

# Start the local development environment
echo "🐳 Starting local development environment..."
docker compose -f docker-compose.local.yml up --build

echo "🎉 Local environment is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
