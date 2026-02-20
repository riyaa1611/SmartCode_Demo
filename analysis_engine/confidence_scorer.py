"""
PR Approval Confidence Scorer — SmartCode's differentiating capability.

Produces a 0-100 composite score answering: "Is this PR safe to merge?"

Score = Requirement_Alignment × 0.30
      + Security_Safety       × 0.25
      + Code_Quality          × 0.20
      + Test_Coverage_Signal  × 0.15
      + Static_Analysis_Clean × 0.10

Verdicts:
  80-100  →  APPROVE           (safe to merge)
  60-79   →  REVIEW_NEEDED     (human should check flagged items)
   0-59   →  CHANGES_REQUESTED (significant issues found)
"""

from typing import Dict, List, Any, Optional
import re


class ConfidenceScorer:
    """Calculate a composite PR Approval Confidence Score."""

    # Weights for each dimension (must sum to 1.0)
    WEIGHTS = {
        "requirement_alignment": 0.30,
        "security_safety": 0.25,
        "code_quality": 0.20,
        "test_coverage_signal": 0.15,
        "static_analysis_clean": 0.10,
    }

    VERDICT_THRESHOLDS = [
        (80, "APPROVE"),
        (60, "REVIEW_NEEDED"),
        (0, "CHANGES_REQUESTED"),
    ]

    # ── public API ──────────────────────────────────────────────────────

    def calculate_score(
        self,
        requirement_result: Dict[str, Any],
        security_result: Dict[str, Any],
        performance_result: Dict[str, Any],
        static_result: Dict[str, Any],
        quality_result: Optional[Dict[str, Any]] = None,
        diff_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return the full confidence-score payload.

        Parameters
        ----------
        requirement_result : dict   – output of LLMReviewer.review_feature_completeness
        security_result    : dict   – output of LLMReviewer.review_security
        performance_result : dict   – output of LLMReviewer.review_performance
        static_result      : dict   – output of CodeAnalyzer.analyze_diff / complexity
        quality_result     : dict   – (optional) output of LLMReviewer code-quality review
        diff_data          : dict   – (optional) raw diff info for test-file detection
        """
        breakdown = {
            "requirement_alignment": self._score_requirement_alignment(requirement_result),
            "security_safety": self._score_security_safety(security_result),
            "code_quality": self._score_code_quality(static_result, performance_result, quality_result),
            "test_coverage_signal": self._score_test_coverage(diff_data),
            "static_analysis_clean": self._score_static_analysis(static_result),
        }

        composite = sum(
            score * self.WEIGHTS[dim] for dim, score in breakdown.items()
        )
        composite = round(composite, 1)

        verdict = self._verdict(composite)
        risk_flags = self._collect_risk_flags(
            requirement_result, security_result, performance_result, static_result, quality_result, diff_data
        )

        recommendation = self._generate_recommendation(composite, verdict, risk_flags)

        return {
            "confidence_score": composite,
            "verdict": verdict,
            "breakdown": breakdown,
            "risk_flags": risk_flags,
            "recommendation": recommendation,
        }

    # ── private scorers ─────────────────────────────────────────────────

    def _score_requirement_alignment(self, result: Dict[str, Any]) -> int:
        """LLM completeness_score already maps to 0-100."""
        return int(result.get("completeness_score", 50))

    def _score_security_safety(self, result: Dict[str, Any]) -> int:
        """Use the LLM security_score (0-100, higher = safer)."""
        return int(result.get("security_score", 50))

    def _score_code_quality(
        self,
        static_result: Dict[str, Any],
        performance_result: Dict[str, Any],
        quality_result: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Blend static-analysis complexity + LLM quality + performance scores."""
        # Start with base from quality LLM review if available
        if quality_result and "quality_score" in quality_result:
            base = int(quality_result["quality_score"])
        else:
            base = 70  # default neutral

        # Penalise high cyclomatic complexity
        complexity = static_result.get("cyclomatic_complexity",
                     static_result.get("complexity_metrics", {}).get("cyclomatic_complexity", 0))
        if complexity > 20:
            base -= 25
        elif complexity > 10:
            base -= 15
        elif complexity > 5:
            base -= 5

        # Blend in performance score
        perf_score = int(performance_result.get("performance_score", 75))
        blended = int(base * 0.6 + perf_score * 0.4)

        return max(0, min(100, blended))

    def _score_test_coverage(self, diff_data: Optional[Dict[str, Any]]) -> int:
        """Heuristic: were test files added/modified in this PR?"""
        if not diff_data:
            return 50  # unknown

        files = diff_data.get("files_changed", [])
        if not files:
            return 50

        test_patterns = re.compile(
            r"(test_|_test\.|tests/|spec/|__tests__/|\.test\.|\.spec\.)", re.IGNORECASE
        )

        total = len(files)
        test_files = sum(
            1 for f in files
            if test_patterns.search(f if isinstance(f, str) else f.get("filename", ""))
        )

        if test_files == 0:
            return 30  # no tests touched → risky
        ratio = test_files / total
        if ratio >= 0.3:
            return 90
        elif ratio >= 0.15:
            return 70
        return 55

    def _score_static_analysis(self, static_result: Dict[str, Any]) -> int:
        """Score based on how clean the static analysis is."""
        # If a dedicated 'issues' list is provided, count them
        issues = static_result.get("issues", [])
        if issues:
            if len(issues) > 10:
                return 30
            elif len(issues) > 5:
                return 55
            elif len(issues) > 0:
                return 75
            return 95

        # Fallback: use complexity metrics as a proxy
        complexity = static_result.get("cyclomatic_complexity",
                     static_result.get("complexity_metrics", {}).get("cyclomatic_complexity", 0))
        nesting = static_result.get("nesting_depth",
                  static_result.get("complexity_metrics", {}).get("nesting_depth", 0))

        score = 100
        if complexity > 15:
            score -= 30
        elif complexity > 8:
            score -= 15
        if nesting > 4:
            score -= 20
        elif nesting > 3:
            score -= 10

        return max(0, min(100, score))

    # ── helpers ─────────────────────────────────────────────────────────

    def _verdict(self, score: float) -> str:
        for threshold, label in self.VERDICT_THRESHOLDS:
            if score >= threshold:
                return label
        return "CHANGES_REQUESTED"

    def _collect_risk_flags(self, req, sec, perf, static, quality, diff) -> List[str]:
        flags: List[str] = []

        # Requirement flags
        missing = req.get("missing_features", [])
        if missing:
            flags.append(f"{len(missing)} requirement(s) not fully implemented")

        # Security flags
        vulns = sec.get("vulnerabilities", sec.get("findings", []))
        critical = [v for v in vulns if v.get("severity") in ("critical", "high")]
        if critical:
            flags.append(f"{len(critical)} high/critical security finding(s)")

        # Performance flags
        perf_issues = perf.get("performance_issues", perf.get("findings", []))
        if perf_issues:
            flags.append(f"{len(perf_issues)} performance concern(s)")

        # Complexity
        complexity = static.get("cyclomatic_complexity",
                     static.get("complexity_metrics", {}).get("cyclomatic_complexity", 0))
        if complexity > 10:
            flags.append(f"Cyclomatic complexity {complexity} exceeds threshold (10)")

        # Test flags
        if diff:
            test_score = self._score_test_coverage(diff)
            if test_score <= 30:
                flags.append("No test files added or modified")

        return flags

    def _generate_recommendation(self, score: float, verdict: str, flags: List[str]) -> str:
        if verdict == "APPROVE":
            if flags:
                return f"Safe to merge with minor notes: {'; '.join(flags)}."
            return "All dimensions look good. Safe to merge."
        elif verdict == "REVIEW_NEEDED":
            return f"Human review recommended. Key concerns: {'; '.join(flags) if flags else 'marginal scores across dimensions'}."
        else:
            return f"Significant issues found — do not merge until resolved: {'; '.join(flags)}."
