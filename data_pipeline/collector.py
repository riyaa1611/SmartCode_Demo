from github import Github
from utils.helpers import parse_issue_references
from typing import Dict, List, Any
import json

class DataCollector:
    def __init__(self, github_client: Github):
        self.github_client = github_client
        
    def collect_pr_data(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Collect all data for a pull request"""
        repo = self.github_client.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))
        
        # Collect PR data
        pr_data = {
            "pr_id": pr_number,
            "title": pr.title,
            "description": pr.body,
            "author": pr.user.login,
            "files_changed": [],
            "diff": "",
            "commit_messages": [],
            "issue_context": {},
            "project_docs": {},
            "timestamp": pr.created_at.isoformat()
        }
        
        # Collect changed files
        files = pr.get_files()
        for file in files:
            pr_data["files_changed"].append({
                "filename": file.filename,
                "status": file.status,  # added, modified, removed
                "patch": file.patch or ""
            })
            
        # Collect commits
        commits = pr.get_commits()
        for commit in commits:
            pr_data["commit_messages"].append(commit.commit.message)
            
        # Parse issue references
        issue_numbers = parse_issue_references(pr.body or "")
        pr_data["issue_numbers"] = issue_numbers
        
        # Collect linked issues
        if issue_numbers:
            pr_data["issue_context"] = self.collect_issue_data(repo, issue_numbers)
            
        return pr_data
        
    def collect_issue_data(self, repo, issue_numbers: List[int]) -> Dict[str, Any]:
        """Collect data from linked issues"""
        issues_data = {}
        
        for issue_num in issue_numbers:
            try:
                issue = repo.get_issue(issue_num)
                issues_data[issue_num] = {
                    "title": issue.title,
                    "body": issue.body,
                    "comments": []
                }
                
                # Collect comments
                comments = issue.get_comments()
                for comment in comments:
                    issues_data[issue_num]["comments"].append({
                        "author": comment.user.login,
                        "body": comment.body,
                        "created_at": comment.created_at.isoformat()
                    })
            except Exception as e:
                print(f"Error collecting issue {issue_num}: {e}")
                
        return issues_data
        
    def collect_project_context(self, repo_name: str) -> Dict[str, Any]:
        """Collect project documentation context"""
        repo = self.github_client.get_repo(repo_name)
        
        context = {
            "readme": "",
            "contributing": "",
            "architecture_docs": {}
        }
        
        try:
            # Get README.md
            readme = repo.get_contents("README.md")
            context["readme"] = readme.decoded_content.decode("utf-8")
        except:
            pass
            
        try:
            # Get CONTRIBUTING.md
            contributing = repo.get_contents("CONTRIBUTING.md")
            context["contributing"] = contributing.decoded_content.decode("utf-8")
        except:
            pass
            
        try:
            # Get docs folder contents
            docs_dir = repo.get_contents("docs")
            if isinstance(docs_dir, list):
                for file in docs_dir:
                    if file.name.endswith(".md"):
                        content = repo.get_contents(file.path)
                        context["architecture_docs"][file.name] = content.decoded_content.decode("utf-8")
        except:
            pass
            
        return context