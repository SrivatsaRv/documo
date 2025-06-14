import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from pathlib import Path
from github import Github
import tiktoken

class DocGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.encoding = tiktoken.encoding_for_model("gpt-4-turbo-preview")
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def _update_token_usage(self, response):
        """Update token usage statistics."""
        self.token_usage["total_tokens"] += response.usage.total_tokens
        self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
        self.token_usage["completion_tokens"] += response.usage.completion_tokens

    def _get_file_content(self, file_path: str) -> str:
        """Read file content from the repository."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _generate_doc_prompt(self, code: str, file_path: str) -> str:
        """Generate prompt for documentation."""
        return f"""Please analyze this code and generate comprehensive documentation:

File: {file_path}

Code:
{code}

Please provide:
1. A brief overview of what this code does
2. Key functions/classes and their purposes
3. Important parameters and return values
4. Any notable patterns or design decisions
5. Potential improvements or considerations

Format the response in markdown."""

    def generate_documentation(self, repo_path: str, files: List[str]) -> Dict[str, str]:
        """Generate documentation for the given files."""
        docs = {}
        
        for file_path in files:
            full_path = os.path.join(repo_path, file_path)
            code = self._get_file_content(full_path)
            
            # Generate documentation using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a documentation expert. Generate clear, concise, and helpful documentation."},
                    {"role": "user", "content": self._generate_doc_prompt(code, file_path)}
                ],
                temperature=0.3
            )
            
            self._update_token_usage(response)
            docs[file_path] = response.choices[0].message.content

        return docs

    def save_documentation(self, docs: Dict[str, str], pr_number: int):
        """Save generated documentation to files."""
        pr_dir = self.output_dir / f"pr_{pr_number}"
        pr_dir.mkdir(exist_ok=True)

        # Save individual file docs
        for file_path, content in docs.items():
            doc_path = pr_dir / f"{Path(file_path).stem}.md"
            with open(doc_path, 'w') as f:
                f.write(content)

        # Generate summary
        summary = self._generate_summary(docs, pr_number)
        with open(pr_dir / "summary.md", 'w') as f:
            f.write(summary)

        # Save token usage stats
        with open(pr_dir / "token_usage.json", 'w') as f:
            json.dump(self.token_usage, f, indent=2)

    def _generate_summary(self, docs: Dict[str, str], pr_number: int) -> str:
        """Generate a summary of all documentation."""
        summary_prompt = f"""Please create a summary of the documentation for PR #{pr_number}:

{json.dumps(docs, indent=2)}

Please provide:
1. Overall changes and their impact
2. Key files modified and their purposes
3. Any important considerations for reviewers

Format the response in markdown."""

        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a documentation expert. Create clear and concise summaries."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3
        )

        self._update_token_usage(response)
        return response.choices[0].message.content

    def post_to_github(self, repo_name: str, pr_number: int):
        """Post documentation summary to GitHub PR."""
        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Read summary and token usage
            pr_dir = self.output_dir / f"pr_{pr_number}"
            with open(pr_dir / "summary.md", 'r') as f:
                summary = f.read()
            
            with open(pr_dir / "token_usage.json", 'r') as f:
                token_usage = json.load(f)

            # Create comment with summary and token usage
            comment = f"""## 📚 Documentation Summary

{summary}

---
### Token Usage Statistics
- Total Tokens: {token_usage['total_tokens']}
- Prompt Tokens: {token_usage['prompt_tokens']}
- Completion Tokens: {token_usage['completion_tokens']}
- Estimated Cost: ${(token_usage['total_tokens'] / 1000) * 0.03:.4f} USD
"""

            pr.create_issue_comment(comment)
            return True
        except Exception as e:
            print(f"Error posting to GitHub: {str(e)}")
            return False 