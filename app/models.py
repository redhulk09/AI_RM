"""Pydantic API models."""

from datetime import datetime
from pydantic import BaseModel, Field


class RiskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    category: str = Field(default="General", max_length=100)
    owner: str = Field(default="Unassigned", max_length=120)
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    control_effectiveness: int = Field(default=0, ge=0, le=100)


class Risk(RiskCreate):
    id: int
    base_score: int
    adjusted_score: int
    severity: str
    priority: str
    recommendation: str = ""
    created_at: datetime
    updated_at: datetime
