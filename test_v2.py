"""Verification script for SmartCode v2 — tests all new modules."""

def test_imports():
    print("=== Testing Imports ===")
    from analysis_engine.confidence_scorer import ConfidenceScorer
    print("  ✓ ConfidenceScorer")
    from analysis_engine.prompt_templates import SYSTEM_PROMPT, REQUIREMENT_REVIEW_TEMPLATE
    print("  ✓ prompt_templates")
    from analysis_engine.metrics_calculator import MetricsCalculator
    print("  ✓ MetricsCalculator")
    from analysis_engine.llm_reviewer import LLMReviewer
    print("  ✓ LLMReviewer")
    from analysis_engine.aggregator import ReviewAggregator
    print("  ✓ ReviewAggregator")
    from analysis_engine.code_analyzer import CodeAnalyzer
    print("  ✓ CodeAnalyzer")
    from analysis_engine.requirement_extractor import RequirementExtractor
    print("  ✓ RequirementExtractor")
    print()


def test_confidence_scorer():
    print("=== Testing ConfidenceScorer ===")
    from analysis_engine.confidence_scorer import ConfidenceScorer
    cs = ConfidenceScorer()

    result = cs.calculate_score(
        requirement_result={"completeness_score": 85},
        security_result={"security_score": 58},
        performance_result={"performance_score": 70},
        static_result={"cyclomatic_complexity": 5},
        quality_result={"quality_score": 70},
        diff_data={"files_changed": [
            {"filename": "src/app.py"},
            {"filename": "tests/test_app.py"},
        ]},
    )
    print(f"  Confidence Score: {result['confidence_score']}")
    print(f"  Verdict: {result['verdict']}")
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Risk Flags: {result['risk_flags']}")
    print(f"  Recommendation: {result['recommendation']}")
    assert 0 <= result["confidence_score"] <= 100, "Score out of range!"
    assert result["verdict"] in ("APPROVE", "REVIEW_NEEDED", "CHANGES_REQUESTED")
    print("  ✓ All assertions passed")
    print()


def test_metrics_calculator():
    print("=== Testing MetricsCalculator ===")
    from analysis_engine.metrics_calculator import MetricsCalculator
    mc = MetricsCalculator()

    # Bug Risk
    bug = mc.calculate_bug_risk([
        {"severity": "critical"},
        {"severity": "medium"},
        {"severity": "low"},
    ])
    print(f"  Bug Risk: {bug}")
    assert 0 <= bug["bug_risk_score"] <= 100

    # Security Index
    sec = mc.calculate_security_index(
        [{"severity": "high", "category": "security"}], files_changed=3
    )
    print(f"  Security Index: {sec}")
    assert 0 <= sec["security_index"] <= 10.0

    # Tech Debt
    debt = mc.calculate_tech_debt({
        "cyclomatic_complexity": 12,
        "nesting_depth": 4,
        "function_count": 8,
    })
    print(f"  Tech Debt: {debt}")
    assert 0 <= debt["tech_debt_indicator"] <= 10.0

    # Summary Report
    report = mc.generate_summary_report(
        findings=[{"severity": "high", "category": "security"}],
        complexity_metrics={"cyclomatic_complexity": 8, "nesting_depth": 3, "function_count": 5},
        confidence_result={"confidence_score": 72, "verdict": "REVIEW_NEEDED"},
        files_changed=3,
    )
    print(f"  Overall Health: {report['overall_health']}")
    print("  ✓ All assertions passed")
    print()


def test_aggregator():
    print("=== Testing ReviewAggregator ===")
    from analysis_engine.aggregator import ReviewAggregator
    agg = ReviewAggregator()

    # Test structured findings
    findings = agg.create_findings_from_structured(
        review_id=1,
        llm_results={
            "findings": [
                {
                    "category": "security",
                    "severity": "high",
                    "title": "SQL Injection",
                    "description": "Vulnerable query",
                    "file_path": "src/db.py",
                    "line_number": 42,
                    "confidence_score": 0.95,
                    "suggested_fix": "Use parameterized queries",
                    "references": ["CWE-89"],
                }
            ]
        },
    )
    assert len(findings) == 1
    assert findings[0].title == "SQL Injection"
    assert findings[0].suggested_fix == "Use parameterized queries"
    print(f"  Created {len(findings)} finding(s)")
    print("  ✓ Structured findings work correctly")
    print()


def test_prompt_templates():
    print("=== Testing Prompt Templates ===")
    from analysis_engine.prompt_templates import (
        SYSTEM_PROMPT, REQUIREMENT_REVIEW_TEMPLATE,
        SECURITY_REVIEW_TEMPLATE, PERFORMANCE_REVIEW_TEMPLATE,
        CODE_QUALITY_REVIEW_TEMPLATE,
    )
    assert "Senior Staff" in SYSTEM_PROMPT
    assert "ACTIONABLE" in SYSTEM_PROMPT
    assert "Never invent" in SYSTEM_PROMPT
    assert "{issue_num}" in REQUIREMENT_REVIEW_TEMPLATE
    assert "{code_diff}" in SECURITY_REVIEW_TEMPLATE
    assert "O(n" in PERFORMANCE_REVIEW_TEMPLATE
    assert "test_coverage_signal" in CODE_QUALITY_REVIEW_TEMPLATE
    print("  ✓ All 4 templates valid")
    print()


if __name__ == "__main__":
    test_imports()
    test_confidence_scorer()
    test_metrics_calculator()
    test_aggregator()
    test_prompt_templates()
    print("=" * 50)
    print("ALL TESTS PASSED ✓")
