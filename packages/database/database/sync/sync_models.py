from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class SyncConflict(BaseModel):
    id: str  # conflict ID, e.g. "processes:test-p1"
    record_id: str
    table_name: str
    field: str
    local_value: str
    cloud_value: str
    local_updated_at: datetime
    cloud_updated_at: datetime
    process_name: str  # User-friendly name of the process/event

class SyncResolution(BaseModel):
    conflict_id: str
    resolution: str  # "local" or "cloud"

class SyncStatus(BaseModel):
    last_synced_at: Optional[datetime] = None
    pending_count: int
    conflict_count: int
    is_online: bool
