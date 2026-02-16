import openai
from config import settings
import json

class LLMReviewer:
    """LLM-powered code reviewer using OpenRouter (OpenAI-compatible API)"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self.model = settings.llm_model
        
    def review_feature_completeness(self, issue_requirements: dict, code_diff: str, readme_summary: str, issue_num: int) -> dict:
        """Review if code changes fully implement requirements"""
        prompt = f"""
You are a senior software engineer reviewing code changes.

REQUIREMENTS (from issue #{issue_num}):
{json.dumps(issue_requirements, indent=2)}

CODE CHANGES:
{code_diff}

PROJECT CONTEXT:
{readme_summary}

Analyze if the code changes fully implement the requirements. Identify:
1. Missing features from requirements
2. Features implemented but not in requirements (scope creep)
3. Edge cases not handled
4. Incomplete error handling

Respond in JSON:
{{
  "completeness_score": 0-100,
  "missing_features": [{{"requirement": "...", "explanation": "..."}}],
  "scope_creep": [{{"code_location": "...", "description": "..."}}],
  "unhandled_edge_cases": [{{"scenario": "...", "risk_level": "..."}}],
  "reasoning": "detailed explanation"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, # Low temperature for consistent JSON
                response_format={"type": "json_object"} # Force JSON if supported, otherwise prompt handles it
            )
            
            content = response.choices[0].message.content
            # Handle potential markdown fencing
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            result = json.loads(content)
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"LLM Error: {e}")
            return {
                "completeness_score": 50,
                "missing_features": [],
                "scope_creep": [],
                "unhandled_edge_cases": [],
                "reasoning": f"Failed to parse LLM response: {str(e)}"
            }
            
    def review_security(self, code_diff: str, data_flow_summary: str) -> dict:
        """Review code for security vulnerabilities"""
        prompt = f"""
You are a security engineer reviewing code for vulnerabilities.

CODE CHANGES:
{code_diff}

DATA FLOW ANALYSIS:
{data_flow_summary}

Check for:
1. PII/sensitive data handling without sanitization
2. SQL injection vulnerabilities
3. XSS vulnerabilities
4. Authentication/authorization bypasses
5. Hardcoded secrets or credentials
6. Unsafe deserialization

Respond in JSON:
{{
  "vulnerabilities": [{{
    "type": "sql_injection|xss|pii_leak|etc",
    "severity": "critical|high|medium|low",
    "location": "file:line",
    "description": "what's wrong",
    "fix_suggestion": "how to fix"
  }}],
  "security_score": 0-100
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
             # Handle potential markdown fencing
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content)
            return result
        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "vulnerabilities": [],
                "security_score": 50
            }
            
    def review_performance(self, code_diff: str) -> dict:
        """Review code for performance issues"""
        prompt = f"""
You are a performance engineer reviewing code.

CODE CHANGES:
{code_diff}

Identify:
1. O(n²) or worse algorithms where O(n) exists
2. Database queries inside loops (N+1 problem)
3. Missing pagination/limits on queries
4. Unnecessary data loading
5. Missing caching opportunities
6. Memory leaks (unclosed connections, growing arrays)

Respond in JSON:
{{
  "performance_issues": [{{
    "issue_type": "algorithmic|database|memory",
    "location": "file:line",
    "current_complexity": "O(n²)",
    "suggested_complexity": "O(n)",
    "fix": "specific code suggestion"
  }}],
  "performance_score": 0-100
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
             # Handle potential markdown fencing
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content)
            return result
        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "performance_issues": [],
                "performance_score": 50
            }