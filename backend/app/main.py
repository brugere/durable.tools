from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router

app = FastAPI(
    title="Durable.tools API",
    version="0.1.0",
)

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend:3000", "http://localhost:3000"],  # Update this if your frontend runs elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v1")
