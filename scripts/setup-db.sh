#!/bin/bash

# Setup local database with washing machine data
set -e

echo "🗄️  Setting up local database with washing machine data..."

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

# Setup the database
echo "🔧 Loading washing machine data into database..."
cd backend
python setup_local_db.py
cd ..

echo "✅ Database setup completed!"
echo "🗄️  Database file: backend/duckdb/washing_machines.duckdb"
echo "🚀 You can now run: docker compose -f docker-compose.local.yml up"
