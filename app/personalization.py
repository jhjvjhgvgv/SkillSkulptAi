from __future__ import annotations

from typing import Iterable, List, Optional

from .models import KnowledgeGap, LearningStyle, MicroSculpt, Recommendation, UserProfile


def _style_weight(modality: LearningStyle, preferred: LearningStyle) -> float:
    return 1.0 if modality == preferred else 0.7


def _gap_weight(gaps: Iterable[str], topics: Iterable[str]) -> float:
    gap_hits = len(set(gaps).intersection(topics))
    return 1 + 0.25 * gap_hits


def _role_weight(role_tags: Iterable[str], role: str) -> float:
    return 1.2 if role in role_tags else 1.0


def _knowledge_gap_weight(
    knowledge_gap: Optional[KnowledgeGap], topics: Iterable[str]
) -> float:
    if not knowledge_gap:
        return 1.0
    focus_hit = knowledge_gap.focus_objective_id in topics
    urgency_multiplier = 1 + (knowledge_gap.topic_urgency_score / 100)
    return urgency_multiplier if focus_hit else 1.0


def rank_sculpts_for_user(
    user: UserProfile,
    sculpts: Iterable[MicroSculpt],
    knowledge_gap: Optional[KnowledgeGap] = None,
) -> List[Recommendation]:
    ranked: list[tuple[float, MicroSculpt]] = []
    for sculpt in sculpts:
        score = _style_weight(sculpt.modality, user.learning_style)
        score *= _gap_weight(user.gaps, sculpt.topics)
        score *= _role_weight(sculpt.role_tags, user.role)
        score *= _knowledge_gap_weight(knowledge_gap, sculpt.topics)
        ranked.append((score, sculpt))

    ranked.sort(key=lambda pair: pair[0], reverse=True)

    recommendations: List[Recommendation] = []
    for score, sculpt in ranked:
        rationale_parts = [
            f"Matches {sculpt.modality} preference" if sculpt.modality == user.learning_style else None,
            "Targets your flagged gaps" if set(user.gaps).intersection(sculpt.topics) else None,
            "Built for your role" if user.role in sculpt.role_tags else None,
            (
                f"Prioritizes urgent objective {knowledge_gap.focus_objective_id}"
                if knowledge_gap and knowledge_gap.focus_objective_id in sculpt.topics
                else None
            ),
        ]
        rationale = ", ".join(part for part in rationale_parts if part)
        recommendations.append(Recommendation(sculpt=sculpt, rationale=rationale or "Balanced refresher"))
    return recommendations
