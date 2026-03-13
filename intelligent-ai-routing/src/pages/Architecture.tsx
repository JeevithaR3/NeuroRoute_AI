import DocPage from "@/components/DocPage";
import SectionWrapper from "@/components/SectionWrapper";
import { Globe, Zap, Database, ArrowRight } from "lucide-react";

const Architecture = () => (
  <DocPage title="Architecture" subtitle="NeuroRoute's 3-layer architecture for intelligent AI routing.">
    {/* Diagram */}
    <div className="glass rounded-2xl p-8">
      <div className="flex flex-col items-center gap-6">
        {[
          { icon: Globe, label: "Layer 1 – Browser Extension", desc: "Users select text on any webpage and click 'Ask NeuroRoute'. The extension sends the query to the middleware API." },
          { icon: Zap, label: "Layer 2 – NeuroRoute Middleware", desc: "Core orchestration: query complexity analysis, hardware detection, environmental impact estimation, model selection, confidence-based escalation." },
          { icon: Database, label: "Layer 3 – Backend Monitoring", desc: "Logs query summaries, selected model, confidence score, energy usage, carbon emissions, and water usage." },
        ].map((layer, i) => (
          <div key={layer.label} className="w-full max-w-xl space-y-2">
            {i > 0 && <ArrowRight className="h-5 w-5 text-primary mx-auto rotate-90 my-2" />}
            <div className="glass rounded-xl p-6 space-y-2">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center">
                  <layer.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-lg">{layer.label}</h3>
              </div>
              <p className="text-sm text-muted-foreground">{layer.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>

    <SectionWrapper className="!py-0">
      <h2 className="text-2xl font-bold mb-4">Data Flow</h2>
      <p className="text-muted-foreground">
        User selects text → Extension captures query → Middleware analyzes complexity → Selects optimal model → Returns response → Logs metrics for sustainability tracking.
      </p>
    </SectionWrapper>
  </DocPage>
);

export default Architecture;
