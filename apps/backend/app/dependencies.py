from sqlalchemy.orm import Session
from fastapi import Depends
from database.connection import SessionLocal
from database.repositories.process_repo import ProcessRepository
from database.repositories.slice_repo import TimeSliceRepository
from database.sync.sync_manager import SyncManager
from database.vector.vector_store import VectorStoreClient

# Shared vector client initialized pointing to a persistent directory in the workspace
_vector_client = VectorStoreClient(persist_dir="w:/Projects Antigravity/TimeSlice AI/chroma_db")

def get_db():
    """Yields SQLAlchemy DB session context."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_process_repo(db: Session = Depends(get_db)) -> ProcessRepository:
    return ProcessRepository(db)

def get_slice_repo(db: Session = Depends(get_db)) -> TimeSliceRepository:
    return TimeSliceRepository(db)

def get_sync_manager(db: Session = Depends(get_db)) -> SyncManager:
    return SyncManager(db)

def get_vector_store() -> VectorStoreClient:
    return _vector_client
