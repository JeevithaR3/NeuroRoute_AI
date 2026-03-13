"""
NeuroRoute Middleware — Layer 2
══════════════════════════════════════════════════════════════════════════════
Plug-and-play green AI routing middleware.
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import os
import yaml
from pathlib import Path
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.dirname(__file__))

from query_analyzer  import analyze_query
from routing_engine  import route, detect_hardware, detect_hardware_with_load
from model_executor  import execute
from logger          import log_query, log_feedback, get_stats, get_recent_queries, get_dataset_info

app = Flask(__name__)

# ── Track last used model ─────────────────────────────────────────────────────
_last_model_id   = None
_last_backend    = None


def _seed_from_log():
    """Restore last model from log after server restart."""
    global _last_model_id
    try:
        recent = get_recent_queries(1)
        if recent:
            _last_model_id = recent[0].get("model_id")
    except Exception:
        pass


_seed_from_log()

# ── CORS ──────────────────────────────────────────────────────────────────────

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/neuroroute/query", methods=["OPTIONS"])
@app.route("/neuroroute/feedback", methods=["OPTIONS"])
def options():
    return jsonify({}), 200


# ── Health ────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "NeuroRoute Middleware v1.0"})


# ── API Info ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({
        "name": "NeuroRoute — Green AI Routing Middleware",
        "version": "1.0.0",
        "description": "Plug-and-play intelligent green AI routing.",
        "endpoints": {
            "POST /neuroroute/query": "Route and execute a query",
            "POST /neuroroute/feedback": "Submit user feedback",
            "GET  /neuroroute/stats": "Cumulative green statistics",
            "GET  /neuroroute/queries": "Recent query log",
            "GET  /neuroroute/hardware": "Live CPU/GPU stats",
            "GET  /neuroroute/datasets": "ML dataset info",
            "GET  /health": "Health check",
        }
    })


# ── Main Query Endpoint ───────────────────────────────────────────────────────

@app.route("/neuroroute/query", methods=["POST"])
def process_query():

    global _last_model_id, _last_backend

    data = request.get_json(force=True)

    selected_text = (data.get("selected_text") or "").strip()
    task          = (data.get("task") or "ask").strip().lower()
    page_url      = data.get("page_url", "")
    page_title    = data.get("page_title", "")

    if not selected_text:
        return jsonify({"error": "selected_text is required"}), 400

    valid_tasks = {"ask","explain","summarize","simplify","analyze","research"}
    if task not in valid_tasks:
        task = "ask"

    # Analyze query
    analysis = analyze_query(selected_text, task)

    # Route model
    routing = route(analysis["complexity"])

    _last_model_id = routing["selected_model_id"]
    _last_backend  = "pending"

    # Execute model
    answer, latency = execute(
        routing["selected_model_id"],
        selected_text,
        task,
        analysis["complexity"],
    )

    _last_backend = _detect_backend(routing["selected_model_id"])

    hw = detect_hardware_with_load(_last_model_id, _last_backend)

    response_data = {

        "answer": answer,

        "model_used": routing["selected_model_name"],
        "model_id": routing["selected_model_id"],
        "complexity": analysis["complexity"],
        "domain": analysis["domain"],
        "task": task,

        "energy_used": f"{routing['energy_kwh']:.5f} kWh",
        "carbon": f"{routing['carbon_kg']:.5f} kg",
        "water": f"{routing['water_liters']:.5f} L",

        "latency": f"{latency:.2f}s",

        "compute_mode": hw.get("compute_mode","CPU"),
        "gpu_usage_pct": hw.get("gpu_usage_pct",0),
        "shift_score": hw.get("shift_score",0),
        "backend_used": _last_backend,

        "hardware": hw,
        "model_comparison": routing["model_comparison"]
    }

    log_query({
        "query_preview": selected_text[:100],
        "task": task,
        "complexity": analysis["complexity"],
        "domain": analysis["domain"],
        "model_id": routing["selected_model_id"],
        "model_name": routing["selected_model_name"],
        "energy_kwh": routing["energy_kwh"],
        "carbon_kg": routing["carbon_kg"],
        "water_liters": routing["water_liters"],
        "latency_seconds": latency,
        "word_count": analysis["word_count"],
        "page_url": page_url,
        "page_title": page_title,
        "compute_mode": hw.get("compute_mode","CPU"),
        "backend_used": _last_backend
    })

    return jsonify(response_data)


# ── Detect Backend ────────────────────────────────────────────────────────────

def _detect_backend(model_id: str):

    try:
        models_path = Path(__file__).parent / "models.yaml"

        with open(models_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        endpoint = cfg["models"][model_id].get("endpoint","")

        if "localhost" in endpoint or "127.0.0.1" in endpoint:
            return "local"

        return "cloud"

    except Exception:
        return "cloud"


# ── Feedback Endpoint ─────────────────────────────────────────────────────────

@app.route("/neuroroute/feedback", methods=["POST"])
def feedback():

    data = request.get_json(force=True)

    log_feedback({
        "query": data.get("query","")[:100],
        "feedback": data.get("feedback"),
        "model": data.get("model")
    })

    return jsonify({"status":"ok"})


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.route("/neuroroute/stats")
def stats():
    return jsonify(get_stats())


# ── Queries ───────────────────────────────────────────────────────────────────

@app.route("/neuroroute/queries")
def queries():

    limit = request.args.get("limit",50,type=int)

    return jsonify(get_recent_queries(limit))


# ── Dataset Info ──────────────────────────────────────────────────────────────

@app.route("/neuroroute/datasets")
def datasets():
    return jsonify(get_dataset_info())


# ── Hardware Stats ────────────────────────────────────────────────────────────

@app.route("/neuroroute/hardware")
def hardware_stats():
    return jsonify(detect_hardware_with_load(_last_model_id,_last_backend))


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":

    models_path = Path(__file__).parent / "models.yaml"

    with open(models_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    models = cfg.get("models", {})
    hw = detect_hardware()

    print("\n" + "═"*58)
    print("  ⬡  NeuroRoute Green AI Middleware — v1.0")
    print("═"*58)
    print(f"  Server  : http://localhost:3000")
    print(f"  CPU     : {hw['cpu_cores']} cores | {hw['ram_gb']} GB RAM | {hw['cpu_usage_pct']}% usage")

    gpu_line = (
        f"{hw['gpu_name']} — {hw['gpu_usage_pct']}% utilisation"
        if hw["gpu_available"]
        else "Not detected (cloud routing active)"
    )

    print(f"  GPU     : {gpu_line}")
    print(f"  Models  : {len(models)} configured")

    for mid, m in models.items():

        ep = m.get("endpoint","not set")
        local = "local" if ("localhost" in ep or "127.0.0.1" in ep) else "cloud"

        print(f"    [{mid}]  {m['name']} → {local} ({m.get('model_name','?')})")

    print(f"  Last model: {_last_model_id or 'none'}")
    print("═"*58 + "\n")

    app.run(host="0.0.0.0", port=3000, debug=True)