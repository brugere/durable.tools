#!/bin/bash

# Copy production database from VPS to local environment
set -e

# Load repo-local defaults if available
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "$0")/.." && pwd)")"
if [[ -f "$REPO_ROOT/scripts/deploy.env" ]]; then
  source "$REPO_ROOT/scripts/deploy.env"
fi

# Default values
HOST="${DEPLOY_HOST:-}"
USER="${DEPLOY_USER:-debian}"
DEST="${DEPLOY_PATH:-/opt/durable.tools}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--host) HOST="${2:-}"; shift 2 ;;
    -u|--user) USER="${2:-}"; shift 2 ;;
    -p|--path) DEST="${2:-}"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 2 ;;
  esac
done

if [[ -z "${HOST:-}" ]]; then
  echo "Error: --host is required (or set DEPLOY_HOST in scripts/deploy.env)"
  echo "Usage: $0 --host HOST [--user USER] [--path /opt/durable.tools]"
  exit 2
fi

echo "🗄️  Copying production database from $USER@$HOST:$DEST..."

# Create local duckdb directory if it doesn't exist
mkdir -p "$REPO_ROOT/backend/duckdb"

# Copy the database file from VPS
echo "📥 Downloading database file..."
scp -o BatchMode=yes -o StrictHostKeyChecking=accept-new \
    "$USER@$HOST:$DEST/duckdb-data/washing_machines.duckdb" \
    "$REPO_ROOT/backend/duckdb/washing_machines.duckdb"

if [ $? -eq 0 ]; then
    echo "✅ Database copied successfully!"
    echo "🗄️  Local database: $REPO_ROOT/backend/duckdb/washing_machines.duckdb"
    echo "🚀 You can now run: docker compose -f docker-compose.local.yml up"
else
    echo "❌ Failed to copy database"
    echo "💡 Make sure the VPS has the database file at: $DEST/duckdb-data/washing_machines.duckdb"
    echo "💡 Or check if the database is stored in a different location on the VPS"
    exit 1
fi
