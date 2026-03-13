import DocPage from "@/components/DocPage";
import { Search, Cpu, Leaf, Zap, TrendingUp } from "lucide-react";

const steps = [
  { icon: Search, title: "Step 1 – Query Analysis", desc: "Determine query complexity: Low, Medium, or High based on token count, semantic depth, and task type." },
  { icon: Cpu, title: "Step 2 – Hardware Detection", desc: "Check available CPU, GPU, and memory resources to match model requirements." },
  { icon: Leaf, title: "Step 3 – Environmental Impact", desc: "Estimate energy usage, carbon emissions, and cooling water consumption for each candidate model." },
  { icon: Zap, title: "Step 4 – Model Selection", desc: "Choose the optimal AI model based on accuracy, latency, and sustainability metrics." },
  { icon: TrendingUp, title: "Step 5 – Confidence Escalation", desc: "If the response confidence is below threshold, automatically retry with a larger model." },
];

const QueryRouting = () => (
  <DocPage title="Query Routing Logic" subtitle="How NeuroRoute selects the optimal AI model for every query.">
    <div className="space-y-6 max-w-2xl">
      {steps.map((s, i) => (
        <div key={i} className="glass rounded-xl p-6 flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center shrink-0">
            <s.icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold">{s.title}</h3>
            <p className="text-sm text-muted-foreground mt-1">{s.desc}</p>
          </div>
        </div>
      ))}
    </div>
  </DocPage>
);

export default QueryRouting;
