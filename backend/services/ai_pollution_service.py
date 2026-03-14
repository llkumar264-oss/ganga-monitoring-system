"""
AI-driven pollution detection with risk levels and inspection suggestions.
"""
import logging
from typing import Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PollutionAnalysis:
    """Result of pollution analysis."""
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    suggestion: str


def analyze_pollution(ph: float, turbidity: float, chemical: float) -> PollutionAnalysis:
    """
    Analyze sensor readings and return risk level, message, and suggested action.
    """
    # Critical: multiple severe indicators
    if chemical > 180 and (ph < 5.5 or ph > 8.5):
        return PollutionAnalysis(
            risk_level="CRITICAL",
            message="Severe chemical contamination with abnormal pH. Emergency response required.",
            suggestion="Immediate water sampling; notify environmental authority; restrict access; investigate upstream industries.",
        )
    if chemical > 180 and turbidity > 80:
        return PollutionAnalysis(
            risk_level="CRITICAL",
            message="High chemical discharge with severe turbidity. Likely industrial spill.",
            suggestion="Dispatch inspection team; collect samples; trace pollution source; alert nearby communities.",
        )
    if ph < 5 or ph > 9:
        return PollutionAnalysis(
            risk_level="CRITICAL",
            message="Extreme water acidity/alkalinity. Immediate health risk.",
            suggestion="Cease water intake; conduct emergency water quality assessment; identify discharge source.",
        )

    # High risk
    if chemical > 150:
        return PollutionAnalysis(
            risk_level="HIGH",
            message="High chemical discharge detected. Inspect nearby industries.",
            suggestion="Schedule inspection within 24 hours; verify industrial discharge permits; collect water samples.",
        )
    if turbidity > 80:
        return PollutionAnalysis(
            risk_level="HIGH",
            message="Very high turbidity. Possible waste dumping or sediment disturbance.",
            suggestion="Inspect for illegal dumping; check construction activities; monitor for 48 hours.",
        )
    if ph < 6 or ph > 8:
        return PollutionAnalysis(
            risk_level="HIGH",
            message="Water acidity abnormal. Inspection required.",
            suggestion="Run pH follow-up tests; identify potential acid/base sources; advise citizens.",
        )

    # Medium risk
    if chemical > 120 or turbidity > 70:
        return PollutionAnalysis(
            risk_level="MEDIUM",
            message="Elevated pollution indicators. Monitor closely.",
            suggestion="Increase monitoring frequency; schedule routine inspection; review recent activities.",
        )
    if ph < 6.2 or ph > 7.8:
        return PollutionAnalysis(
            risk_level="MEDIUM",
            message="Slight pH deviation from optimal range.",
            suggestion="Monitor trend over next readings; check seasonal variations.",
        )

    # Low risk
    return PollutionAnalysis(
        risk_level="LOW",
        message="Water quality within acceptable range.",
        suggestion="Continue routine monitoring; maintain current inspection schedule.",
    )
