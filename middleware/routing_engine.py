"""
NeuroRoute Green Routing Engine
Selects the most energy-efficient AI model for a given query complexity.
Now includes live CPU and GPU usage monitoring.
"""

import yaml
import os
import platform
import multiprocessing
import psutil


def load_model_registry() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "models.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def detect_hardware() -> dict:
    """Detect hardware + live CPU/GPU/RAM usage."""
    cpu_count = multiprocessing.cpu_count()
    cpu_usage  = psutil.cpu_percent(interval=0.2)

    mem        = psutil.virtual_memory()
    ram_gb     = round(mem.total   / (1024 ** 3), 1)
    ram_used   = round(mem.used    / (1024 ** 3), 1)
    ram_pct    = mem.percent

    gpu_available = False
    gpu_name      = "None"
    gpu_usage_pct = 0
    gpu_mem_used  = 0
    gpu_mem_total = 0

    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = [p.strip() for p in result.stdout.strip().split(",")]
            if len(parts) >= 4:
                gpu_available = True
                gpu_name      = parts[0]
                gpu_usage_pct = float(parts[1])
                gpu_mem_used  = round(float(parts[2]) / 1024, 1)
                gpu_mem_total = round(float(parts[3]) / 1024, 1)
    except Exception:
        pass

    if not gpu_available:
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                g = gpus[0]
                gpu_available = True
                gpu_name      = g.name
                gpu_usage_pct = g.load * 100
                gpu_mem_used  = round(g.memoryUsed / 1024, 1)
                gpu_mem_total = round(g.memoryTotal / 1024, 1)
        except Exception:
            pass

    return {
        "cpu_cores":          cpu_count,
        "cpu_usage_pct":      cpu_usage,
        "ram_gb":             ram_gb,
        "ram_used_gb":        ram_used,
        "ram_pct":            ram_pct,
        "gpu_available":      gpu_available,
        "gpu_name":           gpu_name,
        "gpu_usage_pct":      gpu_usage_pct,
        "gpu_mem_used_gb":    gpu_mem_used,
        "gpu_mem_total_gb":   gpu_mem_total,
        "os":                 platform.system(),
    }


def estimate_environmental_impact(model_config: dict) -> dict:
    energy = model_config["energy_kwh"]
    carbon = energy * model_config["carbon_per_kwh"]
    water  = energy * model_config["water_per_kwh"]
    return {
        "energy_kwh":   round(energy, 5),
        "carbon_kg":    round(carbon, 5),
        "water_liters": round(water,  5),
    }


def compute_green_score(model_config: dict, weights: dict) -> float:
    MAX_CARBON  = 0.004
    MAX_WATER   = 0.015
    MAX_LATENCY = 5.0

    accuracy = model_config["accuracy"]
    impact   = estimate_environmental_impact(model_config)
    latency  = model_config["latency_seconds"]

    norm_carbon  = impact["carbon_kg"]    / MAX_CARBON
    norm_water   = impact["water_liters"] / MAX_WATER
    norm_latency = latency                / MAX_LATENCY

    score = (
        weights.get("accuracy", 0.5) * accuracy
        - weights.get("carbon",  0.25) * norm_carbon
        - weights.get("water",   0.15) * norm_water
        - weights.get("latency", 0.10) * norm_latency
    )
    return round(score, 4)


def route(complexity: str) -> dict:
    registry  = load_model_registry()
    models    = registry["models"]
    weights   = registry.get("routing_weights", {})
    hardware  = detect_hardware()

    complexity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    query_level = complexity_order.get(complexity, 1)

    candidates = {}
    for model_id, config in models.items():
        model_max = complexity_order.get(config.get("max_complexity", "HIGH"), 2)
        if model_max >= query_level:
            if model_id == "large_model" and not hardware["gpu_available"]:
                if query_level < 2:
                    continue
            candidates[model_id] = config

    if not candidates:
        candidates = {k: v for k, v in models.items() if k == "medium_model"}

    scored = {mid: compute_green_score(cfg, weights) for mid, cfg in candidates.items()}

    selected_id     = max(scored, key=scored.get)
    selected_config = models[selected_id]
    impact          = estimate_environmental_impact(selected_config)

    comparison = []
    for mid, score in scored.items():
        m = models[mid]
        comparison.append({
            "model_id":    mid,
            "name":        m["name"],
            "accuracy":    m["accuracy"],
            "green_score": score,
            "energy_kwh":  m["energy_kwh"],
            "selected":    mid == selected_id,
        })
    comparison.sort(key=lambda x: x["green_score"], reverse=True)

    return {
        "selected_model_id":   selected_id,
        "selected_model_name": selected_config["name"],
        "accuracy":            selected_config["accuracy"],
        "latency_seconds":     selected_config["latency_seconds"],
        "energy_kwh":          impact["energy_kwh"],
        "carbon_kg":           impact["carbon_kg"],
        "water_liters":        impact["water_liters"],
        "hardware":            hardware,
        "model_comparison":    comparison,
    }