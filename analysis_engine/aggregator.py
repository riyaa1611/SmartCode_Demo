"""Aggregate findings from different analysis modules into the database.

Updated to handle the new structured output format with titles,
suggested fixes, references, and the enhanced finding categories.
"""

from typing import Dict, List, Any, Optional
from models import Finding


class ReviewAggregator:
    """Aggregate findings from different analysis modules."""

    # ── score aggregation ───────────────────────────────────────────────

    def aggregate_scores(
        self,
        completeness_score: int,
        security_score: int,
        performance_score: int,
        quality_score: int = 70,
    ) -> float:
        """Calculate overall review score as weighted average."""
        return (
            completeness_score * 0.30
            + security_score * 0.25
            + performance_score * 0.20
            + quality_score * 0.25
        )

    def calculate_confidence(
        self,
        context_quality: float,
        llm_confidence: float,
        static_analysis_agreement: float,
    ) -> float:
        """Calculate confidence score."""
        return context_quality * llm_confidence * static_analysis_agreement

    # ── finding creation ────────────────────────────────────────────────

    def create_findings_from_structured(
        self,
        review_id: int,
        llm_results: Dict[str, Any],
    ) -> List[Finding]:
        """Create Finding rows from the new structured LLM output.

        Each LLM review method now returns a `findings` list with
        full structured objects (title, description, suggested_fix, etc.).
        """
        findings: List[Finding] = []

        # Collect findings from all review results
        all_findings = llm_results.get("findings", [])

        for f in all_findings:
            finding = Finding(
                review_id=review_id,
                category=f.get("category", "code_quality"),
                severity=f.get("severity", "medium"),
                title=f.get("title", ""),
                description=f.get("description", ""),
                file_path=self._extract_file(f.get("file_path", "")),
                line_number=self._extract_line(f),
                confidence_score=float(f.get("confidence_score", 0.7)),
                code_snippet=f.get("code_snippet", ""),
                suggestion=f.get("suggested_fix", f.get("suggestion", "")),
                suggested_fix=f.get("suggested_fix", ""),
                references=f.get("references", []),
            )
            findings.append(finding)

        return findings

    def create_findings(
        self,
        review_id: int,
        llm_results: dict,
        static_results: dict,
    ) -> List[Finding]:
        """Convert analysis results to database findings.

        Supports both the legacy format and the new structured format.
        """
        findings: List[Finding] = []

        # ── New structured findings (from upgraded templates) ──
        for key in ("findings",):
            for f in llm_results.get(key, []):
                if isinstance(f, dict) and "title" in f:
                    finding = Finding(
                        review_id=review_id,
                        category=f.get("category", "code_quality"),
                        severity=f.get("severity", "medium"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        file_path=self._extract_file(f.get("file_path", "")),
                        line_number=self._extract_line(f),
                        confidence_score=float(f.get("confidence_score", 0.7)),
                        code_snippet=f.get("code_snippet", ""),
                        suggestion=f.get("suggested_fix", f.get("suggestion", "")),
                        suggested_fix=f.get("suggested_fix", ""),
                        references=f.get("references", []),
                    )
                    findings.append(finding)

        # ── Legacy: missing_features ──
        for feature in llm_results.get("missing_features", []):
            if isinstance(feature, dict) and "title" not in feature:
                finding = Finding(
                    review_id=review_id,
                    category="requirement_drift",
                    severity="high",
                    title=f"Missing: {feature.get('requirement', 'Unknown')}",
                    description=f"Missing feature: {feature.get('requirement', 'Unknown')}",
                    file_path="",
                    line_number=0,
                    confidence_score=0.8,
                )
                findings.append(finding)

        # ── Legacy: scope_creep ──
        for creep in llm_results.get("scope_creep", []):
            if isinstance(creep, dict):
                finding = Finding(
                    review_id=review_id,
                    category="requirement_drift",
                    severity="medium",
                    title=f"Scope creep: {creep.get('description', 'Unspecified')[:60]}",
                    description=f"Scope creep: {creep.get('description', 'Unspecified')}",
                    file_path=creep.get("code_location", creep.get("file_path", "")),
                    line_number=0,
                    confidence_score=0.7,
                )
                findings.append(finding)

        # ── Legacy: vulnerabilities ──
        for vuln in llm_results.get("vulnerabilities", []):
            if isinstance(vuln, dict) and "title" not in vuln:
                finding = Finding(
                    review_id=review_id,
                    category="security",
                    severity=vuln.get("severity", "medium"),
                    title=f"Security: {vuln.get('type', 'vulnerability')}",
                    description=vuln.get("description", "Unspecified vulnerability"),
                    file_path=self._extract_file(vuln.get("location", "")),
                    line_number=self._extract_line_from_location(vuln.get("location", "")),
                    confidence_score=0.9,
                    suggested_fix=vuln.get("fix_suggestion", ""),
                )
                findings.append(finding)

        # ── Legacy: performance_issues ──
        for perf in llm_results.get("performance_issues", []):
            if isinstance(perf, dict) and "title" not in perf:
                finding = Finding(
                    review_id=review_id,
                    category="performance",
                    severity="high",
                    title=f"Performance: {perf.get('issue_type', 'issue')}",
                    description=perf.get("description", perf.get("issue_type", "Performance issue")),
                    file_path=self._extract_file(perf.get("location", "")),
                    line_number=self._extract_line_from_location(perf.get("location", "")),
                    confidence_score=0.85,
                    suggested_fix=perf.get("fix", ""),
                )
                findings.append(finding)

        return findings

    # ── helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _extract_file(path: str) -> str:
        if ":" in path:
            return path.split(":")[0]
        return path

    @staticmethod
    def _extract_line(f: dict) -> int:
        ln = f.get("line_number", 0)
        if isinstance(ln, int):
            return ln
        try:
            return int(ln)
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _extract_line_from_location(loc: str) -> int:
        if ":" in loc:
            try:
                return int(loc.split(":")[1])
            except (ValueError, IndexError):
                return 0
        return 0