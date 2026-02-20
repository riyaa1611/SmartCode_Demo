"""LLM-powered code reviewer using OpenRouter (OpenAI-compatible API).

Upgraded to use centralised prompt templates, produce structured findings
with titles, suggested fixes, and confidence scores, and avoid generic
or hallucinated comments.
"""

import json
import traceback
from typing import Dict, Any, Optional

import openai
from config import settings
from analysis_engine.prompt_templates import (
    SYSTEM_PROMPT,
    REQUIREMENT_REVIEW_TEMPLATE,
    SECURITY_REVIEW_TEMPLATE,
    PERFORMANCE_REVIEW_TEMPLATE,
    CODE_QUALITY_REVIEW_TEMPLATE,
)


class LLMReviewer:
    """LLM-powered code reviewer using OpenRouter (OpenAI-compatible API)."""

    def __init__(self):
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self.model = settings.llm_model

    # ── internal helper ─────────────────────────────────────────────────

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Send prompt to LLM and parse JSON response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            # Strip markdown fences if model wraps them anyway
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content)
        except Exception as e:
            traceback.print_exc()
            print(f"LLM Error: {e}")
            return {}

    # ── public review methods ───────────────────────────────────────────

    def review_feature_completeness(
        self,
        issue_requirements: dict,
        code_diff: str,
        readme_summary: str,
        issue_num: int,
    ) -> dict:
        """Review if code changes fully implement the requirements."""
        prompt = REQUIREMENT_REVIEW_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            issue_num=issue_num,
            requirements_json=json.dumps(issue_requirements, indent=2),
            code_diff=self._truncate(code_diff),
            project_context=readme_summary,
        )

        result = self._call_llm(prompt)
        return {
            "completeness_score": result.get("completeness_score", 50),
            "findings": result.get("findings", []),
            "missing_features": [
                f for f in result.get("findings", [])
                if f.get("category") == "requirement_drift"
            ],
            "scope_creep": result.get("scope_creep", []),
            "unhandled_edge_cases": [],
            "summary": result.get("summary", ""),
            "reasoning": result.get("summary", ""),
        }

    def review_security(
        self, code_diff: str, data_flow_summary: str = ""
    ) -> dict:
        """Review code for security vulnerabilities."""
        prompt = SECURITY_REVIEW_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            code_diff=self._truncate(code_diff),
            data_flow=data_flow_summary or "No data-flow context provided.",
        )

        result = self._call_llm(prompt)
        return {
            "security_score": result.get("security_score", 50),
            "findings": result.get("findings", []),
            "vulnerabilities": result.get("findings", []),
            "summary": result.get("summary", ""),
        }

    def review_performance(self, code_diff: str) -> dict:
        """Review code for performance issues."""
        prompt = PERFORMANCE_REVIEW_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            code_diff=self._truncate(code_diff),
        )

        result = self._call_llm(prompt)
        return {
            "performance_score": result.get("performance_score", 50),
            "findings": result.get("findings", []),
            "performance_issues": result.get("findings", []),
            "summary": result.get("summary", ""),
        }

    def review_code_quality(
        self, code_diff: str, static_analysis: str = ""
    ) -> dict:
        """Review code for quality and technical debt."""
        prompt = CODE_QUALITY_REVIEW_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            code_diff=self._truncate(code_diff),
            static_analysis=static_analysis or "No static analysis context.",
        )

        result = self._call_llm(prompt)
        return {
            "quality_score": result.get("quality_score", 70),
            "findings": result.get("findings", []),
            "test_coverage_signal": result.get("test_coverage_signal", {}),
            "summary": result.get("summary", ""),
        }

    # ── utilities ───────────────────────────────────────────────────────

    @staticmethod
    def _truncate(text: str, max_chars: int = 24_000) -> str:
        """Truncate text to fit within context window limits."""
        if len(text) <= max_chars:
            return text
        half = max_chars // 2
        return (
            text[:half]
            + "\n\n... [TRUNCATED — diff too large, showing first & last sections] ...\n\n"
            + text[-half:]
        )