import os
import openai

MODEL_CONFIG = {
    "economical": {
        "name": "gpt-3.5-turbo",
        "provider": "openai",
        "input_price_per_million": 0.50,
        "output_price_per_million": 1.50,
    },
    "premium": {
        "name": "gemini-1.5-pro-latest",
        "provider": "vertex",
        "input_price_per_million": 3.50,
        "output_price_per_million": 10.50,
    },
    "free": {
        "name": "local-classifier",
        "provider": "internal",
        "input_price_per_million": 0.0,
        "output_price_per_million": 0.0,
    }
}


def analyze_query_complexity(query):
    length = len(query.split())
    if any(keyword in query for keyword in ["architect", "pipeline", "generate a full app"]):
        return "critical"
    elif "image" in query.lower() or "photo" in query.lower():
        return "premium"
    elif length > 100:
        return "complex"
    elif length < 10:
        return "simple"
    return "moderate"


def estimate_cost(model_key, input_tokens, output_tokens):
    cfg = MODEL_CONFIG.get(model_key, MODEL_CONFIG["free"])
    return (input_tokens / 1e6) * cfg["input_price_per_million"] + (output_tokens / 1e6) * cfg["output_price_per_million"]


def execute_llm_call(model_key, query):
    model = MODEL_CONFIG[model_key]["name"]
    provider = MODEL_CONFIG[model_key]["provider"]
    if provider == "openai":
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        completion = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": query}])
        return completion.choices[0].message.content
    elif provider == "vertex":
        openai.api_key = os.environ.get("GEMINI_API_KEY")
        openai.api_base = "https://generativelanguage.googleapis.com/v1beta/openai"
        completion = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": query}])
        return completion.choices[0].message.content
    return f"Local response to: {query}"


def route_query(query):
    complexity = analyze_query_complexity(query)
    model_key = {
        "simple": "free",
        "moderate": "economical",
        "complex": "premium",
        "critical": "premium",
    }.get(complexity, "free")
    input_tokens = len(query.split())
    output_tokens = input_tokens * 3
    cost = estimate_cost(model_key, input_tokens, output_tokens)
    response = execute_llm_call(model_key, query)
    return {"model": model_key, "cost": round(cost, 4), "response": response}
