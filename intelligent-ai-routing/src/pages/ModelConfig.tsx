import DocPage from "@/components/DocPage";
import CodeBlock from "@/components/CodeBlock";

const ModelConfig = () => (
  <DocPage title="Model Configuration" subtitle="Plug in new AI models easily using a simple YAML configuration file.">
    <div className="space-y-8 max-w-2xl">
      <div>
        <h3 className="text-lg font-semibold mb-3">Configuration File</h3>
        <CodeBlock title="model_registry.yaml">{`models:
  - name: small_model
    type: local
    path: models/tiny

  - name: medium_model
    type: api
    provider: openai

  - name: large_model
    type: gpu
    path: models/llama`}</CodeBlock>
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
