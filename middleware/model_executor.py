"""
NeuroRoute Model Executor
Uses Groq (free, cloud, no download needed) to generate accurate answers.

Setup:
  1. Sign up free at https://console.groq.com
  2. Go to API Keys → Create Key
  3. pip install groq
  4. Set your key:
       Mac/Linux:  export GROQ_API_KEY=gsk_xxxxxxxx
       Windows:    set GROQ_API_KEY=gsk_xxxxxxxx
  5. Restart the server — done!

Free tier limits (very generous):
  llama-3.1-8b-instant     → 14,400 requests/day, 30 req/min
  llama-3.3-70b-versatile  → 14,400 requests/day, 30 req/min
  gemma2-9b-it             → 14,400 requests/day, 30 req/min

Model mapping:
  small_model  -> llama-3.1-8b-instant    (ultra fast, simple queries)
  medium_model -> gemma2-9b-it            (balanced, good quality)
  large_model  -> llama-3.3-70b-versatile (best quality, complex queries)
"""

import time
import os

try:
    from groq import Groq
    _client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    _HAS_GROQ = True
except ImportError:
    _HAS_GROQ = False
    _client = None

MODEL_MAP = {
    "small_model":  "llama-3.1-8b-instant",
    "medium_model": "llama-3.1-8b-instant",
    "large_model":  "llama-3.3-70b-versatile",
}

SYSTEM_PROMPTS = {
    "summarize": (
        "You are a precise summarization assistant. "
        "Read the given text carefully and provide a clear, accurate summary "
        "that captures the key points. Be concise but complete. "
        "Do not add information that is not in the text."
    ),
    "explain": (
        "You are a clear and helpful explanation assistant. "
        "Explain the given text or concept in a way that is easy to understand. "
        "Break down complex ideas into simple terms with examples where helpful."
    ),
    "ask": (
        "You are a knowledgeable assistant. "
        "Answer the question or respond to the text accurately and helpfully. "
        "Be direct and factual."
    ),
    "simplify": (
        "You are a simplification assistant. "
        "Rewrite or explain the given text in the simplest possible language "
        "as if explaining to someone with no background on the topic. "
        "Use plain words, short sentences, and relatable analogies."
    ),
    "analyze": (
        "You are an analytical assistant. "
        "Provide a deep, structured analysis of the given text. "
        "Identify key themes, arguments, implications, and any notable patterns."
    ),
    "research": (
        "You are a research assistant. "
        "Provide comprehensive information about the given topic, "
        "covering key facts, context, and important details."
    ),
}

USER_PROMPTS = {
    "summarize": "Please summarize the following text:\n\n{text}",
    "explain":   "Please explain the following:\n\n{text}",
    "ask":       "Please answer or respond to the following:\n\n{text}",
    "simplify":  "Please simplify the following text into plain, easy language:\n\n{text}",
    "analyze":   "Please analyze the following text in depth:\n\n{text}",
    "research":  "Please provide detailed information about the following:\n\n{text}",
}


def execute(selected_model_id: str, text: str, task: str, complexity: str):
    """
    Execute the selected model using Groq (free cloud API).
    Returns (answer_string, elapsed_seconds).
    """
    start = time.time()

    if not _HAS_GROQ:
        answer = (
            "Groq package not installed.\n\n"
            "Run: pip install groq\n"
            "Then restart the server."
        )
    elif not os.environ.get("GROQ_API_KEY"):
        answer = (
            "No Groq API key found.\n\n"
            "Get your free key at: https://console.groq.com\n\n"
            "Then set it:\n"
            "  Mac/Linux:  export GROQ_API_KEY=gsk_xxxxxxxx\n"
            "  Windows:    set GROQ_API_KEY=gsk_xxxxxxxx\n\n"
            "Then restart the server."
        )
    else:
        answer = _call_groq(selected_model_id, text, task)

    elapsed = round(time.time() - start, 2)
    return answer, elapsed


def _call_groq(model_id: str, text: str, task: str) -> str:
    """Call Groq cloud API — free, fast, no download needed."""
    groq_model = MODEL_MAP.get(model_id, "llama-3.1-8b-instant")
    system     = SYSTEM_PROMPTS.get(task, SYSTEM_PROMPTS["ask"])
    user_msg   = USER_PROMPTS.get(task, USER_PROMPTS["ask"]).format(text=text)

    max_tokens = {
        "small_model":  300,
        "medium_model": 500,
        "large_model":  1024,
    }.get(model_id, 500)

    try:
        chat_completion = _client.chat.completions.create(
            model=groq_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        err = str(e)
        if "401" in err or "invalid_api_key" in err.lower():
            return (
                "Invalid Groq API key.\n\n"
                "Check your key at https://console.groq.com\n"
                "Make sure you copied it correctly."
            )
        elif "429" in err or "rate_limit" in err.lower():
            return (
                "Groq free tier rate limit hit.\n\n"
                "You've exceeded 30 requests/minute or 14,400/day.\n"
                "Wait a moment and try again."
            )
        elif "model_not_found" in err.lower():
            return (
                f"Model '{groq_model}' not available on your Groq plan.\n\n"
                "Try switching to: llama-3.1-8b-instant"
            )
        else:
            return f"Groq API error: {err}"