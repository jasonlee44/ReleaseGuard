from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class BuildCreate(BaseModel):
    name: str
    version: str
    description: Optional[str] = None

class Build(BaseModel):
    build_id: UUID
    name: str
    version: str
    description: Optional[str] = None
    created_at: datetime
