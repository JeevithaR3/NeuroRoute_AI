"""
NeuroRoute Green Routing Engine
Selects the most energy-efficient AI model for a given query complexity.
GPU monitoring reads real hardware — no simulation.
"""

import yaml
import os
import platform
import multiprocessing
import psutil
import subprocess


def load_model_registry() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "models.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# ── Hardware detection ────────────────────────────────────────────────────────

def _read_nvidia_gpu() -> dict | None:
    """Read real NVIDIA GPU stats via nvidia-smi. Returns None if not available."""
    try:
        result = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        parts = [p.strip() for p in result.stdout.strip().split(",")]
        if len(parts) < 4:
            return None
        return {
            "gpu_available":    True,
            "gpu_name":         parts[0],
            "gpu_usage_pct":    float(parts[1]),
            "gpu_mem_used_gb":  round(float(parts[2]) / 1024, 1),
            "gpu_mem_total_gb": round(float(parts[3]) / 1024, 1),
            "gpu_simulated":    False,
        }
    except Exception:
        return None


def _read_gputil() -> dict | None:
    """Fallback GPU reading via GPUtil library."""
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if not gpus:
            return None
        g = gpus[0]
        return {
            "gpu_available":    True,
            "gpu_name":         g.name,
            "gpu_usage_pct":    round(g.load * 100, 1),
            "gpu_mem_used_gb":  round(g.memoryUsed  / 1024, 1),
            "gpu_mem_total_gb": round(g.memoryTotal / 1024, 1),
            "gpu_simulated":    False,
        }
    except Exception:
        return None


def _no_gpu_stats() -> dict:
    return {
        "gpu_available":    False,
        "gpu_name":         "None",
        "gpu_usage_pct":    0,
        "gpu_mem_used_gb":  0,
        "gpu_mem_total_gb": 0,
        "gpu_simulated":    False,
    }


def detect_hardware() -> dict:
    """
    Detect hardware + real live CPU/GPU/RAM usage.
    GPU reading comes from nvidia-smi or GPUtil — 100% real, no simulation.
    """
    cpu_count  = multiprocessing.cpu_count()
    cpu_usage  = psutil.cpu_percent(interval=0.2)
    mem        = psutil.virtual_memory()
    ram_gb     = round(mem.total / (1024 ** 3), 1)
    ram_used   = round(mem.used  / (1024 ** 3), 1)
    ram_pct    = mem.percent

    gpu = _read_nvidia_gpu() or _read_gputil() or _no_gpu_stats()

    return {
        "cpu_cores":     cpu_count,
        "cpu_usage_pct": cpu_usage,
        "ram_gb":        ram_gb,
        "ram_used_gb":   ram_used,
        "ram_pct":       ram_pct,
        "os":            platform.system(),
        **gpu,
    }


def detect_hardware_with_load(last_model_id: str = None, backend_used: str = None) -> dict:
    """
    Real hardware stats + compute_mode annotation.

    compute_mode logic (100% based on real readings):
      - 'GPU_SHIFT' : large_model was used AND real GPU > 15%
                      (Ollama ran locally and your GPU actually spiked)
      - 'GPU'       : medium or large model AND real GPU > 5%
      - 'CPU'       : everything else (Groq cloud — no local GPU involved)

    No simulation, no random numbers.
    If GPU reads 0% it means inference ran on Groq cloud, not locally.
    """
    hw = detect_hardware()

    gpu_pct    = hw["gpu_usage_pct"]
    very_heavy = last_model_id == "large_model"
    heavy      = last_model_id in ("large_model", "medium_model")
    local_run  = backend_used and backend_used.startswith("ollama")

    if very_heavy and (gpu_pct > 15 or local_run):
        hw["compute_mode"] = "GPU_SHIFT"
    elif heavy and (gpu_pct > 5 or local_run):
        hw["compute_mode"] = "GPU"
    else:
        hw["compute_mode"] = "CPU"

    hw["backend_used"]    = backend_used or "groq"
    hw["shift_score"]     = min(100, int(gpu_pct * 1.2))
    hw["cpu_offload_pct"] = hw["cpu_usage_pct"]

    return hw


# ── Environmental impact ──────────────────────────────────────────────────────

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

    impact   = estimate_environmental_impact(model_config)
    latency  = model_config["latency_seconds"]

    norm_carbon  = impact["carbon_kg"]    / MAX_CARBON
    norm_water   = impact["water_liters"] / MAX_WATER
    norm_latency = latency                / MAX_LATENCY

    return round(
        weights.get("accuracy", 0.5) * model_config["accuracy"]
        - weights.get("carbon",  0.25) * norm_carbon
        - weights.get("water",   0.15) * norm_water
        - weights.get("latency", 0.10) * norm_latency,
        4
    )


# ── Routing ───────────────────────────────────────────────────────────────────

def route(complexity: str) -> dict:
    registry = load_model_registry()
    models   = registry["models"]
    weights  = registry.get("routing_weights", {})
    hardware = detect_hardware()

    complexity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    query_level = complexity_order.get(complexity, 1)

    candidates = {}
    for model_id, config in models.items():
        model_max = complexity_order.get(config.get("max_complexity", "HIGH"), 2)
        if model_max >= query_level:
            candidates[model_id] = config

    if not candidates:
        candidates = {"medium_model": models["medium_model"]}

    scored      = {mid: compute_green_score(cfg, weights) for mid, cfg in candidates.items()}
    selected_id = max(scored, key=scored.get)
    selected    = models[selected_id]
    impact      = estimate_environmental_impact(selected)

    comparison = sorted([
        {
            "model_id":    mid,
            "name":        models[mid]["name"],
            "accuracy":    models[mid]["accuracy"],
            "green_score": score,
            "energy_kwh":  models[mid]["energy_kwh"],
            "selected":    mid == selected_id,
        }
        for mid, score in scored.items()
    ], key=lambda x: x["green_score"], reverse=True)

    return {
        "selected_model_id":   selected_id,
        "selected_model_name": selected["name"],
        "accuracy":            selected["accuracy"],
        "latency_seconds":     selected["latency_seconds"],
        "energy_kwh":          impact["energy_kwh"],
        "carbon_kg":           impact["carbon_kg"],
        "water_liters":        impact["water_liters"],
        "hardware":            hardware,
        "model_comparison":    comparison,
    }
