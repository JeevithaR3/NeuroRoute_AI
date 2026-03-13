"""
NeuroRoute Middleware — Layer 2
Main Flask API server: Green AI Router
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import os
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.dirname(__file__))

from query_analyzer import analyze_query
from routing_engine import route, detect_hardware
from model_executor import execute
from logger import log_query, log_feedback, get_stats, get_recent_queries, get_dataset_info

app = Flask(__name__)


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/neuroroute/query", methods=["OPTIONS"])
@app.route("/neuroroute/feedback", methods=["OPTIONS"])
def options():
    return jsonify({}), 200


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "NeuroRoute Middleware v1.0"})


@app.route("/")
def index():
    return jsonify({
        "name": "NeuroRoute Green AI Middleware",
        "version": "1.0.0",
        "description": "Intelligent green AI routing",
        "endpoints": {
            "POST /neuroroute/query":    "Process a query",
            "POST /neuroroute/feedback": "Submit user feedback",
            "GET /neuroroute/stats":     "System statistics",
            "GET /neuroroute/queries":   "Recent query log",
            "GET /neuroroute/hardware":  "Live CPU/GPU usage",
            "GET /health":               "Health check",
        },
    })


@app.route("/neuroroute/query", methods=["POST"])
def process_query():
    data = request.get_json(force=True)

    selected_text = (data.get("selected_text") or "").strip()
    task          = (data.get("task") or "ask").strip().lower()
    page_url      = data.get("page_url", "")
    page_title    = data.get("page_title", "")

    if not selected_text:
        return jsonify({"error": "selected_text is required"}), 400

    valid_tasks = {"ask", "explain", "summarize", "simplify", "analyze", "research"}
    if task not in valid_tasks:
        task = "ask"

    analysis = analyze_query(selected_text, task)
    routing  = route(analysis["complexity"])

    answer, actual_latency = execute(
        routing["selected_model_id"],
        selected_text,
        task,
        analysis["complexity"],
    )

    response_data = {
        "answer":           answer,
        "model_used":       routing["selected_model_name"],
        "model_id":         routing["selected_model_id"],
        "complexity":       analysis["complexity"],
        "domain":           analysis["domain"],
        "task":             task,
        "energy_used":      f"{routing['energy_kwh']:.5f} kWh",
        "carbon":           f"{routing['carbon_kg']:.5f} kg",
        "water":            f"{routing['water_liters']:.5f} L",
        "latency":          f"{actual_latency:.2f}s",
        "hardware":         routing["hardware"],
        "model_comparison": routing["model_comparison"],
    }

    log_query({
        "query_preview":   selected_text[:100],
        "task":            task,
        "complexity":      analysis["complexity"],
        "domain":          analysis["domain"],
        "model_id":        routing["selected_model_id"],
        "model_name":      routing["selected_model_name"],
        "energy_kwh":      routing["energy_kwh"],
        "carbon_kg":       routing["carbon_kg"],
        "water_liters":    routing["water_liters"],
        "latency_seconds": actual_latency,
        "word_count":      analysis["word_count"],
        "page_url":        page_url,
        "page_title":      page_title,
    })

    return jsonify(response_data)


@app.route("/neuroroute/feedback", methods=["POST"])
def feedback():
    data = request.get_json(force=True)
    log_feedback({
        "query":    data.get("query", "")[:100],
        "feedback": data.get("feedback"),
        "model":    data.get("model"),
    })
    return jsonify({"status": "ok"})


@app.route("/neuroroute/stats")
def stats():
    return jsonify(get_stats())


@app.route("/neuroroute/queries")
def queries():
    limit = request.args.get("limit", 50, type=int)
    return jsonify(get_recent_queries(limit))


@app.route("/neuroroute/datasets")
def datasets():
    return jsonify(get_dataset_info())


@app.route("/neuroroute/hardware")
def hardware_stats():
    return jsonify(detect_hardware())


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  ⬡  NeuroRoute Green AI Middleware — Layer 2")
    print("=" * 55)
    print("  Server   : http://localhost:3000")
    hw = detect_hardware()
    print(f"  CPU      : {hw['cpu_cores']} cores | {hw['ram_gb']} GB RAM | {hw['cpu_usage_pct']}% usage")
    print(f"  GPU      : {'Available ✓ — ' + hw['gpu_name'] if hw['gpu_available'] else 'Not detected (CPU mode)'}")
    print("=" * 55 + "\n")
    app.run(host="0.0.0.0", port=3000, debug=True)