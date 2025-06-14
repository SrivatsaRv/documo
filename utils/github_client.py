import os
from typing import List, Optional
from github import Github, Auth
from github.Repository import Repository
from github.ContentFile import ContentFile
from pydantic import BaseModel

class GitHubConfig(BaseModel):
    """GitHub configuration."""
    app_id: str
    private_key: str
    webhook_secret: str

class GitHubClient:
    def __init__(self, config: GitHubConfig):
        """Initialize GitHub client."""
        self.config = config
        self.auth = Auth.AppAuth(
            app_id=config.app_id,
            private_key=config.private_key
        )
        self.client = Github(auth=self.auth)

    def get_repository(self, repo_url: str) -> Repository:
        """Get repository object from URL."""
        # Convert URL to owner/repo format
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1]
        return self.client.get_repo(f"{owner}/{repo}")

    def list_files(self, repo: Repository, path: str = "", branch: str = "main") -> List[str]:
        """List files in repository, excluding tests and binaries."""
        contents = repo.get_contents(path, ref=branch)
        files = []
        
        for content in contents:
            if content.type == "dir":
                files.extend(self.list_files(repo, content.path, branch))
            elif content.type == "file":
                # Skip test files and binaries
                if not any(x in content.path.lower() for x in [
                    'test_', '_test', '.test', 'tests/', 'test/', '.pyc', '.so', '.dll'
                ]):
                    files.append(content.path)
        
        return files

    def get_file_content(self, repo: Repository, file_path: str, branch: str = "main") -> str:
        """Get content of a specific file."""
        try:
            content = repo.get_contents(file_path, ref=branch)
            if isinstance(content, ContentFile):
                return content.decoded_content.decode('utf-8')
            return ""
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return ""

    def create_pr_comment(self, repo: Repository, pr_number: int, comment: str) -> None:
        """Create a comment on a pull request."""
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment) 