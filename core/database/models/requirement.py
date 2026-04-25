from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RequirementBase(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    status: str = "DRAFT"


class RequirementCreate(RequirementBase):
    pass


class RequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class RequirementResponse(RequirementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    created_at: datetime
    updated_at: datetime
