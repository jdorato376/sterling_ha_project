import os
import time
import uuid

import vertexai
from vertexai.language_models import ChatModel


MODEL_TIERS = {
    "free": "gemini-1.5-flash",
    "economical": "gemini-1.5-pro",
    "premium": "gemini-2.5-pro",
}


def route_query(query: str, project_id: str | None = None) -> dict:
    """Route the query to an appropriate Vertex AI model."""
    project = project_id or os.getenv("GCP_PROJECT_ID")
    region = os.getenv("REGION", "us-central1")
    vertexai.init(project=project, location=region)

    complexity = "free"
    if "photo" in query or len(query.split()) > 100:
        complexity = "premium"
    elif len(query.split()) > 30:
        complexity = "economical"

    model = ChatModel.from_pretrained(MODEL_TIERS[complexity])
    chat = model.start_chat()
    response = chat.send_message(query)

    return {
        "query": query,
        "model_used": MODEL_TIERS[complexity],
        "response": response.text,
        "timestamp": time.time(),
        "request_id": str(uuid.uuid4()),
    }
