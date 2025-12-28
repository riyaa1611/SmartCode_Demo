from typing import Dict, List
from models import Finding

class ReviewAggregator:
    """Aggregate findings from different analysis modules"""
    
    def aggregate_scores(self, completeness_score: int, security_score: int, performance_score: int) -> float:
        """Calculate overall review score as weighted average"""
        # Weighted average: completeness 40%, security 35%, performance 25%
        overall_score = (
            completeness_score * 0.4 +
            security_score * 0.35 +
            performance_score * 0.25
        )
        return overall_score
        
    def calculate_confidence(self, context_quality: float, llm_confidence: float, static_analysis_agreement: float) -> float:
        """Calculate confidence score"""
        confidence_score = context_quality * llm_confidence * static_analysis_agreement
        return confidence_score
        
    def create_findings(self, review_id: int, llm_results: dict, static_results: dict) -> List[Finding]:
        """Convert analysis results to database findings"""
        findings = []
        
        # Process completeness findings
        if "missing_features" in llm_results:
            for feature in llm_results["missing_features"]:
                finding = Finding(
                    review_id=review_id,
                    category="incomplete",
                    severity="high",
                    description=f"Missing feature: {feature.get('requirement', 'Unknown')}",
                    file_path="",  # Would be populated with specific file info
                    line_number=0,
                    confidence_score=0.8
                )
                findings.append(finding)
                
        if "scope_creep" in llm_results:
            for creep in llm_results["scope_creep"]:
                finding = Finding(
                    review_id=review_id,
                    category="feature_drift",
                    severity="medium",
                    description=f"Scope creep: {creep.get('description', 'Unspecified')}",
                    file_path=creep.get("code_location", ""),
                    line_number=0,
                    confidence_score=0.7
                )
                findings.append(finding)
                
        # Process security findings
        if "vulnerabilities" in llm_results:
            for vuln in llm_results["vulnerabilities"]:
                severity_map = {"critical": "critical", "high": "high", "medium": "medium", "low": "low"}
                finding = Finding(
                    review_id=review_id,
                    category="security",
                    severity=severity_map.get(vuln.get("severity", "medium"), "medium"),
                    description=vuln.get("description", "Unspecified vulnerability"),
                    file_path=vuln.get("location", "").split(":")[0] if ":" in vuln.get("location", "") else vuln.get("location", ""),
                    line_number=int(vuln.get("location", "").split(":")[1]) if ":" in vuln.get("location", "") else 0,
                    confidence_score=0.9
                )
                findings.append(finding)
                
        # Process performance findings
        if "performance_issues" in llm_results:
            for perf in llm_results["performance_issues"]:
                finding = Finding(
                    review_id=review_id,
                    category="performance",
                    severity="high",
                    description=perf.get("description", perf.get("issue_type", "Performance issue")),
                    file_path=perf.get("location", "").split(":")[0] if ":" in perf.get("location", "") else perf.get("location", ""),
                    line_number=int(perf.get("location", "").split(":")[1]) if ":" in perf.get("location", "") else 0,
                    confidence_score=0.85
                )
                findings.append(finding)
                
        return findings