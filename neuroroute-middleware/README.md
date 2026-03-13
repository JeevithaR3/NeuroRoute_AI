# NeuroRoute Middleware

> **Plug-and-play green AI routing. Bring your own models.**

NeuroRoute sits between your application and your AI models. It analyzes every query, picks the most energy-efficient model capable of answering it, executes it, and returns the answer along with full environmental impact data.

---

## How it works

```
Your App
   │
   ▼
POST /neuroroute/query
   │
   ▼
┌─────────────────────────────────────────┐
│           NeuroRoute Middleware          │
│                                         │
│  1. Complexity analysis                 │
│     LOW / MEDIUM / HIGH                 │
│                                         │
│  2. Green scoring                       │
│     Score = 0.5×Accuracy               │
│           − 0.25×NormCarbon            │
│           − 0.15×NormWater             │
│           − 0.10×NormLatency           │
│                                         │
│  3. Route to best model                 │
│     LOW    → your small/fast model      │
│     MEDIUM → your balanced model        │
│     HIGH   → your large/powerful model  │
│                                         │
│  4. Execute via universal HTTP adapter  │
│     (any OpenAI-compatible endpoint)    │
│                                         │
│  5. Return answer + green metrics       │
└─────────────────────────────────────────┘
   │
   ▼
{
  "answer":       "...",
  "model_used":   "Small LLM",
  "complexity":   "LOW",
  "energy_used":  "0.00100 kWh",
  "carbon":       "0.00040 kg",
  "water":        "0.00150 L",
  "compute_mode": "CPU",
  "latency":      "0.31s"
}
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure your models
Edit `models.yaml`. For each of the three tiers, set:
```yaml
models:
  small_model:
    endpoint:    "https://your-api.com/v1/chat/completions"
    api_key_env: "YOUR_API_KEY"      # name of env var, not the key itself
    model_name:  "your-model-name"   # model string your endpoint expects
    energy_kwh:  0.001
    accuracy:    0.78
    max_complexity: LOW

  medium_model:
    endpoint:    "https://your-api.com/v1/chat/completions"
    api_key_env: "YOUR_API_KEY"
    model_name:  "your-medium-model"
    energy_kwh:  0.003
    accuracy:    0.90
    max_complexity: MEDIUM

  large_model:
    endpoint:    "http://localhost:11434/v1/chat/completions"  # local Ollama
    api_key_env: ""                  # no key for local models
    model_name:  "llama3.2"
    energy_kwh:  0.010
    accuracy:    0.97
    max_complexity: HIGH
```

### 3. Set environment variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Start the server
```bash
python server.py
```

---

## API Reference

### POST /neuroroute/query

Route and execute a query.

**Request:**
```json
{
  "selected_text": "Explain the transformer attention mechanism",
  "task": "explain"
}
```

**Tasks:** `ask` | `explain` | `summarize` | `simplify` | `analyze` | `research`

**Response:**
```json
{
  "answer":           "Transformer attention works by...",
  "model_used":       "Medium LLM",
  "model_id":         "medium_model",
  "complexity":       "MEDIUM",
  "domain":           "technology",
  "task":             "explain",
  "energy_used":      "0.00300 kWh",
  "carbon":           "0.00120 kg",
  "water":            "0.00450 L",
  "latency":          "1.42s",
  "compute_mode":     "CPU",
  "gpu_usage_pct":    0,
  "shift_score":      0,
  "backend_used":     "cloud"
}
```

**compute_mode values:**
| Value | Meaning |
|---|---|
| `CPU` | Small model or cloud API — no local GPU used |
| `GPU` | Medium model running locally — GPU active |
| `GPU_SHIFT` | Large model running locally — full CPU→GPU shift |

---

### GET /neuroroute/stats
Cumulative green statistics across all queries.

### GET /neuroroute/queries?limit=50
Recent query log with model, complexity, and environmental data.

### GET /neuroroute/hardware
Live CPU/RAM/GPU usage + compute_mode.

### GET /neuroroute/datasets
Info about the auto-generated ML training datasets.

### GET /health
Health check.

---

## Compatible Endpoints

NeuroRoute works with any server that accepts `POST /v1/chat/completions`:

| Provider | Endpoint |
|---|---|
| **Groq** | `https://api.groq.com/openai/v1/chat/completions` |
| **OpenAI** | `https://api.openai.com/v1/chat/completions` |
| **Together AI** | `https://api.together.xyz/v1/chat/completions` |
| **Ollama (local)** | `http://localhost:11434/v1/chat/completions` |
| **vLLM (local)** | `http://localhost:8000/v1/chat/completions` |
| **LM Studio** | `http://localhost:1234/v1/chat/completions` |
| **Azure OpenAI** | `https://<resource>.openai.azure.com/openai/deployments/<deploy>/chat/completions?api-version=2024-02-01` |
| **Your own server** | Any URL that speaks OpenAI-format |

---

## Real CPU→GPU Shift

To get a genuine CPU→GPU shift on your hardware:

1. Install Ollama: https://ollama.com/download
2. Pull a model: `ollama pull llama3.2`
3. Point `large_model` in `models.yaml` at:
   ```yaml
   endpoint: "http://localhost:11434/v1/chat/completions"
   api_key_env: ""
   model_name: "llama3.2"
   ```
4. Restart NeuroRoute
5. Send a HIGH complexity query — Ollama runs on your GPU, `nvidia-smi` will show real utilisation, and the dashboard will show `compute_mode: GPU_SHIFT`

---

## What NeuroRoute generates automatically

Every query auto-writes to:

| File | Purpose |
|---|---|
| `backend/logs/queries.json` | Full query log |
| `backend/datasets/routing_classifier_dataset.csv` | ML training data for complexity classifier |
| `backend/datasets/environmental_impact_dataset.csv` | ML training data for impact predictor |
| `backend/datasets/full_neuroroute_dataset.csv` | Complete feature set |

---

## Files you own (do not modify)
```
query_analyzer.py   ← complexity detection (your IP)
routing_engine.py   ← green scoring algorithm (your IP)
logger.py           ← environmental tracking (your IP)
```

## Files companies configure
```
models.yaml         ← plug in any models here
.env                ← API keys
```

## Files companies can extend
```
server.py           ← add auth, rate limiting, custom endpoints
model_executor.py   ← add custom adapters if needed
```
