from datetime import datetime
from pydantic import BaseModel, Field

class ChecklistItem(BaseModel):
    id: str = Field(..., description="Unique checklist item ID")
    time_slice_id: str = Field(..., description="Associated time slice ID")
    title: str = Field(..., description="Title or task description")
    completed: bool = Field(False, description="Task completion status")
    order: int = Field(0, description="Sort order of the item")
