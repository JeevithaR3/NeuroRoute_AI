"""
NeuroRoute — Universal Model Executor
══════════════════════════════════════════════════════════════════════════════
Calls ANY OpenAI-compatible endpoint defined in models.yaml.

Works with:
  • Groq          (https://api.groq.com/openai/v1/chat/completions)
  • OpenAI        (https://api.openai.com/v1/chat/completions)
  • Ollama local  (http://localhost:11434/v1/chat/completions)
  • Together AI   (https://api.together.xyz/v1/chat/completions)
  • vLLM          (http://localhost:8000/v1/chat/completions)
  • LM Studio     (http://localhost:1234/v1/chat/completions)
  • Azure OpenAI  (your deployment URL)
  • Any server    that speaks POST /v1/chat/completions

No Groq SDK. No vendor lock-in. Pure HTTP.
══════════════════════════════════════════════════════════════════════════════
"""

import os
import time
import json
import urllib.request
import urllib.error
import yaml
from pathlib import Path


# ── Load model registry ───────────────────────────────────────────────────────

def _load_registry() -> dict:
    path = Path(__file__).parent / "models.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


# ── Default system + user prompts ─────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "summarize": (
        "You are a precise summarization assistant. "
        "Read the given text carefully and provide a clear, accurate summary "
        "that captures the key points. Be concise but complete."
    ),
    "explain": (
        "You are a clear and helpful explanation assistant. "
        "Explain the given text or concept in simple, easy-to-understand terms."
    ),
    "ask": (
        "You are a knowledgeable assistant. "
        "Answer the question accurately and helpfully. Be direct and factual."
    ),
    "simplify": (
        "You are a simplification assistant. "
        "Rewrite the given text in the simplest possible language."
    ),
    "analyze": (
        "You are an analytical assistant. "
        "Provide a deep, structured analysis covering key themes and implications."
    ),
    "research": (
        "You are a research assistant. "
        "Provide comprehensive, well-structured information covering key facts and context."
    ),
}

USER_PROMPTS = {
    "summarize": "Please summarize the following text:\n\n{text}",
    "explain":   "Please explain the following:\n\n{text}",
    "ask":       "Please answer or respond to the following:\n\n{text}",
    "simplify":  "Please simplify the following text:\n\n{text}",
    "analyze":   "Please analyze the following text in depth:\n\n{text}",
    "research":  "Please provide detailed information about the following:\n\n{text}",
}


# ── Main entry point ──────────────────────────────────────────────────────────

def execute(model_id: str, text: str, task: str, complexity: str):
    """
    Execute a query against the model defined for `model_id` in models.yaml.

    Steps:
      1. Load model config from models.yaml
      2. Read API key from the environment variable named in `api_key_env`
      3. Build OpenAI-format request payload
      4. POST to the configured endpoint
      5. Return (answer_string, elapsed_seconds)

    Returns:
        tuple: (answer: str, elapsed: float)
    """
    start = time.time()

    registry     = _load_registry()
    models       = registry.get("models", {})
    model_config = models.get(model_id)

    if not model_config:
        return f"[NeuroRoute] Model '{model_id}' not found in models.yaml", 0.0

    answer  = _call_model(model_config, text, task)
    elapsed = round(time.time() - start, 2)

    return answer, elapsed


# ── Universal OpenAI-compatible caller ────────────────────────────────────────

def _call_model(config: dict, text: str, task: str) -> str:
    """
    Call any OpenAI-compatible endpoint using pure urllib (no SDK needed).

    Reads:
      config["endpoint"]    → URL to POST to
      config["api_key_env"] → name of the env var holding the API key
      config["model_name"]  → model string to send in the request
      config["max_tokens"]  → max tokens for the response
    """
    endpoint   = config.get("endpoint", "").strip()
    key_env    = config.get("api_key_env", "").strip()
    model_name = config.get("model_name", "").strip()
    max_tokens = int(config.get("max_tokens", 512))

    # ── Validate config ───────────────────────────────────────────────────────
    if not endpoint:
        return (
            "[NeuroRoute Config Error]\n"
            "No 'endpoint' defined for this model in models.yaml.\n"
            "Add:  endpoint: 'https://your-api.com/v1/chat/completions'"
        )

    if not model_name:
        return (
            "[NeuroRoute Config Error]\n"
            "No 'model_name' defined for this model in models.yaml.\n"
            "Add:  model_name: 'your-model-id'"
        )

    # ── Resolve API key ───────────────────────────────────────────────────────
    api_key = ""
    if key_env:
        api_key = os.environ.get(key_env, "").strip()
        if not api_key:
            return (
                f"[NeuroRoute Auth Error]\n"
                f"Environment variable '{key_env}' is not set or is empty.\n\n"
                f"Fix:\n"
                f"  export {key_env}=your_api_key_here\n"
                f"Then restart the NeuroRoute server."
            )

    # ── Build prompts ─────────────────────────────────────────────────────────
    system_prompt = SYSTEM_PROMPTS.get(task, SYSTEM_PROMPTS["ask"])
    user_prompt   = USER_PROMPTS.get(task, USER_PROMPTS["ask"]).format(text=text)

    # ── Build payload ─────────────────────────────────────────────────────────
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens":  max_tokens,
        "temperature": 0.7,
    }

    # ── Build headers ─────────────────────────────────────────────────────────
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # ── Make request ──────────────────────────────────────────────────────────
    try:
        req = urllib.request.Request(
            url     = endpoint,
            data    = json.dumps(payload).encode("utf-8"),
            headers = headers,
            method  = "POST",
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            data   = json.loads(resp.read().decode("utf-8"))
            answer = data["choices"][0]["message"]["content"].strip()
            return answer

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
            err  = json.loads(body)
            msg  = err.get("error", {}).get("message", body)
        except Exception:
            msg = body or str(e)

        if e.code == 401:
            return (
                f"[NeuroRoute Auth Error — 401]\n"
                f"API key rejected by {endpoint}.\n"
                f"Check the value of '{config.get('api_key_env', 'your key env var')}'.\n"
                f"Detail: {msg}"
            )
        elif e.code == 429:
            return (
                "[NeuroRoute Rate Limit — 429]\n"
                "Too many requests. Wait a moment and try again.\n"
                f"Detail: {msg}"
            )
        elif e.code == 404:
            return (
                f"[NeuroRoute 404]\n"
                f"Endpoint not found: {endpoint}\n"
                f"Check 'endpoint' and 'model_name' in models.yaml.\n"
                f"Detail: {msg}"
            )
        else:
            return f"[NeuroRoute HTTP {e.code}] {msg}"

    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "Connection refused" in reason or "111" in reason:
            return (
                f"[NeuroRoute Connection Error]\n"
                f"Cannot reach: {endpoint}\n\n"
                f"If using a local model (Ollama / vLLM / LM Studio):\n"
                f"  → Make sure the local server is running\n"
                f"  → Ollama:    ollama serve\n"
                f"  → vLLM:      python -m vllm.entrypoints.openai.api_server ...\n"
                f"  → LM Studio: start the local server in the app"
            )
        return f"[NeuroRoute Network Error] {reason}"

    except Exception as e:
        return f"[NeuroRoute Unexpected Error] {type(e).__name__}: {e}"
