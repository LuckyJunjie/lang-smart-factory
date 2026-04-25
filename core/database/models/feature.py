from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class FeatureBase(BaseModel):
    requirement_id: int
    name: str
    tech_notes: Optional[str] = None
    art_asset_required: bool = False
    priority: int = 0
    status: str = "active"


class FeatureCreate(FeatureBase):
    pass


class FeatureUpdate(BaseModel):
    name: Optional[str] = None
    tech_notes: Optional[str] = None
    art_asset_required: Optional[bool] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class FeatureResponse(FeatureBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    created_at: datetime
    updated_at: datetime


class FeatureBulkPriorityUpdate(BaseModel):
    updates: list[dict]  # [{"code": "F0001", "priority": 1}, ...]
