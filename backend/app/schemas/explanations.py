"""Schemas Pydantic para el dominio de explicaciones (T009).

Cumple estrictamente con specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    url: str
    source: str
    published_at: datetime


class ExplanationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: uuid.UUID
    text: str
    is_fallback_no_evidence: bool
    evidence: list[EvidenceItemOut] = Field(default_factory=list)
    generated_at: datetime
    updated_at: datetime


class FollowUpRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


class FollowUpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: uuid.UUID
    question: str
    answer: str
    evidence: list[EvidenceItemOut] = Field(default_factory=list)
    generated_at: datetime
