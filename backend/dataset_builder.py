#!/usr/bin/env python3
"""
NeuroRoute Dataset Builder — Layer 3
Converts query logs into structured ML training datasets.

Usage:
  python3 dataset_builder.py              # Build all datasets
  python3 dataset_builder.py --export     # Export to datasets/ folder
  python3 dataset_builder.py --summary    # Print dataset summary
"""

import sys
import os
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent / "middleware"))
from logger import get_recent_queries, get_stats

DATASETS_DIR = Path(__file__).parent / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)


def build_routing_dataset(queries: list) -> list:
    """
    Dataset for training a Query Complexity Classifier.
    Input: query text features → Output: complexity label
    """
    rows = []
    for q in queries:
        rows.append({
            "query_preview": q.get("query_preview", ""),
            "word_count": q.get("word_count", 0),
            "task": q.get("task", ""),
            "domain": q.get("domain", ""),
            "label_complexity": q.get("complexity", ""),
        })
    return rows


def build_environmental_dataset(queries: list) -> list:
    """
    Dataset for training an Environmental Impact Estimator.
    Input: model + complexity → Output: energy, carbon, water
    """
    rows = []
    for q in queries:
        rows.append({
            "model_id": q.get("model_id", ""),
            "model_name": q.get("model_name", ""),
            "complexity": q.get("complexity", ""),
            "task": q.get("task", ""),
            "energy_kwh": q.get("energy_kwh", 0),
            "carbon_kg": q.get("carbon_kg", 0),
            "water_liters": q.get("water_liters", 0),
            "latency_seconds": q.get("latency_seconds", 0),
        })
    return rows


def build_full_dataset(queries: list) -> list:
    """
    Full dataset combining all features for Green Routing model training.
    """
    rows = []
    for q in queries:
        rows.append({
            "timestamp": q.get("timestamp", ""),
            "query_preview": q.get("query_preview", ""),
            "task": q.get("task", ""),
            "domain": q.get("domain", ""),
            "complexity": q.get("complexity", ""),
            "word_count": q.get("word_count", 0),
            "model_id": q.get("model_id", ""),
            "model_name": q.get("model_name", ""),
            "energy_kwh": q.get("energy_kwh", 0),
            "carbon_kg": q.get("carbon_kg", 0),
            "water_liters": q.get("water_liters", 0),
            "latency_seconds": q.get("latency_seconds", 0),
            "page_url": q.get("page_url", ""),
        })
    return rows


def save_csv(rows: list, filename: str) -> Path:
    if not rows:
        return None
    path = DATASETS_DIR / filename
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def save_json(data: object, filename: str) -> Path:
    path = DATASETS_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def print_summary(queries: list, stats: dict):
    n = len(queries)
    print("\n" + "=" * 55)
    print("  ⬡  NeuroRoute Dataset Summary")
    print("=" * 55)
    print(f"  Total Records     : {n}")

    if n == 0:
        print("  No data yet.\n")
        return

    # Complexity distribution
    cx_counts = Counter(q.get("complexity") for q in queries)
    print(f"\n  Complexity Distribution:")
    for level in ["LOW", "MEDIUM", "HIGH"]:
        count = cx_counts.get(level, 0)
        pct = round(count / n * 100) if n else 0
        print(f"    {level:<10} {count:>5} ({pct}%)")

    # Task distribution
    task_counts = Counter(q.get("task") for q in queries)
    print(f"\n  Task Distribution:")
    for task, count in task_counts.most_common():
        print(f"    {task:<14} {count:>5}")

    # Model distribution
    model_counts = Counter(q.get("model_id") for q in queries)
    print(f"\n  Model Routing:")
    for model, count in model_counts.most_common():
        pct = round(count / n * 100)
        print(f"    {model:<20} {count:>4} ({pct}%)")

    # Environmental totals
    print(f"\n  Environmental Impact:")
    print(f"    Total Energy : {stats.get('total_energy_kwh', 0):.5f} kWh")
    print(f"    Total CO₂   : {stats.get('total_carbon_kg', 0):.5f} kg")
    print(f"    Total Water : {stats.get('total_water_liters', 0):.5f} L")

    print("\n  Saved Datasets:")
    for f in sorted(DATASETS_DIR.glob("*.csv")):
        size = f.stat().st_size
        print(f"    📄 {f.name:<40} {size:>6} bytes")
    for f in sorted(DATASETS_DIR.glob("*.json")):
        size = f.stat().st_size
        print(f"    📄 {f.name:<40} {size:>6} bytes")

    print("=" * 55 + "\n")


def build_all():
    queries = get_recent_queries(10000)
    stats = get_stats()

    routing_ds = build_routing_dataset(queries)
    env_ds = build_environmental_dataset(queries)
    full_ds = build_full_dataset(queries)

    save_csv(routing_ds,  "routing_classifier_dataset.csv")
    save_csv(env_ds,      "environmental_impact_dataset.csv")
    save_csv(full_ds,     "full_neuroroute_dataset.csv")
    save_json(full_ds,    "full_neuroroute_dataset.json")
    save_json(stats,      "system_stats_snapshot.json")

    print_summary(queries, stats)
    print(f"  ✓ Datasets written to: {DATASETS_DIR}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NeuroRoute Dataset Builder")
    parser.add_argument("--summary", action="store_true", help="Print summary only")
    args = parser.parse_args()

    queries = get_recent_queries(10000)
    stats = get_stats()

    if args.summary:
        print_summary(queries, stats)
    else:
        build_all()
