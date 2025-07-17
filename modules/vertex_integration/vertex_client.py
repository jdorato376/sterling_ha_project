"""
Phase 1: Vertex AI Client Stub
Calls deployed model endpoint using GCP SDK.
"""
from google.cloud import aiplatform
import os

def predict(query: str) -> str:
    endpoint = os.getenv("VERTEX_ENDPOINT")
    client = aiplatform.Endpoint(endpoint)
    response = client.predict([{"content": query}])
    return response.predictions[0]
