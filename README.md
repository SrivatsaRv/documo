# DocuMo - AI-Powered Repository Documentation Agent

DocuMo is an autonomous documentation generator that creates comprehensive documentation for GitHub/GitLab repositories when Pull Requests are created, updated, or merged. It uses GPT-4/Claude 3.5 to analyze your codebase and generate high-quality documentation automatically.

## Features

- 🚀 Automatic documentation generation on PR events
- 📝 High-quality markdown documentation
- 📊 Mermaid architecture diagrams
- 💬 PR comments with documentation summary
- 🔒 Runs entirely on-premises
- 🤖 Powered by GPT-4/Claude 3.5

## Prerequisites

- Python 3.11 or higher
- OpenAI API key or Anthropic API key
- GitHub App credentials or GitLab token
- Git installed on your system

## Detailed Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/documo.git
cd documo

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. GitHub App Setup (for GitHub integration)

1. Go to your GitHub account settings
2. Navigate to Developer Settings > GitHub Apps
3. Click "New GitHub App"
4. Fill in the following details:
   - Name: DocuMo
   - Homepage URL: Your server URL
   - Webhook URL: Your server URL/webhook/github
   - Webhook Secret: Generate a secure random string
   - Permissions needed:
     - Repository permissions:
       - Contents: Read
       - Pull requests: Read & Write
       - Metadata: Read
5. After creating the app, note down:
   - App ID
   - Generate and download the private key
   - Webhook secret

### 3. Environment Configuration

```bash
# Copy the environment template
cp config/env.example config/.env

# Edit the .env file with your credentials
nano config/.env
```

Required environment variables:
```env
# API Keys (at least one is required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# GitHub Configuration
GITHUB_APP_ID=your_github_app_id
GITHUB_PRIVATE_KEY=your_github_private_key  # Path to private key file
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Documentation Settings
DOCS_OUTPUT_DIR=output
ENABLE_PR_COMMENTS=true
```

### 4. Running the Server

#### Using Docker (Recommended for Production)

```bash
# Build the Docker image
docker build -t documo .

# Run the container
docker run -p 8000:8000 \
  --env-file config/.env \
  -v $(pwd)/output:/app/output \
  documo
```

#### Running Locally (Development)

```bash
# Start the webhook server
python -m webhook.server
```

The server will start on http://localhost:8000

### 5. Repository Configuration

#### GitHub Repository Setup

1. Go to your repository settings
2. Navigate to Webhooks
3. Click "Add webhook"
4. Configure the webhook:
   - Payload URL: `http://your-server:8000/webhook/github`
   - Content type: `application/json`
   - Secret: Your configured webhook secret
   - Events: Select "Pull request" events
   - Active: Checked

#### GitLab Repository Setup

1. Go to your repository settings
2. Navigate to Webhooks
3. Add new webhook:
   - URL: `http://your-server:8000/webhook/gitlab`
   - Secret token: Your configured webhook secret
   - Trigger: Pull request events
   - SSL verification: Enabled

## Usage

### Automatic Documentation Generation

1. Create a new Pull Request in your repository
2. DocuMo will automatically:
   - Analyze the codebase
   - Generate documentation
   - Create a PR comment with a summary
   - Add a link to the full documentation

### Manual Documentation Generation

You can also trigger documentation generation manually:

```python
from agent.agent_runner import DocumentationAgent
from utils.github_client import GitHubConfig

# Initialize the agent
config = GitHubConfig(
    app_id="your_app_id",
    private_key="path/to/private_key.pem",
    webhook_secret="your_webhook_secret"
)

agent = DocumentationAgent(
    openai_api_key="your_openai_api_key",
    github_config=config
)

# Generate documentation
await agent.generate_documentation(
    repo_url="https://github.com/username/repo",
    branch="main"
)
```

## Output Structure

The documentation will be generated in the `output` directory:
```
output/
└── guide.md  # Markdown documentation with Mermaid diagrams
```

The markdown file includes:
- Project overview
- Architecture diagram (Mermaid)
- Module documentation
- File listings
- Dependencies

## Architecture

DocuMo uses a modular, agent-based architecture:

- `agent/`: Core documentation generation logic
  - `tools/`: LangChain tools for repository operations
  - `agent_runner.py`: Main agent orchestration
- `webhook/`: FastAPI server for handling PR events
  - `server.py`: Webhook endpoint and event handling
- `docs_generator/`: Documentation generation
  - `markdown_writer.py`: Markdown generation and formatting
- `utils/`: API clients and utilities
  - `github_client.py`: GitHub API integration
  - `gitlab_client.py`: GitLab API integration

## Troubleshooting

### Common Issues

1. **Webhook Not Triggering**
   - Check webhook URL is accessible
   - Verify webhook secret matches
   - Check server logs for errors

2. **Documentation Not Generating**
   - Verify API keys are valid
   - Check repository permissions
   - Ensure Python version is 3.11+

3. **Mermaid Diagrams Not Rendering**
   - Diagrams are rendered by GitHub/GitLab
   - Verify markdown syntax is correct
   - Check for valid Mermaid syntax

### Logging

Enable debug mode in `.env`:
```env
DEBUG=true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Local Testing Setup

For local testing, you don't need to set up GitHub App webhooks. Here's how to test the agent directly:

### 1. Basic Local Configuration

Create a `.env` file in the `config` directory:

```env
# API Keys (at least one is required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Local Development Settings
DEBUG=true
DOCS_OUTPUT_DIR=output
```

### 2. Running the Agent Locally

Create a test script `test_agent.py`:

```python
import asyncio
from agent.agent_runner import DocumentationAgent
from utils.github_client import GitHubConfig

async def main():
    # For local testing, we can use a simple configuration
    config = GitHubConfig(
        app_id="local_test",
        private_key="",  # Not needed for local testing
        webhook_secret=""  # Not needed for local testing
    )

    # Initialize the agent
    agent = DocumentationAgent(
        openai_api_key="your_openai_api_key",
        github_config=config
    )

    # Generate documentation for a local repository
    doc = await agent.generate_documentation(
        repo_url="https://github.com/username/repo",  # Replace with your repo
        branch="main"
    )

    print(f"Documentation generated in: {doc}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run the test script:
```bash
python test_agent.py
```

### 3. Testing with Local Repository

You can also test with a local repository:

```python
import asyncio
from agent.agent_runner import DocumentationAgent
from utils.github_client import GitHubConfig
import os

async def main():
    config = GitHubConfig(
        app_id="local_test",
        private_key="",
        webhook_secret=""
    )

    agent = DocumentationAgent(
        openai_api_key="your_openai_api_key",
        github_config=config
    )

    # Use a local repository path
    local_repo_path = "/path/to/your/local/repo"
    
    # Generate documentation
    doc = await agent.generate_documentation(
        repo_url=f"file://{local_repo_path}",
        branch="main"
    )

    print(f"Documentation generated in: {doc}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Production Setup (with Webhooks)

When you're ready to deploy to production, you'll need to:

1. Set up a server with a public URL (e.g., using ngrok for testing)
2. Configure GitHub App webhooks to point to your server
3. Use the full configuration as described in the GitHub App Setup section

### Testing Webhooks Locally with ngrok

1. Install ngrok:
```bash
# On macOS with Homebrew
brew install ngrok

# Or download from https://ngrok.com/download
```

2. Start your DocuMo server:
```bash
python -m webhook.server
```

3. In a new terminal, start ngrok:
```bash
ngrok http 8000
```

4. Use the ngrok URL (e.g., `https://abc123.ngrok.io`) as your webhook URL in GitHub App settings. 