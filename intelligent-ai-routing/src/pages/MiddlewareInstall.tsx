import DocPage from "@/components/DocPage";
import CodeBlock from "@/components/CodeBlock";

const MiddlewareInstall = () => (
  <DocPage title="Middleware Installation" subtitle="Set up the NeuroRoute middleware server on your machine.">
    <div className="space-y-8 max-w-2xl">
      <div>
        <h3 className="text-lg font-semibold mb-3">1. Clone & Install</h3>
        <CodeBlock title="Terminal">{`git clone https://github.com/neuroroute
cd neuroroute
pip install -r requirements.txt`}</CodeBlock>
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-3">2. Run the Server</h3>
        <CodeBlock title="Terminal">{`python server.py`}</CodeBlock>
      </div>
      <div className="glass rounded-xl p-6">
        <p className="text-sm text-muted-foreground">
          The middleware exposes REST APIs that the browser extension connects to. By default, the server runs on <code className="text-primary font-mono">http://localhost:5000</code>.
        </p>
      </div>
    </div>
  </DocPage>
);

export default MiddlewareInstall;
