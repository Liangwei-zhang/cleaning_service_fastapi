from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import os
from contextlib import asynccontextmanager
import time
import logging

from app.core.database import init_db, engine
from app.core.logging import logger
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SmartClean API...")
    init_db()
    logger.info("Database initialized!")
    yield
    logger.info("Shutting down...")
    await engine.dispose()


app = FastAPI(
    title="SmartClean API",
    description="短租清潔調度系統 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"← {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.3f}s"
    )
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for Docker/K8s"""
    import redis
    from sqlalchemy import text
    
    health = {
        "status": "healthy",
        "database": "unknown",
        "cache": "unknown"
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health["database"] = "healthy"
    except Exception as e:
        health["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check Redis
    try:
        import os
        if os.getenv("REDIS_ENABLED", "false").lower() == "true":
            r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
            r.ping()
            health["cache"] = "healthy"
        else:
            health["cache"] = "disabled"
    except Exception as e:
        health["cache"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)


# Include routers
app.include_router(router)

# Static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.get("/")
async def root():
    return FileResponse(os.path.join(BASE_DIR, "..", "index.html"))


@app.get("/{path:path}")
async def serve_static(path: str):
    file_path = os.path.join(BASE_DIR, "..", path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(BASE_DIR, "..", "index.html"))
