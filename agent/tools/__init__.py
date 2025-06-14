from typing import List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class RepoContext(BaseModel):
    """Context about the repository being documented."""
    repo_url: str
    branch: str
    pr_number: Optional[int] = None
    commit_sha: Optional[str] = None
    provider: str = Field(..., description="Either 'github' or 'gitlab'")

class ListRepoFilesTool(BaseTool):
    """Tool for listing files in a repository."""
    name = "list_repo_files"
    description = "Lists all relevant files in the repository, excluding tests and binaries"
    repo_context: RepoContext

    def _run(self, path: str = "") -> List[str]:
        """List files in the repository."""
        # Implementation will be added
        pass

class ReadFileContentTool(BaseTool):
    """Tool for reading file contents."""
    name = "read_file_content"
    description = "Reads the content of a specific file from the repository"
    repo_context: RepoContext

    def _run(self, file_path: str) -> str:
        """Read file content."""
        # Implementation will be added
        pass

class GenerateMarkdownTool(BaseTool):
    """Tool for generating markdown documentation."""
    name = "generate_markdown"
    description = "Generates markdown documentation for a specific module or component"
    repo_context: RepoContext

    def _run(self, module_path: str, context: str) -> str:
        """Generate markdown documentation."""
        # Implementation will be added
        pass

class GenerateMermaidTool(BaseTool):
    """Tool for generating Mermaid diagrams."""
    name = "generate_mermaid"
    description = "Generates Mermaid diagram code for architecture visualization"
    repo_context: RepoContext

    def _run(self, context: str, diagram_type: str = "flowchart") -> str:
        """Generate Mermaid diagram code."""
        # Implementation will be added
        pass 