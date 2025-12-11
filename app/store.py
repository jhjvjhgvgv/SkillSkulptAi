from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from .models import KnowledgeGap, LearningEvent, MicroSculpt, UserProfile


class MemoryStore:
    """Tiny in-memory store for demo purposes only."""

    def __init__(self) -> None:
        self.users: Dict[str, UserProfile] = {}
        self.sculpts: Dict[str, MicroSculpt] = {}
        self.learning_events: List[LearningEvent] = []

    def upsert_user(self, profile: UserProfile) -> UserProfile:
        self.users[profile.id] = profile
        return profile

    def add_sculpt(self, sculpt: MicroSculpt) -> MicroSculpt:
        self.sculpts[sculpt.id] = sculpt
        return sculpt

    def record_event(
        self,
        user_id: str,
        sculpt_id: str,
        score: float | None = None,
        objective_id: str | None = None,
        hesitation: bool = False,
        failure_reason: str | None = None,
        content_format: str | None = None,
    ) -> LearningEvent:
        sculpt = self.sculpts.get(sculpt_id)
        objective = objective_id or (sculpt.topics[0] if sculpt and sculpt.topics else "general")
        event = LearningEvent(
            user_id=user_id,
            sculpt_id=sculpt_id,
            objective_id=objective,
            completed_at=datetime.utcnow(),
            score=score,
            hesitation=hesitation,
            failure_reason=failure_reason,
            content_format=content_format,
        )
        self.learning_events.append(event)
        return event

    def events_for_user(self, user_id: str) -> List[LearningEvent]:
        return [event for event in self.learning_events if event.user_id == user_id]

    def _krs_from_success(self, last_success: Optional[datetime]) -> float:
        if not last_success:
            return 55.0
        days_since_success = (datetime.utcnow() - last_success).days
        decay_rate = 7.5
        return max(20.0, 100.0 - (decay_rate * days_since_success))

    def _recommended_format(self, last_format: Optional[str]) -> str:
        if not last_format:
            return "Scenario-Based Quiz"
        if last_format.lower() == "scenario-based quiz":
            return "Explainer with visuals"
        if "quiz" in last_format.lower():
            return "Scenario-Based Quiz"
        return "Applied practice quiz"

    def knowledge_gap(self, user_id: str) -> KnowledgeGap | None:
        events = self.events_for_user(user_id)
        if not events:
            return None

        objective_events: Dict[str, List[LearningEvent]] = {}
        for event in events:
            objective_events.setdefault(event.objective_id, []).append(event)

        best_gap: KnowledgeGap | None = None
        best_score = -1.0

        for objective_id, history in objective_events.items():
            history.sort(key=lambda e: e.completed_at)
            last_success_event = next(
                (e for e in reversed(history) if e.score is not None and e.score >= 0.8),
                None,
            )
            last_success_date = (
                last_success_event.completed_at.date() if last_success_event else None
            )
            krs = self._krs_from_success(
                last_success_event.completed_at if last_success_event else None
            )

            recent_window = history[-5:]
            recent_failures = [
                e for e in recent_window if e.score is not None and e.score < 0.7
            ]
            last_failure_reason = (
                recent_failures[-1].failure_reason or "low confidence"
                if recent_failures
                else None
            )
            hesitation_penalty = 10 if any(e.hesitation for e in recent_window) else 0
            failure_penalty = min(25, 5 * len(recent_failures))
            urgency = min(100, round((100 - krs) + hesitation_penalty + failure_penalty))

            last_format = history[-1].content_format
            recommended_format = self._recommended_format(last_format)

            if urgency > best_score:
                best_score = urgency
                best_gap = KnowledgeGap(
                    focus_objective_id=objective_id,
                    last_failure_reason=last_failure_reason,
                    topic_urgency_score=urgency,
                    recommended_format=recommended_format,
                    last_success_date=last_success_date,
                )

        return best_gap

    def user_progress(self, user_id: str) -> dict:
        events = self.events_for_user(user_id)
        completed = len(events)
        average_score = (
            sum(event.score for event in events if event.score is not None)
            / max(1, len([event for event in events if event.score is not None]))
            if events
            else 0
        )
        return {
            "completed": completed,
            "average_score": round(average_score, 3),
            "recent": [event.model_dump() for event in events[-5:]],
        }


store = MemoryStore()
