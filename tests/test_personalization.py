from app.models import KnowledgeGap, LearningStyle, MicroSculpt, UserProfile
from app.personalization import rank_sculpts_for_user


def test_rank_sculpts_orders_by_style_and_gaps():
    user = UserProfile(
        id="1",
        name="Ava",
        role="sales",
        learning_style=LearningStyle.AUDITORY,
        gaps=["security", "pricing"],
    )
    sculpts = [
        MicroSculpt(
            id="a",
            title="Security Basics",
            modality=LearningStyle.AUDITORY,
            role_tags=["sales"],
            topics=["security"],
        ),
        MicroSculpt(
            id="b",
            title="Pricing Objections",
            modality=LearningStyle.VISUAL,
            role_tags=["sales"],
            topics=["pricing"],
        ),
    ]

    ranked = rank_sculpts_for_user(user, sculpts)

    assert ranked[0].sculpt.id == "a"
    assert "auditory" in ranked[0].rationale
    assert ranked[0].rationale


def test_rank_sculpts_includes_role_signal():
    user = UserProfile(
        id="2",
        name="Eli",
        role="support",
        learning_style=LearningStyle.VISUAL,
        gaps=[],
    )
    sculpts = [
        MicroSculpt(
            id="c",
            title="Platform Overview",
            modality=LearningStyle.VISUAL,
            role_tags=["support"],
            topics=["product"],
        ),
        MicroSculpt(
            id="d",
            title="Generic Refresher",
            modality=LearningStyle.AUDITORY,
            role_tags=[],
            topics=["product"],
        ),
    ]

    ranked = rank_sculpts_for_user(user, sculpts)

    assert ranked[0].sculpt.id == "c"
    assert ranked[0].rationale


def test_rank_sculpts_prioritizes_urgent_objective():
    user = UserProfile(
        id="3",
        name="Riley",
        role="analyst",
        learning_style=LearningStyle.VISUAL,
        gaps=["compliance"],
    )
    knowledge_gap = KnowledgeGap(
        focus_objective_id="CMP-Q3-DRP",
        last_failure_reason="confused compliance dates",
        topic_urgency_score=92,
        recommended_format="Scenario-Based Quiz",
        last_success_date=None,
    )
    sculpts = [
        MicroSculpt(
            id="gap",
            title="Data Retention Policy",
            modality=LearningStyle.VISUAL,
            role_tags=["analyst"],
            topics=["CMP-Q3-DRP"],
        ),
        MicroSculpt(
            id="general",
            title="General Refresher",
            modality=LearningStyle.VISUAL,
            role_tags=["analyst"],
            topics=["security"],
        ),
    ]

    ranked = rank_sculpts_for_user(user, sculpts, knowledge_gap)

    assert ranked[0].sculpt.id == "gap"
    assert "urgent objective" in ranked[0].rationale
