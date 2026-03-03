from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import os
from contextlib import asynccontextmanager
import time

from app.core.database import init_db
from app.core.logging import logger
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SmartClean API...")
    init_db()
    logger.info("Database initialized!")
    yield
    logger.info("Shutting down...")


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
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
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
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


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
