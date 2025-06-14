import os
from typing import List, Optional
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage

from .tools import (
    ListRepoFilesTool,
    ReadFileContentTool,
    GenerateMarkdownTool,
    GenerateMermaidTool,
    RepoContext
)
from docs_generator.markdown_writer import Documentation, ModuleInfo, MarkdownWriter
from utils.github_client import GitHubClient, GitHubConfig

class DocumentationAgent:
    def __init__(
        self,
        openai_api_key: str,
        github_config: GitHubConfig,
        output_dir: str = "output"
    ):
        """Initialize documentation agent."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Initialize GitHub client
        self.github_client = GitHubClient(github_config)

        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4",
            openai_api_key=openai_api_key
        )

        # Initialize tools
        self.tools = [
            ListRepoFilesTool,
            ReadFileContentTool,
            GenerateMarkdownTool,
            GenerateMermaidTool
        ]

        # Initialize agent
        self.agent = self._create_agent()

        # Initialize document generator
        self.markdown_writer = MarkdownWriter(output_dir)

    def _create_agent(self):
        """Create and configure the agent."""
        system_message = SystemMessage(content="""You are an expert software documentation agent.
Your task is to analyze codebases and generate comprehensive documentation.
Follow these steps:
1. List and analyze repository files
2. Understand the project structure
3. Generate module-level documentation
4. Create architecture diagrams
5. Write clear, concise documentation

Be thorough but concise. Focus on the most important aspects of the codebase.""")

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        return initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            system_message=system_message,
            verbose=True
        )

    async def generate_documentation(
        self,
        repo_url: str,
        branch: str,
        pr_number: Optional[int] = None
    ) -> Documentation:
        """Generate documentation for a repository."""
        # Create repository context
        repo_context = RepoContext(
            repo_url=repo_url,
            branch=branch,
            pr_number=pr_number,
            provider="github"
        )

        # Get repository
        repo = self.github_client.get_repository(repo_url)

        # List files
        files = self.github_client.list_files(repo, branch=branch)

        # Generate documentation using agent
        result = await self.agent.arun(
            f"Generate documentation for repository {repo_url}",
            repo_context=repo_context
        )

        # Parse agent output and create documentation
        doc = Documentation(
            project_name=repo.name,
            description=result.get("description", ""),
            modules=[
                ModuleInfo(
                    name=module["name"],
                    description=module["description"],
                    files=module["files"],
                    dependencies=module["dependencies"]
                )
                for module in result.get("modules", [])
            ],
            architecture_diagram=result.get("architecture_diagram", "")
        )

        # Write markdown
        markdown_path = self.markdown_writer.write_documentation(doc)

        # Post PR comment if applicable
        if pr_number and os.getenv("ENABLE_PR_COMMENTS", "true").lower() == "true":
            comment = self.markdown_writer.generate_pr_summary(doc)
            self.github_client.create_pr_comment(repo, pr_number, comment)

        return doc 