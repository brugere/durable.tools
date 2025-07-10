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
- [ ] **Filter available datasets to only get the reparability datasets of washing machines.  
- [ ] **Get all data from data.gouv.fr**: Full data ingestion and processing pipeline to be completed.
- [ ] **Modelize data fetched into DB service**: Design and implement database models for storing fetched data.
- [ ] **Make backend use the database to serve the available data**: API endpoints to serve processed data from the database.
- [ ] **Update frontend to present an appealing view and search over the data available on backend API**: Enhance UI/UX for searching and displaying repairability data.

## Getting Started

1. **Clone the repository**
2. **Start the stack**:
   ```sh
   docker-compose up --build
   ```
3. **Access the app**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)

## Contributing

Contributions are welcome! Please open issues or pull requests for suggestions, bug reports, or improvements.

## License

This project is licensed under the MIT License. 