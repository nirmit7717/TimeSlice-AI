from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ContextDocument(BaseModel):
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: float

class ContextPackage(BaseModel):
    relevant_processes: List[Dict[str, Any]] = Field(default_factory=list)
    relevant_documents: List[ContextDocument] = Field(default_factory=list)
    relevant_reflections: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = 1.0
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
