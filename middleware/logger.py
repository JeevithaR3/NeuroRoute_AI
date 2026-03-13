"""
NeuroRoute Logger
Handles structured logging of all query events for monitoring and dataset creation.

Every query is AUTOMATICALLY:
  1. Appended to queries.json  (full log)
  2. Appended to queries.csv   (raw log)
  3. Appended to all 3 ML dataset CSVs (live, no manual rebuild needed)
  4. Stats snapshot updated    (stats_snapshot.json)
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path


LOG_DIR      = Path(__file__).parent.parent / "backend" / "logs"
DATASET_DIR  = Path(__file__).parent.parent / "backend" / "datasets"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)

JSON_LOG      = LOG_DIR / "queries.json"
CSV_LOG       = LOG_DIR / "queries.csv"
FEEDBACK_LOG  = LOG_DIR / "feedback.json"
STATS_FILE    = DATASET_DIR / "stats_snapshot.json"

# Dataset file paths (written live on every query)
DS_ROUTING    = DATASET_DIR / "routing_classifier_dataset.csv"
DS_ENV        = DATASET_DIR / "environmental_impact_dataset.csv"
DS_FULL       = DATASET_DIR / "full_neuroroute_dataset.csv"

CSV_FIELDS = [
    "timestamp", "query_preview", "task", "complexity", "domain",
    "model_id", "model_name", "energy_kwh", "carbon_kg", "water_liters",
    "latency_seconds", "word_count",
]

ROUTING_FIELDS = ["timestamp", "query_preview", "word_count", "task", "domain", "label_complexity"]
ENV_FIELDS     = ["timestamp", "model_id", "model_name", "complexity", "task",
                  "energy_kwh", "carbon_kg", "water_liters", "latency_seconds"]
FULL_FIELDS    = ["timestamp", "query_preview", "task", "domain", "complexity",
                  "word_count", "model_id", "model_name", "energy_kwh",
                  "carbon_kg", "water_liters", "latency_seconds", "page_url"]


def log_query(event: dict):
    """
    Called automatically after every query.
    Writes to ALL logs and ALL datasets — no manual rebuild ever needed.
    """
    event["timestamp"] = datetime.utcnow().isoformat()

    # 1. Append to master JSON log
    _append_json(JSON_LOG, event)

    # 2. Append to raw CSV log
    _append_csv(CSV_LOG, event, CSV_FIELDS, {
        "timestamp":       event.get("timestamp"),
        "query_preview":   event.get("query_preview", "")[:60],
        "task":            event.get("task"),
        "complexity":      event.get("complexity"),
        "domain":          event.get("domain"),
        "model_id":        event.get("model_id"),
        "model_name":      event.get("model_name"),
        "energy_kwh":      event.get("energy_kwh"),
        "carbon_kg":       event.get("carbon_kg"),
        "water_liters":    event.get("water_liters"),
        "latency_seconds": event.get("latency_seconds"),
        "word_count":      event.get("word_count"),
    })

    # 3a. Live-append to routing classifier dataset
    _append_csv(DS_ROUTING, event, ROUTING_FIELDS, {
        "timestamp":        event.get("timestamp"),
        "query_preview":    event.get("query_preview", "")[:60],
        "word_count":       event.get("word_count", 0),
        "task":             event.get("task"),
        "domain":           event.get("domain"),
        "label_complexity": event.get("complexity"),
    })

    # 3b. Live-append to environmental impact dataset
    _append_csv(DS_ENV, event, ENV_FIELDS, {
        "timestamp":       event.get("timestamp"),
        "model_id":        event.get("model_id"),
        "model_name":      event.get("model_name"),
        "complexity":      event.get("complexity"),
        "task":            event.get("task"),
        "energy_kwh":      event.get("energy_kwh"),
        "carbon_kg":       event.get("carbon_kg"),
        "water_liters":    event.get("water_liters"),
        "latency_seconds": event.get("latency_seconds"),
    })

    # 3c. Live-append to full dataset
    _append_csv(DS_FULL, event, FULL_FIELDS, {
        "timestamp":       event.get("timestamp"),
        "query_preview":   event.get("query_preview", "")[:60],
        "task":            event.get("task"),
        "domain":          event.get("domain"),
        "complexity":      event.get("complexity"),
        "word_count":      event.get("word_count", 0),
        "model_id":        event.get("model_id"),
        "model_name":      event.get("model_name"),
        "energy_kwh":      event.get("energy_kwh"),
        "carbon_kg":       event.get("carbon_kg"),
        "water_liters":    event.get("water_liters"),
        "latency_seconds": event.get("latency_seconds"),
        "page_url":        event.get("page_url", ""),
    })

    # 4. Refresh stats snapshot JSON
    _refresh_stats_snapshot()

    # 5. Print to CLI
    _print_cli_event(event)


def log_feedback(feedback_event: dict):
    """Log user feedback."""
    feedback_event["timestamp"] = datetime.utcnow().isoformat()
    _append_json(FEEDBACK_LOG, feedback_event)


def get_stats() -> dict:
    """
    Returns stats. First tries the live snapshot (instant),
    falls back to recomputing from JSON log.
    """
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return _compute_stats()


def get_recent_queries(limit: int = 50) -> list:
    """Return the most recent logged queries."""
    events = _read_json_log(JSON_LOG)
    return list(reversed(events[-limit:]))


def get_dataset_info() -> dict:
    """Return info about live dataset files."""
    files = {}
    for ds in [DS_ROUTING, DS_ENV, DS_FULL]:
        if ds.exists():
            size = ds.stat().st_size
            with open(ds) as f:
                rows = sum(1 for _ in f) - 1
            files[ds.name] = {"rows": max(rows, 0), "size_bytes": size, "path": str(ds)}
        else:
            files[ds.name] = {"rows": 0, "size_bytes": 0, "path": str(ds)}
    return files


# ─── Internal stats computation ───────────────────────────────────────────────

def _compute_stats() -> dict:
    events = _read_json_log(JSON_LOG)
    if not events:
        return {
            "total_queries": 0,
            "total_energy_kwh": 0,
            "total_carbon_kg": 0,
            "total_water_liters": 0,
            "model_usage": {},
            "avg_latency": 0,
            "complexity_breakdown": {},
            "dataset_files": get_dataset_info(),
        }

    total_energy  = sum(e.get("energy_kwh", 0) for e in events)
    total_carbon  = sum(e.get("carbon_kg", 0) for e in events)
    total_water   = sum(e.get("water_liters", 0) for e in events)
    total_latency = sum(e.get("latency_seconds", 0) for e in events)

    model_usage = {}
    complexity_breakdown = {}
    for e in events:
        mid = e.get("model_id", "unknown")
        model_usage[mid] = model_usage.get(mid, 0) + 1
        c = e.get("complexity", "MEDIUM")
        complexity_breakdown[c] = complexity_breakdown.get(c, 0) + 1

    n = len(events)
    return {
        "total_queries": n,
        "total_energy_kwh": round(total_energy, 5),
        "total_carbon_kg": round(total_carbon, 5),
        "total_water_liters": round(total_water, 5),
        "model_usage": model_usage,
        "avg_latency": round(total_latency / n, 2),
        "complexity_breakdown": complexity_breakdown,
        "dataset_files": get_dataset_info(),
    }


def _refresh_stats_snapshot():
    """Rewrite the stats snapshot after every query (keeps dashboard instant)."""
    stats = _compute_stats()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


# ─── Low-level helpers ────────────────────────────────────────────────────────

def _append_json(path: Path, event: dict):
    events = _read_json_log(path)
    events.append(event)
    with open(path, "w") as f:
        json.dump(events, f, indent=2)


def _read_json_log(path: Path) -> list:
    if not path.exists():
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def _append_csv(path: Path, event: dict, fields: list, row: dict):
    """Append one row to a CSV dataset file, writing header if new."""
    file_exists = path.exists()
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _print_cli_event(event: dict):
    """Print a formatted CLI event log."""
    sep = "=" * 50
    print(f"\n{sep}")
    print("  ⬡ NeuroRoute — Query Processed")
    print(sep)
    print(f"  Query    : {event.get('query_preview', '')[:55]}")
    print(f"  Task     : {event.get('task', '—').upper()}")
    print(f"  Domain   : {event.get('domain', '—')}")
    print(f"  Complexity: {event.get('complexity', '—')}")
    print(f"  Model    : {event.get('model_name', '—')}")
    print(f"  Energy   : {event.get('energy_kwh', 0):.5f} kWh")
    print(f"  CO₂      : {event.get('carbon_kg', 0):.5f} kg")
    print(f"  Water    : {event.get('water_liters', 0):.5f} L")
    print(f"  Latency  : {event.get('latency_seconds', 0):.2f} s")
    print(sep)