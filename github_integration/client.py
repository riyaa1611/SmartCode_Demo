from github import Github
from github.AppAuthentication import AppAuthentication
import os
import re
from config import settings


class GitHubAppClient:
    """GitHub App client for authenticated API access and PR commenting."""

    def __init__(self):
        self.app_id = settings.github_app_id
        self.private_key = settings.github_private_key

    def get_installation_client(self, installation_id):
        """Get authenticated GitHub client for an installation."""
        auth = AppAuthentication(
            app_id=self.app_id,
            private_key=self.private_key,
            installation_id=installation_id,
        )
        return Github(auth=auth)

    def get_repo_client(self, installation_id, repo_name):
        """Get authenticated GitHub client for a specific repository."""
        client = self.get_installation_client(installation_id)
        return client.get_repo(repo_name)

    def post_review_comment(self, repo, pr_number, body):
        """Post (or update) a review comment on a PR.

        Parameters
        ----------
        repo : github.Repository.Repository
            PyGithub repository object (already authenticated).
        pr_number : int
            The pull-request number.
        body : str
            Markdown body of the comment.
        """
        pr = repo.get_pull(int(pr_number))
        # Check if SmartCode already left a comment — update it instead
        for comment in pr.get_issue_comments():
            if "🤖 SmartCode AI Review" in (comment.body or ""):
                comment.edit(body)
                print(f"[github] Updated existing review comment on PR #{pr_number}")
                return comment
        # No existing comment — create new one
        comment = pr.create_issue_comment(body)
        print(f"[github] Posted new review comment on PR #{pr_number}")
        return comment

    def parse_issue_references(self, text):
        """Parse issue references from text (#123, fixes #456, etc.)."""
        pattern = r'(?:fixes|closes|resolves)?\s*#(\d+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [int(match) for match in matches]