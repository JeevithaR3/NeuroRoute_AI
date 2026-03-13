const CodeBlock = ({ children, title }: { children: string; title?: string }) => (
  <div className="rounded-xl overflow-hidden border border-border">
    {title && (
      <div className="bg-muted px-4 py-2 text-xs font-mono text-muted-foreground border-b border-border">
        {title}
      </div>
    )}
    <pre className="bg-card p-4 overflow-x-auto text-sm font-mono text-foreground">
      <code>{children}</code>
    </pre>
  </div>
);

export default CodeBlock;
