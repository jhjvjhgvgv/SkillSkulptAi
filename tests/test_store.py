from datetime import datetime, timedelta

from app.models import LearningStyle, MicroSculpt, UserProfile
from app.store import MemoryStore


def test_knowledge_gap_builds_prompt_from_performance_and_decay():
    store = MemoryStore()
    user = UserProfile(
        id="user-1",
        name="Jordan",
        role="compliance",
        learning_style=LearningStyle.VISUAL,
        strengths=[],
        gaps=["CMP-Q3-DRP"],
    )
    store.upsert_user(user)
    sculpt = MicroSculpt(
        id="sculpt-1",
        title="Data Retention Policy",
        role_tags=["compliance"],
        topics=["CMP-Q3-DRP"],
        modality=LearningStyle.VISUAL,
        summary="Quiz on retention rules",
    )
    store.add_sculpt(sculpt)

    # Older success to seed KRS then recent failure
    store.record_event(
        user_id=user.id,
        sculpt_id=sculpt.id,
        score=0.9,
        objective_id="CMP-Q3-DRP",
        content_format="article",
    )
    store.learning_events[-1].completed_at = datetime.utcnow() - timedelta(days=6)

    store.record_event(
        user_id=user.id,
        sculpt_id=sculpt.id,
        score=0.4,
        objective_id="CMP-Q3-DRP",
        hesitation=True,
        failure_reason="confused compliance dates",
        content_format="article",
    )

    gap = store.knowledge_gap(user.id)

    assert gap is not None
    assert gap.focus_objective_id == "CMP-Q3-DRP"
    assert gap.last_failure_reason == "confused compliance dates"
    assert gap.topic_urgency_score > 40
    assert gap.recommended_format == "Scenario-Based Quiz"

    prompt = gap.to_prompt_string()
    assert "CRITICAL KNOWLEDGE GAP" in prompt
    assert "KRS-derived" in prompt
