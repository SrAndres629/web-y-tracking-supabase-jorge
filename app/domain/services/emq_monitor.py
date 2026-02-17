"""
Event Match Quality (EMQ) Monitor
==================================
Analyzes tracking payloads to estimate Meta CAPI Match Quality Score (0-10).
Implements Step 2 of MVP Phase 1.
"""

from typing import Any, Dict


class EMQMonitor:
    """
    Scoring Logic based on Meta's importance weights:
    - strong_identifiers (email, phone): High Impact (+4.0)
    - medium_identifiers (fbp, fbc, external_id): Medium Impact (+2.0)
    - basic_identifiers (ip, ua): Baseline (+1.0)
    - geo_identifiers (city, country, zip): Low Impact (+0.5)
    """

    STRONG_KEYS = {"em", "ph"}
    MEDIUM_KEYS = {"fbp", "fbc", "external_id", "fb_browser_id"}
    GEO_KEYS = {
        "ct",
        "st",
        "zp",
        "country",
        "fn",
        "ln",
    }  # Name is also medium-ish but often paired with email

    def evaluate(self, user_data: Dict[str, Any]) -> float:
        score = 0.0

        # Base Requirements (IP + UA) - Mandatory for any matching
        if user_data.get("client_ip_address") and user_data.get("client_user_agent"):
            score += 2.0

        # Check Strong Identifiers
        for key in self.STRONG_KEYS:
            if user_data.get(key):
                score += 3.0  # +3 per strong ID

        # Check Medium Identifiers
        for key in self.MEDIUM_KEYS:
            if user_data.get(key):
                score += 1.5  # +1.5 per medium ID

        # Check Geo/Demo Identifiers
        for key in self.GEO_KEYS:
            if user_data.get(key):
                score += 0.5  # +0.5 per geo ID

        # Cap at 10.0
        return min(round(score, 1), 10.0)

    def get_quality_level(self, score: float) -> str:
        if score >= 8.0:
            return "EXCELLENT"
        if score >= 6.0:
            return "GOOD"
        if score >= 4.0:
            return "FAIR"
        return "POOR"


emq_monitor = EMQMonitor()
