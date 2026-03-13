from __future__ import annotations

from app.services.rules import RuleEvaluation

CLASSIFICATION_PROMPT_VERSION = "v1"


def build_classification_messages(*, comment_text: str, rules: RuleEvaluation) -> list[dict[str, str]]:
    system_prompt = (
        "You classify social app comments into structured JSON for product planning. "
        "Return JSON only with the required schema and keep rationale_short under 25 words."
    )

    user_prompt = f"""
Comment text:
{comment_text}

Rule tags:
{', '.join(rules.tags) if rules.tags else 'none'}
Rule suggested primary category:
{rules.primary_category.value if rules.primary_category else 'none'}
Rule suggested MVP area:
{rules.mvp_area.value if rules.mvp_area else 'none'}
Rule needs human review:
{str(rules.needs_human_review).lower()}

Return a JSON object with:
primary_category
secondary_categories
mvp_area
sentiment
confidence
mvp_relevance_score
urgency_score
needs_human_review
recommended_action
rationale_short
""".strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
