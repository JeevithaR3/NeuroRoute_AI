# ⬡ NeuroRoute — Green AI Router

**An intelligent, environment-aware AI orchestration system that routes queries to the most energy-efficient model.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1 — Chrome Extension (User Interaction)          │
│  Detects text selection → shows popup → sends query     │
└────────────────────────┬────────────────────────────────┘
                         │ POST /neuroroute/query
┌────────────────────────▼────────────────────────────────┐
│  Layer 2 — NeuroRoute Middleware (Green AI Router)      │
│  Analyze → Route → Execute → Calculate impact → Respond │
└────────────────────────┬────────────────────────────────┘
                         │ Log events
┌────────────────────────▼────────────────────────────────┐
│  Layer 3 — Backend Monitoring & Dataset System          │
│  CLI dashboard, web dashboard, dataset builder          │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
neuroroute/
│
├── chrome-extension/           # Layer 1
│   ├── manifest.json           # Extension config
│   ├── content.js              # Text selection + popup logic
│   ├── content.css             # Popup styles
│   ├── background.js           # Service worker + stats
│   ├── popup/
│   │   ├── popup.html          # Extension popup UI
│   │   └── popup.js            # Stats + server check
│   └── icons/                  # Extension icons
│
├── middleware/                 # Layer 2
│   ├── server.py               # Flask API server (port 3000)
│   ├── query_analyzer.py       # Task/complexity/domain detection
│   ├── routing_engine.py       # Green routing algorithm
│   ├── model_executor.py       # Model simulation/execution
│   ├── logger.py               # Query event logging
│   └── models.yaml             # Model registry config
│
├── backend/                    # Layer 3
│   ├── dashboard.py            # CLI monitoring dashboard
│   ├── dataset_builder.py      # ML dataset generator
│   ├── web_dashboard.html      # Web monitoring UI
│   ├── logs/                   # Auto-created: query logs
│   └── datasets/               # Auto-created: ML datasets
│
├── start_server.sh             # Start middleware
├── dashboard.sh                # Open CLI dashboard
└── README.md
```

---

## Quick Start

### Step 1 — Start the Middleware Server (Layer 2)

```bash
chmod +x start_server.sh
./start_server.sh
```

Or manually:
```bash
cd middleware
python3 server.py
```

Server runs at: **http://localhost:3000**

---

### Step 2 — Install Chrome Extension (Layer 1)

1. Open Chrome → go to `chrome://extensions/`
2. Enable **Developer Mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `chrome-extension/` folder
5. The ⬡ NeuroRoute icon appears in your toolbar

**Usage:**
- Browse any webpage
- **Highlight any text**
- A floating popup appears → choose Ask / Explain / Summarize / Simplify
- View the AI answer + environmental metrics inline

---

### Step 3 — Monitor (Layer 3)

**Web Dashboard** — open in browser:
```
backend/web_dashboard.html
```

**CLI Dashboard:**
```bash
./dashboard.sh              # Stats + recent queries
./dashboard.sh --watch      # Live auto-refresh
./dashboard.sh --stats      # Stats only
./dashboard.sh --queries    # Query table only
./dashboard.sh --dataset    # Build ML datasets
```

---

## API Reference

### POST `/neuroroute/query`
Process a query through the green routing pipeline.

**Request:**
```json
{
  "selected_text": "Quantum entanglement connects two particles...",
  "task": "summarize",
  "page_url": "https://example.com",
  "page_title": "Physics Article",
  "domain": "example.com",
  "timestamp": "2026-03-13T12:40:00"
}
```

**Response:**
```json
{
  "answer": "Quantum entanglement occurs when...",
  "model_used": "Medium LLM",
  "model_id": "medium_model",
  "complexity": "MEDIUM",
  "domain": "science",
  "task": "summarize",
  "energy_used": "0.00300 kWh",
  "carbon": "0.00120 kg",
  "water": "0.00450 L",
  "latency": "1.02s",
  "model_comparison": [...]
}
```

### GET `/neuroroute/stats`
Returns aggregated system statistics.

### GET `/neuroroute/queries?limit=50`
Returns recent query log.

### POST `/neuroroute/feedback`
Submit user feedback on a response.

### GET `/health`
Health check.

---

## Green Routing Algorithm

NeuroRoute scores each candidate model using:

```
Score = (0.50 × Accuracy)
      - (0.25 × NormalizedCarbon)
      - (0.15 × NormalizedWater)
      - (0.10 × NormalizedLatency)
```

The model with the **highest green score** wins — balancing response quality against environmental impact.

| Model        | Accuracy | Energy    | CO₂       | Water     |
|--------------|----------|-----------|-----------|-----------|
| Small LLM    | 78%      | 0.001 kWh | 0.0004 kg | 0.0015 L  |
| Medium LLM   | 90%      | 0.003 kWh | 0.0012 kg | 0.0045 L  |
| Large LLM    | 97%      | 0.010 kWh | 0.0040 kg | 0.0150 L  |

---

## Connecting Real AI Models

In `middleware/model_executor.py`, replace the simulation methods with real API calls:

```python
# Small model → local Ollama (mistral:7b)
import requests
def _run_small(text, task):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral:7b", "prompt": f"{task}: {text}", "stream": False
    })
    return res.json()["response"]

# Medium model → Anthropic Claude Haiku
import anthropic
def _run_medium(text, task):
    client = anthropic.Anthropic(api_key="YOUR_KEY")
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": f"{task}: {text}"}]
    )
    return msg.content[0].text

# Large model → Anthropic Claude Sonnet
def _run_large(text, task):
    client = anthropic.Anthropic(api_key="YOUR_KEY")
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"{task}: {text}"}]
    )
    return msg.content[0].text
```

---

## Dataset Output

Running `./dashboard.sh --dataset` generates:

```
backend/datasets/
├── routing_classifier_dataset.csv    # Train complexity classifier
├── environmental_impact_dataset.csv  # Train impact estimator
├── full_neuroroute_dataset.csv       # Complete feature set
├── full_neuroroute_dataset.json      # JSON version
└── system_stats_snapshot.json        # Point-in-time stats
```

---

## Requirements

- Python 3.8+
- Flask (`pip install flask`)
- PyYAML (`pip install pyyaml`)
- Chrome browser (for extension)
- psutil (optional, for RAM detection)

---

## Built For

NeuroRoute is designed to demonstrate **Green AI** — the idea that intelligent model routing can dramatically reduce the environmental footprint of AI inference without sacrificing quality.

> "Not every question needs a large model. NeuroRoute finds the smallest model that gets the job done."
