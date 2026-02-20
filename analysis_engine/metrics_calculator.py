"""
Metrics Calculator for SmartCode AI Reviews.

Computes four measurable indicators per review:
  • Bug Risk Score          (0-100, lower = riskier)
  • Security Severity Index (0.0-10.0)
  • Technical Debt Indicator(0.0-10.0)
  • Review Confidence %     (from ConfidenceScorer)
"""

from typing import Dict, List, Any, Optional


# Severity weights used across metrics
SEVERITY_WEIGHTS = {
    "critical": 10,
    "high": 7,
    "medium": 4,
    "low": 1,
    "info": 0,
}


class MetricsCalculator:
    """Compute quantified metrics from review findings and static analysis."""

    # ── Bug Risk Score ──────────────────────────────────────────────────

    def calculate_bug_risk(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bug Risk Score = 100 − (weighted_severity_sum / max_possible) × 100

        A score of 100 means zero risk flags; 0 means extreme risk.
        """
        if not findings:
            return {"bug_risk_score": 100, "risk_level": "low", "finding_count": 0}

        weighted_sum = sum(
            SEVERITY_WEIGHTS.get(f.get("severity", "low"), 1)
            for f in findings
        )
        # Cap max at 100 points of weighted findings for normalisation
        max_possible = max(weighted_sum, 100)
        score = max(0, round(100 - (weighted_sum / max_possible) * 100))

        if score >= 80:
            level = "low"
        elif score >= 50:
            level = "medium"
        else:
            level = "high"

        return {
            "bug_risk_score": score,
            "risk_level": level,
            "finding_count": len(findings),
            "weighted_severity_sum": weighted_sum,
        }

    # ── Security Severity Index ─────────────────────────────────────────

    def calculate_security_index(
        self,
        findings: List[Dict[str, Any]],
        files_changed: int = 1,
    ) -> Dict[str, Any]:
        """Security Severity Index = Σ(severity_weight × count) / files_changed

        Range 0.0 (clean) – 10.0 (heavily compromised).
        """
        security_findings = [
            f for f in findings if f.get("category") == "security"
        ]
        if not security_findings:
            return {
                "security_index": 0.0,
                "rating": "clean",
                "security_findings": 0,
            }

        weighted = sum(
            SEVERITY_WEIGHTS.get(f.get("severity", "low"), 1)
            for f in security_findings
        )
        index = round(min(10.0, weighted / max(files_changed, 1)), 2)

        if index <= 1.0:
            rating = "low"
        elif index <= 4.0:
            rating = "moderate"
        elif index <= 7.0:
            rating = "high"
        else:
            rating = "critical"

        return {
            "security_index": index,
            "rating": rating,
            "security_findings": len(security_findings),
        }

    # ── Technical Debt Indicator ────────────────────────────────────────

    def calculate_tech_debt(
        self, complexity_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Technical Debt Indicator (0.0-10.0)

        = (normalised_complexity × 0.4)
        + (normalised_nesting   × 0.3)
        + (normalised_functions × 0.3)
        """
        cc = complexity_metrics.get("cyclomatic_complexity", 0)
        nd = complexity_metrics.get("nesting_depth",
             complexity_metrics.get("max_nesting_depth", 0))
        fc = complexity_metrics.get("function_count", 0)

        # Normalise each to 0-10 scale
        norm_cc = min(10.0, cc / 3.0)       # cc=30 → 10
        norm_nd = min(10.0, nd * 2.0)        # nd=5  → 10
        norm_fc = min(10.0, fc / 5.0)        # fc=50 → 10

        indicator = round(norm_cc * 0.4 + norm_nd * 0.3 + norm_fc * 0.3, 2)

        if indicator <= 2.0:
            level = "low"
        elif indicator <= 5.0:
            level = "moderate"
        elif indicator <= 7.5:
            level = "high"
        else:
            level = "severe"

        return {
            "tech_debt_indicator": indicator,
            "level": level,
            "details": {
                "cyclomatic_complexity": cc,
                "nesting_depth": nd,
                "function_count": fc,
            },
        }

    # ── Summary Report ──────────────────────────────────────────────────

    def generate_summary_report(
        self,
        findings: List[Dict[str, Any]],
        complexity_metrics: Dict[str, Any],
        confidence_result: Dict[str, Any],
        files_changed: int = 1,
    ) -> Dict[str, Any]:
        """Generate a full metrics report for a review."""
        bug_risk = self.calculate_bug_risk(findings)
        security = self.calculate_security_index(findings, files_changed)
        tech_debt = self.calculate_tech_debt(complexity_metrics)

        return {
            "bug_risk": bug_risk,
            "security_severity": security,
            "tech_debt": tech_debt,
            "review_confidence": {
                "score": confidence_result.get("confidence_score", 0),
                "verdict": confidence_result.get("verdict", "UNKNOWN"),
            },
            "overall_health": self._overall_health(
                bug_risk["bug_risk_score"],
                security["security_index"],
                tech_debt["tech_debt_indicator"],
                confidence_result.get("confidence_score", 0),
            ),
        }

    # ── helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _overall_health(
        bug_risk: int,
        security_index: float,
        tech_debt: float,
        confidence: float,
    ) -> str:
        """One-word health label: healthy / caution / unhealthy."""
        if bug_risk >= 80 and security_index <= 2.0 and tech_debt <= 3.0 and confidence >= 75:
            return "healthy"
        if bug_risk < 50 or security_index > 6.0 or tech_debt > 7.0 or confidence < 50:
            return "unhealthy"
        return "caution"
