import DocPage from "@/components/DocPage";
import CodeBlock from "@/components/CodeBlock";
import { Leaf, Droplets, Zap } from "lucide-react";

const metrics = [
  { icon: Zap, label: "Energy Consumption", unit: "kWh" },
  { icon: Leaf, label: "Carbon Emissions", unit: "kg CO₂" },
  { icon: Droplets, label: "Water Usage", unit: "Liters" },
];

const EnvironmentalImpact = () => (
  <DocPage title="Environmental Impact" subtitle="How NeuroRoute estimates and tracks sustainability metrics.">
    <div className="space-y-8 max-w-2xl">
      <div className="grid sm:grid-cols-3 gap-4">
        {metrics.map((m) => (
          <div key={m.label} className="glass rounded-xl p-5 text-center space-y-2">
            <m.icon className="h-8 w-8 text-primary mx-auto" />
            <h3 className="font-semibold text-sm">{m.label}</h3>
            <p className="text-xs text-muted-foreground">{m.unit}</p>
          </div>
        ))}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-3">Example Output</h3>
        <CodeBlock title="Query Response Metrics">{`Model Used:      Medium Model
Energy Used:     0.003 kWh
Carbon Emission: 0.0012 kg CO₂
Water Usage:     0.0045 L`}</CodeBlock>
      </div>

      <div className="glass rounded-xl p-6">
        <p className="text-sm text-muted-foreground">
          By tracking these metrics per query, NeuroRoute enables organizations to build environmentally aware AI infrastructure and reduce their carbon footprint.
        </p>
      </div>
    </div>
  </DocPage>
);

export default EnvironmentalImpact;
