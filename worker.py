from config import settings

# The full Celery worker and heavy analysis pipeline are optional for
# quick local runs. If Celery isn't installed in the environment, provide a
# lightweight fallback so the API can enqueue/trigger analysis without
# failing at import time.
try:
    from celery import Celery
    from github_integration.client import GitHubAppClient
    from data_pipeline.collector import DataCollector
    from analysis_engine.requirement_extractor import RequirementExtractor
    from analysis_engine.code_analyzer import CodeAnalyzer
    from analysis_engine.llm_reviewer import LLMReviewer
    from analysis_engine.aggregator import ReviewAggregator
    from analysis_engine.confidence_scorer import ConfidenceScorer
    from analysis_engine.metrics_calculator import MetricsCalculator
    from database import SessionLocal
    from models import Review, Finding
    import json
    from datetime import datetime, timezone

    celery_app = Celery('smart_review_worker')
    celery_app.conf.broker_url = settings.redis_url
    celery_app.conf.result_backend = settings.redis_url

    @celery_app.task
    def analyze_pull_request(repo_name: str, pr_number: int, installation_id: int):
        """Full async analysis pipeline.

        PR → Context Extraction → Static Analysis → AI Reasoning
            → Confidence Scoring → Findings Storage → GitHub Comment
        """
        print(f"[worker] Starting analysis for {repo_name}#{pr_number}")

        github_client = GitHubAppClient()
        repo_client = github_client.get_repo_client(installation_id, repo_name)
        collector = DataCollector(repo_client)
        requirement_extractor = RequirementExtractor()
        code_analyzer = CodeAnalyzer()
        llm_reviewer = LLMReviewer()
        aggregator = ReviewAggregator()
        confidence_scorer = ConfidenceScorer()
        metrics_calc = MetricsCalculator()

        db = SessionLocal()
        review = None
        try:
            # ── 1. Context Extraction ───────────────────────────────
            print(f"[worker] Collecting PR data...")
            pr_data = collector.collect_pr_data(repo_name, pr_number)

            # Build unified diff from file patches
            code_diff = "\n".join(
                f"--- a/{f['filename']}\n+++ b/{f['filename']}\n{f['patch']}"
                for f in pr_data.get("files_changed", [])
                if f.get("patch")
            )

            # Extract requirements from linked issues
            issue_requirements = {}
            issue_num = 0
            for inum, idata in pr_data.get("issue_context", {}).items():
                issue_num = inum
                extracted = requirement_extractor.extract_from_issue(
                    idata.get("body", "")
                )
                issue_requirements = extracted
                break  # use first linked issue

            # Project context
            project_context = pr_data.get("project_docs", {}).get("readme", "")

            # ── 2. Static Analysis ──────────────────────────────────
            print(f"[worker] Running static analysis...")
            diff_analysis = code_analyzer.analyze_diff(code_diff)

            # Calculate complexity for each changed Python file
            complexity_metrics = {"cyclomatic_complexity": 0, "function_count": 0, "nesting_depth": 0}
            for f in pr_data.get("files_changed", []):
                if f.get("filename", "").endswith(".py") and f.get("patch"):
                    # Extract added lines as code
                    added = "\n".join(
                        line[1:] for line in f["patch"].split("\n")
                        if line.startswith("+") and not line.startswith("+++")
                    )
                    if added.strip():
                        m = code_analyzer.calculate_complexity(added)
                        complexity_metrics["cyclomatic_complexity"] += m.get("cyclomatic_complexity", 0)
                        complexity_metrics["function_count"] += m.get("function_count", 0)
                        complexity_metrics["nesting_depth"] = max(
                            complexity_metrics["nesting_depth"],
                            m.get("nesting_depth", 0)
                        )

            # ── 3. AI Reasoning (LLM Reviews) ──────────────────────
            print(f"[worker] Running LLM reviews...")
            req_result = llm_reviewer.review_feature_completeness(
                issue_requirements, code_diff, project_context, issue_num
            )
            sec_result = llm_reviewer.review_security(code_diff)
            perf_result = llm_reviewer.review_performance(code_diff)
            quality_result = llm_reviewer.review_code_quality(
                code_diff, json.dumps(complexity_metrics)
            )

            # ── 4. Confidence Scoring ───────────────────────────────
            print(f"[worker] Calculating confidence score...")
            confidence_result = confidence_scorer.calculate_score(
                requirement_result=req_result,
                security_result=sec_result,
                performance_result=perf_result,
                static_result=complexity_metrics,
                quality_result=quality_result,
                diff_data=pr_data,
            )

            # ── 5. Store Review + Findings ──────────────────────────
            review = db.query(Review).filter(
                Review.repo_name == repo_name,
                Review.pr_number == pr_number,
            ).first()

            if not review:
                review = Review(
                    repo_name=repo_name,
                    pr_number=pr_number,
                    pr_url=f"https://github.com/{repo_name}/pull/{pr_number}",
                )
                db.add(review)
                db.commit()
                db.refresh(review)

            # Merge all findings from each review pass
            all_findings_raw = (
                req_result.get("findings", [])
                + sec_result.get("findings", [])
                + perf_result.get("findings", [])
                + quality_result.get("findings", [])
            )

            combined = {"findings": all_findings_raw}
            combined.update(req_result)
            combined.update(sec_result)
            combined.update(perf_result)

            findings = aggregator.create_findings(review.id, combined, diff_analysis)
            for finding in findings:
                db.add(finding)

            # Update review record
            overall = aggregator.aggregate_scores(
                req_result.get("completeness_score", 50),
                sec_result.get("security_score", 50),
                perf_result.get("performance_score", 50),
                quality_result.get("quality_score", 70),
            )
            review.summary = (
                f"SmartCode AI Review: {len(findings)} finding(s). "
                f"Confidence: {confidence_result['confidence_score']}/100 "
                f"({confidence_result['verdict']}). "
                f"Overall score: {overall:.0f}/100."
            )
            review.status = "completed"
            review.completed_at = datetime.now(timezone.utc)
            review.confidence_score = confidence_result["confidence_score"]
            review.verdict = confidence_result["verdict"]
            review.score_breakdown = confidence_result["breakdown"]
            db.commit()

            # ── 6. Post GitHub Comment ──────────────────────────────
            print(f"[worker] Posting GitHub comment...")
            try:
                comment_body = _format_github_comment(
                    confidence_result, findings, review
                )
                github_client.post_review_comment(
                    repo_client, pr_number, comment_body
                )
            except Exception as comment_err:
                print(f"[worker] Warning: Could not post GitHub comment: {comment_err}")

            print(f"[worker] Analysis complete for {repo_name}#{pr_number}")
            return {
                "status": "success",
                "review_id": review.id,
                "confidence_score": confidence_result["confidence_score"],
                "verdict": confidence_result["verdict"],
                "findings_count": len(findings),
            }

        except Exception:
            import traceback
            traceback.print_exc()
            if review:
                review.status = "error"
                db.commit()
            raise
        finally:
            db.close()


    def _format_github_comment(confidence_result, findings, review):
        """Format the AI review as a GitHub PR comment."""
        score = confidence_result["confidence_score"]
        verdict = confidence_result["verdict"]
        breakdown = confidence_result.get("breakdown", {})

        verdict_emoji = {"APPROVE": "✅", "REVIEW_NEEDED": "⚠️", "CHANGES_REQUESTED": "❌"}
        emoji = verdict_emoji.get(verdict, "❓")

        # Header
        lines = [
            f"## 🤖 SmartCode AI Review\n",
            f"**PR Confidence Score: {score}/100** — {emoji} {verdict.replace('_', ' ')}\n",
        ]

        # Score breakdown table
        if breakdown:
            lines.append("### 📊 Score Breakdown\n")
            lines.append("| Dimension | Score |")
            lines.append("|-----------|-------|")
            dim_names = {
                "requirement_alignment": "Requirement Alignment",
                "security_safety": "Security Safety",
                "code_quality": "Code Quality",
                "test_coverage_signal": "Test Coverage",
                "static_analysis_clean": "Static Analysis",
            }
            for dim, name in dim_names.items():
                s = breakdown.get(dim, "—")
                lines.append(f"| {name} | {s}/100 |")
            lines.append("")

        # Findings
        if findings:
            lines.append(f"### 🔍 Findings ({len(findings)} issue{'s' if len(findings) != 1 else ''})\n")

            severity_icons = {
                "critical": "🔴 CRITICAL", "high": "🔴 HIGH",
                "medium": "🟡 MEDIUM", "low": "🟢 LOW", "info": "ℹ️ INFO",
            }

            for f in findings:
                sev = severity_icons.get(f.severity, f.severity)
                title = f.title or f.description[:80]
                lines.append(f"#### {sev} — {title}")
                lines.append(f"**File:** `{f.file_path}:{f.line_number}`\n")

                if f.code_snippet:
                    lines.append(f"```\n{f.code_snippet}\n```\n")

                if f.suggested_fix or f.suggestion:
                    fix = f.suggested_fix or f.suggestion
                    lines.append(f"**Suggested Fix:** {fix}\n")

                conf = f.confidence_score or 0
                refs = ""
                if f.references:
                    refs = " · ".join(f.references) if isinstance(f.references, list) else str(f.references)
                    refs = f" · **Ref:** {refs}"
                lines.append(f"**Confidence:** {conf:.0%}{refs}\n")
                lines.append("---\n")
        else:
            lines.append("### ✅ No issues found!\n")

        # Risk flags
        risk_flags = confidence_result.get("risk_flags", [])
        if risk_flags:
            lines.append("### ⚠️ Risk Flags\n")
            for flag in risk_flags:
                lines.append(f"- {flag}")
            lines.append("")

        # Recommendation
        rec = confidence_result.get("recommendation", "")
        if rec:
            lines.append(f"> 💡 **Recommendation:** {rec}\n")

        lines.append("> *Powered by [SmartCode](https://github.com/riyaa1611/SmartCode) — AI Code Review that understands intent*")

        return "\n".join(lines)

except Exception:
    # Celery (or other optional deps) not available — provide a no-op
    # analyze_pull_request with a .delay attribute so callers can use
    # `analyze_pull_request.delay(...)` without raising ImportError.
    def analyze_pull_request(repo_name: str, pr_number: int, installation_id: int):
        print(f"[worker] Celery not available — skipping analysis for {repo_name}#{pr_number}")
        return {"status": "skipped"}

    def _delay(repo_name: str, pr_number: int, installation_id: int):
        return analyze_pull_request(repo_name, pr_number, installation_id)

    analyze_pull_request.delay = _delay