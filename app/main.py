from __future__ import annotations

from typing import List

from fastapi import FastAPI, HTTPException

from .models import KnowledgeGap, MicroSculpt, Recommendation, UserProfile
from .personalization import rank_sculpts_for_user
from .store import store

app = FastAPI(title="SkillSculpt AI", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/users", response_model=UserProfile)
def upsert_user(profile: UserProfile) -> UserProfile:
    return store.upsert_user(profile)


@app.post("/sculpts", response_model=MicroSculpt)
def create_sculpt(sculpt: MicroSculpt) -> MicroSculpt:
    return store.add_sculpt(sculpt)


@app.get("/recommendations/{user_id}", response_model=List[Recommendation])
def recommendations(user_id: str) -> List[Recommendation]:
    user = store.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    knowledge_gap = store.knowledge_gap(user_id)
    return rank_sculpts_for_user(user, store.sculpts.values(), knowledge_gap)


@app.post("/events")
def record_event(
    user_id: str,
    sculpt_id: str,
    score: float | None = None,
    objective_id: str | None = None,
    hesitation: bool = False,
    failure_reason: str | None = None,
    content_format: str | None = None,
) -> dict:
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    if sculpt_id not in store.sculpts:
        raise HTTPException(status_code=404, detail="Micro-sculpt not found")
    event = store.record_event(
        user_id,
        sculpt_id,
        score=score,
        objective_id=objective_id,
        hesitation=hesitation,
        failure_reason=failure_reason,
        content_format=content_format,
    )
    return {"recorded": event.model_dump()}


@app.get("/progress/{user_id}")
def progress(user_id: str) -> dict:
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    return store.user_progress(user_id)


@app.get("/knowledge-gap/{user_id}", response_model=KnowledgeGap | None)
def knowledge_gap(user_id: str) -> KnowledgeGap | None:
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    return store.knowledge_gap(user_id)
