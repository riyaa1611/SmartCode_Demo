import json
import re
from typing import Dict, List

class RequirementExtractor:
    """Extract requirements from issues and PR descriptions"""
    
    def extract_from_issue(self, issue_body: str) -> Dict[str, List[str]]:
        """Extract functional requirements from issue body"""
        if not issue_body:
            return {"requirements": [], "edge_cases": [], "acceptance_criteria": []}
            
        # Extract requirements (bulleted lists)
        requirements = re.findall(r'^\s*[-*]\s+(.+)$', issue_body, re.MULTILINE)
        
        # Extract acceptance criteria (checkboxes)
        acceptance_criteria = re.findall(r'^\s*[-*]\s+\[[x ]\]\s+(.+)$', issue_body, re.MULTILINE)
        
        # Extract edge cases (look for "edge case" or "edge-case")
        edge_cases = re.findall(r'(?:edge\s+case[s]?|corner\s+case[s]?)[:\-\s]+(.+?)(?=\n\n|\Z)', issue_body, re.IGNORECASE | re.DOTALL)
        
        return {
            "requirements": requirements,
            "edge_cases": edge_cases,
            "acceptance_criteria": acceptance_criteria
        }
        
    def classify_requirement_type(self, issue_body: str) -> str:
        """Classify the type of requirement"""
        if not issue_body:
            return "unknown"
            
        issue_body_lower = issue_body.lower()
        
        if any(keyword in issue_body_lower for keyword in ["bug", "fix", "error", "crash", "broken"]):
            return "bugfix"
        elif any(keyword in issue_body_lower for keyword in ["refactor", "cleanup", "improve", "optimize"]):
            return "refactor"
        elif any(keyword in issue_body_lower for keyword in ["performance", "slow", "faster", "optimiz"]):
            return "optimization"
        else:
            return "feature"