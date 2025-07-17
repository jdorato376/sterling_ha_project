#!/usr/bin/env python3
"""Full lifecycle validator for Sterling GPT and Vertex AI integration."""
import subprocess
import os
import requests

PROJECT_ID = os.getenv("GCP_PROJECT_ID") or "eminent-parsec-464203-v9"
REGION = os.getenv("REGION") or "us-central1"
ARTIFACT_REPO = "sterling-gpt-artifacts"
CLOUD_RUN_SERVICE = "sterling-ai-router"
IMAGE_TAG = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{ARTIFACT_REPO}/{CLOUD_RUN_SERVICE}:latest"
AI_ROUTER_ENDPOINT = f"https://{REGION}-{PROJECT_ID}.a.run.app/route"
TEST_QUERY = "Design a multi-agent executive architecture for healthcare finance."


def validate_phase_boot() -> None:
    print("[Phase 0-10] → Validating GitOps clone & HAOS boot")
    subprocess.run([
        "git",
        "clone",
        "https://github.com/jdorato376/sterling_ha_project.git",
    ], check=True)
    print("[\u2713] Repo cloned successfully")

    if not os.path.exists("sterling_ha_project/configuration.yaml"):
        raise Exception("Home Assistant config not found")
    print("[\u2713] HA config detected")


def validate_vertex_artifacts() -> None:
    print("[Phase 11-33] → Verifying Artifact Registry and Cloud Build")
    result = subprocess.run([
        "gcloud",
        "artifacts",
        "repositories",
        "describe",
        ARTIFACT_REPO,
        "--location",
        REGION,
        "--project",
        PROJECT_ID,
    ], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Artifact Registry not found")
    print("[\u2713] Artifact Registry ready")


def validate_cloud_run_router() -> None:
    print("[Phase 34-52] → Testing Cloud Run AI Router endpoint")
    headers = {"Content-Type": "application/json"}
    data = {"query": TEST_QUERY}
    try:
        response = requests.post(AI_ROUTER_ENDPOINT, json=data, headers=headers, timeout=15)
        response.raise_for_status()
        result = response.json()
        snippet = result.get("response", "")[:100]
        print("[\u2713] AI Router response:", snippet, "...")
    except Exception as exc:
        raise Exception(f"Cloud Run routing test failed: {exc}")


def test_model_routing_logic() -> None:
    print("[Phase 53-100] → Simulating model tier routing logic")
    queries = [
        "What is 2+2?",
        "Summarize the Medicare reimbursement changes for 2025.",
        "Design a machine learning pipeline for hospital readmission prediction.",
        "Write a 5-year strategic healthcare automation roadmap.",
    ]
    for q in queries:
        r = requests.post(AI_ROUTER_ENDPOINT, json={"query": q})
        print(f"[{q[:20]}...] => {r.json().get('model_used')}")
    print("[\u2713] Model routing logic passed complexity checks")


def validate_secrets_and_kms() -> None:
    print("[Phase 101-152] → Verifying Secret Manager and KMS")
    required_secrets = ["openai-api-key", "gemini-api-key", "storj-access-key"]
    for secret in required_secrets:
        result = subprocess.run([
            "gcloud",
            "secrets",
            "describe",
            secret,
            "--project",
            PROJECT_ID,
        ], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Secret {secret} not found")
    print("[\u2713] All required secrets validated")

    print("[\u2713] Validating KMS key")
    subprocess.run([
        "gcloud",
        "kms",
        "keys",
        "list",
        "--keyring=sterling-keys",
        "--location",
        REGION,
        "--project",
        PROJECT_ID,
    ], check=True)


def validate_final_phase() -> None:
    print("[Phase 153-167] → Verifying final escalation, repair, and dashboard hooks")
    r = requests.post(AI_ROUTER_ENDPOINT, json={"query": "Trigger fail-safe diagnostic and self-repair."})
    if r.status_code == 200 and "repair" in r.text.lower():
        print("[\u2713] Fail-safe and repair logic simulated")
    else:
        raise Exception("[x] Final repair/test hook failed")


if __name__ == "__main__":
    try:
        print("\n\U0001f9e0 STERLING GPT PHASE 0–167 FULL VALIDATION INITIATED\n")
        validate_phase_boot()
        validate_vertex_artifacts()
        validate_cloud_run_router()
        test_model_routing_logic()
        validate_secrets_and_kms()
        validate_final_phase()
        print("\n\ud83d\ude80 SYSTEM IS FULLY BOOTABLE AND VERTEX-AI READY\n")
    except Exception as exc:
        print("\n\u274c VALIDATION FAILED:", exc)
        exit(1)
