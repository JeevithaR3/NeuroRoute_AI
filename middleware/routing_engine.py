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

    # GPU detection + usage
    gpu_available = False
    gpu_name      = "None"
    gpu_usage_pct = 0
    gpu_mem_used  = 0
    gpu_mem_total = 0

    # Try nvidia-smi for NVIDIA GPUs
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
                gpu_mem_used  = round(float(parts[2]) / 1024, 1)   # MB → GB
                gpu_mem_total = round(float(parts[3]) / 1024, 1)
    except Exception:
        pass

    # Try GPUtil as fallback
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
        "cpu_cores":    cpu_count,
        "cpu_usage_pct": cpu_usage,
        "ram_gb":       ram_gb,
        "ram_used_gb":  ram_used,
        "ram_pct":      ram_pct,
        "gpu_available": gpu_available,
        "gpu_name":     gpu_name,
        "gpu_usage_pct": gpu_usage_pct,
        "gpu_mem_used_gb":  gpu_mem_used,
        "gpu_mem_total_gb": gpu_mem_total,
        "os":           platform.system(),
    }


def detect_hardware_with_load(last_model_id: str = None) -> dict:
    """
    Hardware stats PLUS compute-shift metadata.
    compute_mode: 'CPU' | 'GPU' | 'GPU_SHIFT'
    Always simulates GPU load when no real GPU reading > 0 is available,
    so the dashboard reflects actual model weight correctly.
    """
    import random, time
    hw = detect_hardware()

    heavy      = last_model_id in ("large_model", "medium_model")
    very_heavy = last_model_id == "large_model"

    # Treat as "no real GPU" if gpu_available=False OR gpu reads as 0
    # (some machines report gpu_available=True but 0% — still simulate)
    has_real_gpu = hw["gpu_available"] and hw["gpu_usage_pct"] > 0

    if has_real_gpu:
        # Real live GPU reading — use it, just annotate mode
        hw["gpu_simulated"] = False
        if very_heavy and hw["gpu_usage_pct"] > 15:
            hw["compute_mode"] = "GPU_SHIFT"
        elif hw["gpu_usage_pct"] > 5 or heavy:
            hw["compute_mode"] = "GPU"
        else:
            hw["compute_mode"] = "CPU"
    else:
        # Simulate GPU load based on which model is active
        rng = random.Random(int(time.time() / 5))   # smooth 5-second jitter

        if very_heavy:
            sim_gpu = rng.randint(62, 88)
            hw["compute_mode"] = "GPU_SHIFT"
        elif heavy:
            sim_gpu = rng.randint(35, 65)
            hw["compute_mode"] = "GPU"
        else:
            # small_model or idle — CPU primary, low GPU background
            sim_gpu = rng.randint(5, 16)
            hw["compute_mode"] = "CPU"

        hw["gpu_available"]    = True
        hw["gpu_name"]         = "Simulated GPU (no CUDA)"
        hw["gpu_usage_pct"]    = sim_gpu
        hw["gpu_mem_used_gb"]  = round(sim_gpu / 100 * 8, 1)
        hw["gpu_mem_total_gb"] = 8.0
        hw["gpu_simulated"]    = True

    # CPU effective load drops when GPU takes over
    if hw["compute_mode"] in ("GPU", "GPU_SHIFT"):
        hw["cpu_offload_pct"] = max(5, int(hw["cpu_usage_pct"] * 0.55))
    else:
        hw["cpu_offload_pct"] = hw["cpu_usage_pct"]

    # Shift score 0–100: how much compute has moved to GPU
    hw["shift_score"] = min(100, int(hw["gpu_usage_pct"] * 1.15))
    return hw


def estimate_environmental_impact(model_config: dict) -> dict:
    energy = model_config["energy_kwh"]
    carbon = energy * model_config["carbon_per_kwh"]
    water  = energy * model_config["water_per_kwh"]
    return {
        "energy_kwh":    round(energy, 5),
        "carbon_kg":     round(carbon, 5),
        "water_liters":  round(water,  5),
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

    # Filter candidate models by complexity capability
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

    # Score each candidate
    scored = {mid: compute_green_score(cfg, weights) for mid, cfg in candidates.items()}

    selected_id     = max(scored, key=scored.get)
    selected_config = models[selected_id]
    impact          = estimate_environmental_impact(selected_config)

    comparison = []
    for mid, score in scored.items():
        m = models[mid]
        comparison.append({
            "model_id":   mid,
            "name":       m["name"],
            "accuracy":   m["accuracy"],
            "green_score": score,
            "energy_kwh": m["energy_kwh"],
            "selected":   mid == selected_id,
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