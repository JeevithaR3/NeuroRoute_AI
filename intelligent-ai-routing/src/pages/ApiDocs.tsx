import DocPage from "@/components/DocPage";
import CodeBlock from "@/components/CodeBlock";

const ApiDocs = () => (
  <DocPage title="API Documentation" subtitle="REST API reference for the NeuroRoute middleware.">
    <div className="space-y-8 max-w-2xl">
      <div>
        <h3 className="text-lg font-semibold mb-1">POST /ask</h3>
        <p className="text-sm text-muted-foreground mb-4">Send a query to NeuroRoute for intelligent routing and response.</p>

        <h4 className="text-sm font-semibold mb-2">Request</h4>
        <CodeBlock title="POST /ask">{`{
  "query": "Explain this article"
}`}</CodeBlock>
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-2">Response</h4>
        <CodeBlock title="200 OK">{`{
  "answer": "...",
  "model": "medium_model",
  "energy": "0.003 kWh",
  "carbon": "0.0012 kg",
  "water": "0.0045 L"
}`}</CodeBlock>
      </div>

      <div className="glass rounded-xl p-6 space-y-3">
        <h4 className="font-semibold">Response Fields</h4>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li><code className="text-primary font-mono">answer</code> — The AI-generated response</li>
          <li><code className="text-primary font-mono">model</code> — Which model was selected</li>
          <li><code className="text-primary font-mono">energy</code> — Energy consumed</li>
          <li><code className="text-primary font-mono">carbon</code> — CO₂ emissions</li>
          <li><code className="text-primary font-mono">water</code> — Water usage for cooling</li>
        </ul>
      </div>
    </div>
  </DocPage>
);

export default ApiDocs;
