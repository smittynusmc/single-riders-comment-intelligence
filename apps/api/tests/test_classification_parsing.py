from __future__ import annotations

from app.services.classification import ClassificationResultParser


def test_classification_result_parser_clamps_scores_and_parses_json_string():
    payload = """
    {
      "primary_category": "feature_request",
      "secondary_categories": ["beta"],
      "mvp_area": "onboarding",
      "sentiment": "positive",
      "confidence": 1.4,
      "mvp_relevance_score": 0.85,
      "urgency_score": -0.1,
      "needs_human_review": false,
      "recommended_action": "Track beta signup demand.",
      "rationale_short": "Multiple comments ask for beta access."
    }
    """

    parsed = ClassificationResultParser().parse(payload)

    assert parsed.confidence == 1.0
    assert parsed.urgency_score == 0.0
    assert parsed.primary_category.value == "feature_request"
