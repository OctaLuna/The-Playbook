"""Evaluation helpers for manually audited groundedness samples."""


def groundedness_alert_triggered(
    failed_reviews: int, reviewed_explanations: int, threshold: float | None
) -> bool:
    """Return whether the audited failure rate exceeds the configured maximum."""
    if threshold is None or reviewed_explanations == 0:
        return False
    if not 0 <= failed_reviews <= reviewed_explanations:
        raise ValueError("failed_reviews must be between zero and reviewed_explanations")
    return failed_reviews / reviewed_explanations > threshold
