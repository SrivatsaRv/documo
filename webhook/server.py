import os
import hmac
import hashlib
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from doc_generator import DocGenerator

# Load environment variables
load_dotenv()

# Initialize FastAPI application with title for better API documentation
app = FastAPI(title="DocuMo Webhook Server")

# Initialize documentation generator
doc_generator = DocGenerator()

class WebhookPayload(BaseModel):
    """Base webhook payload model for GitHub events.
    
    This model captures the essential information from GitHub webhook events,
    including repository details and pull request information when available.
    """
    repository: dict
    pull_request: Optional[dict] = None
    action: Optional[str] = None
    ref: Optional[str] = None

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature:
        return False
    
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.post("/webhook/github")
@app.get("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """Handle GitHub webhook events."""
    if x_github_event != "pull_request":
        return JSONResponse({"message": "Ignoring non-PR event"})

    # Verify webhook signature
    payload = await request.body()
    if not verify_github_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    data = await request.json()
    webhook_data = WebhookPayload(**data)

    # Only process PR events
    if not webhook_data.pull_request:
        return JSONResponse({"message": "Not a PR event"})

    # Extract relevant information
    repo_url = webhook_data.repository["html_url"]
    repo_name = webhook_data.repository["full_name"]
    pr_number = webhook_data.pull_request["number"]
    branch = webhook_data.pull_request["head"]["ref"]
    
    # Get list of modified files from the PR
    modified_files = [
        file["filename"] 
        for file in webhook_data.pull_request.get("files", [])
    ]

    if not modified_files:
        return JSONResponse({
            "message": "No files modified in PR",
            "repo": repo_url,
            "pr": pr_number
        })

    try:
        # Generate documentation for modified files
        docs = doc_generator.generate_documentation(".", modified_files)
        
        # Save documentation
        doc_generator.save_documentation(docs, pr_number)

        # Post to GitHub PR
        doc_generator.post_to_github(repo_name, pr_number)

        return JSONResponse({
            "message": "Documentation generated and posted successfully",
            "repo": repo_url,
            "pr": pr_number,
            "files": modified_files,
            "docs_generated": list(docs.keys())
        })
    except Exception as e:
        return JSONResponse({
            "message": f"Error generating documentation: {str(e)}",
            "repo": repo_url,
            "pr": pr_number
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    ) # Dummy change for webhook test
