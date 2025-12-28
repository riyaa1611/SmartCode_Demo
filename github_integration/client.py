from github import Github
from github.AppAuthentication import AppAuthentication
import os
from config import settings

class GitHubAppClient:
    def __init__(self):
        self.app_id = settings.github_app_id
        self.private_key = settings.github_private_key
        
    def get_installation_client(self, installation_id):
        """Get authenticated GitHub client for an installation"""
        auth = AppAuthentication(
            app_id=self.app_id,
            private_key=self.private_key,
            installation_id=installation_id
        )
        return Github(auth=auth)
        
    def get_repo_client(self, installation_id, repo_name):
        """Get authenticated GitHub client for a specific repository"""
        client = self.get_installation_client(installation_id)
        return client.get_repo(repo_name)
        
    def parse_issue_references(self, text):
        """Parse issue references from text (#123, fixes #456, etc.)"""
        import re
        # Match patterns like #123, fixes #456, closes #789
        pattern = r'(?:fixes|closes|resolves)?\s*#(\d+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [int(match) for match in matches]