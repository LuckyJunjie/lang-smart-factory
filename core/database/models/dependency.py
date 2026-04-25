from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class DependencyBase(BaseModel):
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    dep_type: Optional[str] = None


class DependencyCreate(DependencyBase):
    pass


class DependencyResponse(DependencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
