from fastapi import FastAPI
from .api import router as api_router

app = FastAPI(
    title="Durable.tools API",
    version="0.1.0",
)

app.include_router(api_router, prefix="/v1")
