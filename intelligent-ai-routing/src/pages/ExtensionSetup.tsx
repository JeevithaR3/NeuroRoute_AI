import DocPage from "@/components/DocPage";
import { Download, Settings, MousePointer, MessageSquare } from "lucide-react";

const steps = [
  { icon: Download, title: "Step 1: Download", desc: "Download the NeuroRoute browser extension package." },
  { icon: Settings, title: "Step 2: Install", desc: "Open Chrome → Extensions → Enable Developer Mode → Load Unpacked → Select the extension folder." },
  { icon: MousePointer, title: "Step 3: Select Text", desc: "Select text on any webpage and click the NeuroRoute popup icon." },
  { icon: MessageSquare, title: "Step 4: Choose Action", desc: "Choose an option: Ask, Explain, Summarize, or Simplify. The query is sent to the middleware for processing." },
];

const ExtensionSetup = () => (
  <DocPage title="Browser Extension Setup" subtitle="Install and use the NeuroRoute Chrome extension in minutes.">
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

export default ExtensionSetup;
