import DocPage from "@/components/DocPage";
import CodeBlock from "@/components/CodeBlock";

const ModelConfig = () => (
  <DocPage title="Model Configuration" subtitle="Plug in new AI models easily using a simple YAML configuration file.">
    <div className="space-y-8 max-w-2xl">
      <div>
        <h3 className="text-lg font-semibold mb-3">Configuration File</h3>
        <CodeBlock title="model_registry.yaml">{`# NeuroRoute Model Registry
# Defines available AI models, their capabilities, and environmental footprint

models:
  small_model:
    name: "Small LLM"
    description: "Fast model for simple factual queries and math"
    capabilities:
      - basic_qa
      - math
      - definitions
      - factual
    accuracy: 0.78
    latency_seconds: 0.3
    energy_kwh: 0.001
    carbon_per_kwh: 0.4      # kg CO2 per kWh (grid intensity)
    water_per_kwh: 1.5       # liters per kWh (cooling factor)
    max_complexity: LOW

  medium_model:
    name: "Medium LLM"
    description: "Balanced model for summarization, explanation, and moderate reasoning"
    capabilities:
      - summarization
      - explanation
      - simplification
      - analysis
      - basic_qa
    accuracy: 0.90
    latency_seconds: 1.5
    energy_kwh: 0.003
    carbon_per_kwh: 0.4
    water_per_kwh: 1.5
    max_complexity: MEDIUM

  large_model:
    name: "Large LLM"
    description: "Powerful model for complex reasoning, deep analysis, research tasks"
    capabilities:
      - deep_reasoning
      - research
      - complex_analysis
      - creative
      - coding
      - summarization
      - explanation
    accuracy: 0.97
    latency_seconds: 4.0
    energy_kwh: 0.010
    carbon_per_kwh: 0.4
    water_per_kwh: 1.5
    max_complexity: HIGH

# Routing weights for green scoring
routing_weights:
  accuracy: 0.5
  carbon: 0.25
  water: 0.15
  latency: 0.10
`}</CodeBlock>
      </div>
      <div className="glass rounded-xl p-6 space-y-3">
        <h3 className="font-semibold">Plug-and-Play Integration</h3>
        <p className="text-sm text-muted-foreground">
          Add or remove models by editing the YAML file — no code changes required. NeuroRoute automatically discovers and integrates new models on server restart.
        </p>
      </div>
    </div>
  </DocPage>
);

export default ModelConfig;
