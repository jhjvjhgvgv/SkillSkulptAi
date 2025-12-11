from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"


class UserProfile(BaseModel):
    id: str
    name: str
    role: str
    learning_style: LearningStyle = Field(
        ..., description="Dominant style used for sequencing content"
    )
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)


class MicroSculpt(BaseModel):
    id: str
    title: str
    role_tags: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    modality: LearningStyle = LearningStyle.VISUAL
    duration_minutes: int = 5
    summary: Optional[str] = None


class LearningEvent(BaseModel):
    user_id: str
    sculpt_id: str
    objective_id: str
    completed_at: datetime
    score: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Normalized outcome score from quiz or assessment",
    )
    hesitation: bool = Field(
        default=False,
        description="Whether the user hesitated or changed an answer, signaling low confidence",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="Short explanation of why the learner missed the question",
    )
    content_format: Optional[str] = Field(
        default=None,
        description="Format of the learning object the event was tied to (e.g., quiz, article)",
    )


class Recommendation(BaseModel):
    sculpt: MicroSculpt
    rationale: str


class KnowledgeGap(BaseModel):
    focus_objective_id: str
    last_failure_reason: str | None
    topic_urgency_score: int = Field(ge=0, le=100)
    recommended_format: str
    last_success_date: date | None

    def to_prompt_string(self) -> str:
        urgency = (
            f"User's KRS-derived urgency is {self.topic_urgency_score}% for objective {self.focus_objective_id}."
        )
        failure = (
            f" The last failure was due to {self.last_failure_reason}."
            if self.last_failure_reason
            else ""
        )
        success = (
            f" Last success was recorded on {self.last_success_date}."
            if self.last_success_date
            else " No success recorded yet."
        )
        format_hint = f" The system recommends a {self.recommended_format} next."
        return f"CRITICAL KNOWLEDGE GAP: {urgency}{failure}{success}{format_hint}"
