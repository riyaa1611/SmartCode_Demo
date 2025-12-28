import re
from typing import List

def parse_issue_references(text: str) -> List[int]:
    """Parse issue references from text (#123, fixes #456, etc.)"""
    if not text:
        return []
    
    # Match patterns like #123, fixes #456, closes #789
    pattern = r'(?:fixes|closes|resolves)?\s*#(\d+)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [int(match) for match in matches]

def extract_project_docs(repo_path: str) -> dict:
    """Extract project documentation from common files"""
    import os
    
    docs = {}
    
    # README.md
    readme_path = os.path.join(repo_path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            docs["readme"] = f.read()
    
    # CONTRIBUTING.md
    contributing_path = os.path.join(repo_path, "CONTRIBUTING.md")
    if os.path.exists(contributing_path):
        with open(contributing_path, "r", encoding="utf-8") as f:
            docs["contributing"] = f.read()
            
    # Docs folder
    docs_dir = os.path.join(repo_path, "docs")
    if os.path.exists(docs_dir):
        docs["architecture"] = {}
        for filename in os.listdir(docs_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(docs_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    docs["architecture"][filename] = f.read()
                    
    return docs