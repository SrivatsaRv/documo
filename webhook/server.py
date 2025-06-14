import os
import hmac
import hashlib
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="DocuMo Webhook Server")

class WebhookPayload(BaseModel):
    """Base webhook payload model."""
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
    pr_number = webhook_data.pull_request["number"]
    branch = webhook_data.pull_request["head"]["ref"]

    # TODO: Trigger documentation generation
    # This will be implemented when we create the agent runner

    return JSONResponse({
        "message": "Webhook received",
        "repo": repo_url,
        "pr": pr_number,
        "branch": branch
    })

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
    ) 