from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
from contextlib import asynccontextmanager

from .api import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up washing machine durability API...")
    yield
    # Shutdown
    print("👋 Shutting down washing machine durability API...")

app = FastAPI(
    title="Washing Machine Durability API",
    description="API for searching and analyzing washing machine durability data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://51.210.241.37:3000",
        "http://51.210.241.37",
        "http://eco-lavelinge.fr",
        "https://eco-lavelinge.fr",
        "http://www.eco-lavelinge.fr",
        "https://www.eco-lavelinge.fr",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "51.210.241.37",
        "*.durable.tools",
        "eco-lavelinge.fr",
        "www.eco-lavelinge.fr",
    ]
)

# Add custom middleware for performance monitoring
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Only add caching headers on successful GET API responses
    if (
        request.url.path.startswith("/v1/")
        and request.method == "GET"
        and 200 <= response.status_code < 400
    ):
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=600"
        # Do not attempt to compute ETag for streaming responses
    
    return response

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# Add root endpoint
@app.get("/")
async def root():
    return {
        "message": "Washing Machine Durability API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include API router
app.include_router(router, prefix="/v1")

# Add exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": time.time()
        }
    )
