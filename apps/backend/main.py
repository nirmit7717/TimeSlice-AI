import uvicorn
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.dependencies import get_db
from app.logger import setup_logging
from app.routers import (
    processes_router, slices_router, scheduler_router,
    vault_router, chat_router, sync_router
)

# Initialize telemetry JSON logging formats on server load
setup_logging()

app = FastAPI(
    title="TimeSlice AI Local API",
    description="Deterministic scheduling and local RAG context vault service for TimeSlice AI",
    version="0.1.0"
)

# Configure CORS for Vite dev server and Tauri desktop wrappers
origins = [
    "http://localhost:5173",
    "http://localhost:1420",
    "http://127.0.0.1:1420",
    "tauri://localhost",
    "https://tauri.localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIRouters
app.include_router(processes_router, prefix="/api/v1")
app.include_router(slices_router, prefix="/api/v1")
app.include_router(scheduler_router, prefix="/api/v1")
app.include_router(vault_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(sync_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    """Ensure database tables exist on local startup."""
    from database.connection import engine, Base
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "TimeSlice AI Backend API",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Database-aware health telemetry verification endpoint.
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
