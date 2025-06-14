import os
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class ModuleInfo(BaseModel):
    """Information about a module."""
    name: str
    description: str
    files: List[str]
    dependencies: List[str]

class Documentation(BaseModel):
    """Complete documentation structure."""
    project_name: str
    description: str
    modules: List[ModuleInfo]
    architecture_diagram: str
    generated_at: datetime = datetime.now()

class MarkdownWriter:
    def __init__(self, output_dir: str = "output"):
        """Initialize markdown writer."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def write_documentation(self, doc: Documentation) -> str:
        """Write complete documentation to markdown file."""
        content = self._generate_markdown(doc)
        output_path = os.path.join(self.output_dir, "guide.md")
        
        with open(output_path, "w") as f:
            f.write(content)
        
        return output_path

    def _generate_markdown(self, doc: Documentation) -> str:
        """Generate markdown content."""
        content = [
            f"# {doc.project_name} Documentation",
            f"\n*Generated on {doc.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*\n",
            f"\n## Project Overview\n{doc.description}\n",
            "\n## Architecture\n",
            "```mermaid",
            doc.architecture_diagram,
            "```\n",
            "\n## Module Documentation\n"
        ]

        for module in doc.modules:
            content.extend([
                f"\n### {module.name}",
                f"\n{module.description}\n",
                "\n#### Files",
                "\n```",
                *[f"- {file}" for file in module.files],
                "```\n",
                "\n#### Dependencies",
                "\n```",
                *[f"- {dep}" for dep in module.dependencies],
                "```\n"
            ])

        return "\n".join(content)

    def generate_pr_summary(self, doc: Documentation) -> str:
        """Generate a summary for PR comment."""
        return f"""## Documentation Generated

I've generated documentation for this project. Here's a quick summary:

### Project Overview
{doc.description}

### Modules Documented
{len(doc.modules)} modules have been documented, including:
{chr(10).join(f"- {module.name}" for module in doc.modules)}

[View Full Documentation](guide.md)
""" 