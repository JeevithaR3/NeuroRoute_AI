import DocPage from "@/components/DocPage";

const fields = [
  { name: "query_summary", desc: "Brief summary of the user query" },
  { name: "query_complexity", desc: "Low, Medium, or High" },
  { name: "model_selected", desc: "Which AI model was used" },
  { name: "response_confidence", desc: "Confidence score of the response" },
  { name: "energy_usage", desc: "Energy consumed in kWh" },
  { name: "carbon_estimate", desc: "Estimated CO₂ emissions in kg" },
  { name: "water_estimate", desc: "Estimated water usage in liters" },
];

const DatasetGeneration = () => (
  <DocPage title="Dataset Generation" subtitle="NeuroRoute logs query metadata to generate datasets for AI research.">
    <div className="space-y-8 max-w-2xl">
      <div>
        <h3 className="text-lg font-semibold mb-4">Logged Data Fields</h3>
        <div className="space-y-3">
          {fields.map((f) => (
            <div key={f.name} className="glass rounded-xl p-4 flex items-center gap-4">
              <code className="text-primary font-mono text-sm shrink-0">{f.name}</code>
              <span className="text-sm text-muted-foreground">{f.desc}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="glass rounded-xl p-6">
        <p className="text-sm text-muted-foreground">
          These datasets can be used to train better AI routing algorithms, optimize model selection, and improve sustainability predictions over time.
        </p>
      </div>
    </div>
  </DocPage>
);

export default DatasetGeneration;
