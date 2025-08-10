# Local Development Setup with Real Data

This guide explains how to set up your local development environment to use the same real washing machine data as your production VPS deployment.

## Problem

By default, your local deployment shows mocked data instead of the real washing machine database. This happens because:
1. The local database file doesn't exist
2. The API falls back to mock data when the database is unavailable

## Solutions

You have two options to get real data locally:

### Option 1: Copy Production Database (Recommended)

This gives you the exact same data as your VPS:

```bash
# Copy the database from your VPS
./scripts/copy-prod-db.sh --host YOUR_VPS_IP

# Or if you have deploy.env configured:
./scripts/copy-prod-db.sh
```

### Option 2: Build Database from Raw CSV Files

This recreates the database from your local CSV files:

```bash
# Set up the database with local CSV data
./scripts/setup-db.sh
```

## Quick Start

1. **Copy the production database:**
   ```bash
   ./scripts/copy-prod-db.sh --host 51.210.241.37
   ```

2. **Start the local environment:**
   ```bash
   docker compose -f docker-compose.local.yml up --build
   ```

3. **Access your app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## All-in-One Script

For a complete setup, you can use:

```bash
./scripts/setup-local.sh
```

This script will:
- Set up Python dependencies
- Create the database (if needed)
- Start the local environment

## File Structure

After setup, your local database will be at:
```
backend/duckdb/washing_machines.duckdb
```

## Troubleshooting

### Database not found
- Make sure you've run one of the setup scripts
- Check that `backend/duckdb/washing_machines.duckdb` exists

### Permission denied
- Make sure the scripts are executable: `chmod +x scripts/*.sh`

### Python dependencies missing
- The setup scripts will create a virtual environment and install dependencies automatically

### VPS connection issues
- Check your SSH key is configured for the VPS
- Verify the VPS IP and path in your `deploy.env` file

## Data Sources

The washing machine data comes from:
- **Raw CSV files**: `backend/data/raw/*.csv` (French government data)
- **Production database**: Copied from your VPS deployment
- **Generated database**: Built locally from CSV files

## Updating Data

To get fresh data from your VPS:
```bash
./scripts/copy-prod-db.sh
```

To rebuild from CSV files:
```bash
./scripts/setup-db.sh
```
