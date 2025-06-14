import asyncio
import os
from dotenv import load_dotenv
from agent.agent_runner import DocumentationAgent
from utils.github_client import GitHubConfig

# Load environment variables
load_dotenv('config/.env')

async def main():
    # Get API key from environment
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    # For local testing, we can use a simple configuration
    config = GitHubConfig(
        app_id="local_test",
        private_key="",  # Not needed for local testing
        webhook_secret=""  # Not needed for local testing
    )

    # Initialize the agent
    agent = DocumentationAgent(
        openai_api_key=openai_api_key,
        github_config=config
    )

    # Test with a public repository
    test_repo = "https://github.com/yourusername/your-repo"  # Replace with your repo
    print(f"Generating documentation for {test_repo}...")

    try:
        doc = await agent.generate_documentation(
            repo_url=test_repo,
            branch="main"
        )
        print(f"Documentation generated successfully!")
        print(f"Check the output directory for guide.md")
    except Exception as e:
        print(f"Error generating documentation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 