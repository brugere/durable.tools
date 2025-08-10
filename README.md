# Durable Tools

## Project Overview

**Durable Tools** is a web application designed to help users search and discover the most repairable machines available on the market. The project leverages open data from [data.gouv.fr](https://www.data.gouv.fr/) to provide up-to-date information about products, with a focus on repairability and sustainability.

## Architecture

The project is structured as a modern web application with the following main components:

```
durable.tools/
├── backend/         # Python FastAPI backend for data ingestion and API
│   ├── app/
│   │   ├── api.py           # API endpoints
│   │   └── main.py          # FastAPI app entrypoint
│   ├── ingest/
│   │   └── fetch_wmdi.py    # Data fetching scripts (e.g., from data.gouv.fr)
│   └── requirements.txt     # Python dependencies
├── frontend/        # Next.js (React) frontend for the user interface
│   ├── app/
│   │   ├── layout.tsx       # Main layout
│   │   └── page.tsx         # Main page
│   ├── components/          # React components (Results, SearchBox, etc.)
│   ├── lib/                 # API client utilities
│   └── public/              # Static assets
├── infra/           # Infrastructure as code (future use)
├── docker-compose.yml       # Multi-service orchestration
└── README.md
```

- **Backend**: Python FastAPI app for ingesting data from data.gouv.fr, processing it, and serving it via a REST API. Includes scripts for fetching and preparing datasets.
- **Frontend**: Next.js (React) app for the user interface, allowing users to search and view datasets and machine repairability information.
- **Docker**: Both backend and frontend are containerized for easy deployment and development.

## Project Goal

The main goal of this project is to provide a user-friendly website where users can search for and compare the most repairable machines available on the market, using open data sources. The platform aims to promote sustainability and informed purchasing decisions.

## Development Status

Below is a checklist of the main development steps, with their current status:

- [x] **Setup Docker deployment**: Docker Compose and Dockerfiles for backend and frontend are configured.
- [x] **Fetch data.gouv.fr API from backend**: Backend can fetch data from data.gouv.fr.
- [x] **Setup UI in React**: Initial React/Next.js UI is in place.
- [x] **Fetch list of available datasets on data.gouv.fr**: UI to display and interact with available datasets is in progress.
- [x] **Filter available datasets** to only get the reparability datasets of washing machines.  
  - [x] Create a directory for raw data (e.g., backend/data/raw/).
  - [x] Write a function to fetch the list of datasets.
  - [x] For each dataset, download the main CSV resource.
  - [x] Save each file locally.
- [x] **Get all data from data.gouv.fr**: Full data ingestion and processing pipeline to be completed.
- [x] **Modelize data fetched into DB service**: Design and implement database models for storing fetched data.
  - [x] **create V0 data model in pg**: stick to data.gouv.fr model as much as possible
  - [x] **load local data into PG**: create a setup script to load data into PG
- [ ] **Make backend use the database to serve the available data**: API endpoints to serve processed data from the database.
  - [ ] **plug database in backend**: move backend api from direct remote api to local database 
  - [ ] **make data searchable**: enhance search engine so UI becomes more versatile
- [ ] **Update frontend to present an appealing view and search over the data available on backend API**: Enhance UI/UX for searching and displaying repairability data.

## Getting Started

### Local Development Environment

For local development with hot reload and direct service access:

```bash
# Using the development helper script (recommended)
npm run dev:start      # Start local environment
npm run dev:stop       # Stop local environment
npm run dev:restart    # Restart local environment
npm run dev:build      # Rebuild and start
npm run dev:logs       # View logs
npm run dev:status     # Show container status
npm run dev:shell      # Open shell in container
npm run dev:clean      # Clean up containers and volumes

# Or using direct docker compose commands
npm run local          # Start local environment
npm run local:build    # Rebuild and start local environment
npm run local:down     # Stop local environment
```

**Local Environment Features:**
- Frontend runs on `http://localhost:3000` with hot reload
- Backend runs on `http://localhost:8000` with auto-reload
- Direct access to services (no Nginx proxy)
- Source code mounted for live editing
- Uses `docker-compose.local.yml`
- Development helper script for easy management

### Production Environment (VPS)

For production deployment on your VPS:

```bash
# Deploy to VPS
npm run deploy

# Or manually with production compose
docker compose -f docker-compose.prod.yml up -d
```

**Production Environment Features:**
- Nginx reverse proxy with SSL/TLS
- Services exposed only internally
- Production-optimized builds
- Uses `docker-compose.prod.yml`

### Development Helper Script

We provide a convenient development helper script (`scripts/dev.sh`) that simplifies local development:

```bash
# From the project root
./scripts/dev.sh start      # Start local environment
./scripts/dev.sh stop       # Stop local environment
./scripts/dev.sh restart    # Restart local environment
./scripts/dev.sh build      # Rebuild and start
./scripts/dev.sh logs       # View logs
./scripts/dev.sh status     # Show container status
./scripts/dev.sh shell <service>  # Open shell in container
./scripts/dev.sh clean      # Clean up containers and volumes
./scripts/dev.sh help       # Show all available commands
```

### Legacy Single Compose (Deprecated)

The original `docker-compose.yml` is kept for backward compatibility but consider using the environment-specific files above.

## Deployment

We provide a small CLI and Git hook to deploy to a VPS.

1) Configure deploy settings

```
cp scripts/deploy.env.example scripts/deploy.env
vi scripts/deploy.env
```

Key values:
- `DEPLOY_HOST` (required): your VPS IP or hostname
- `DEPLOY_USER` (default: `debian`)
- `DEPLOY_PATH` (default: `/opt/durable.tools`)
- `DEPLOY_DOMAIN` (optional): used for HTTPS checks
- `DEPLOY_BRANCH` (default: `main`): auto-deploy only on this branch

2) Hooks path (already set in this repo; run if needed)

```
git config core.hooksPath .githooks
```

3) Manual deploy

```
./scripts/deploy.sh --host $DEPLOY_HOST --user $DEPLOY_USER --domain $DEPLOY_DOMAIN
```

4) Auto-deploy on commit to `main`

The post-commit hook deploys automatically on `main`. To skip for a commit:

```
git commit -m "feat: something [skip deploy]"
```

Options:
- `--no-cache` – rebuild images from scratch
- `--pull` – pull base images before build
- `--services "frontend backend"` – build specific services

## Contributing

Contributions are welcome! Please open issues or pull requests for suggestions, bug reports, or improvements.

## License

This project is licensed under the MIT License. 