import { Zap } from "lucide-react";

const Footer = () => (
  <footer className="border-t border-border bg-card/50 py-12">
    <div className="container">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-primary" />
          <span className="font-bold text-gradient">NeuroRoute</span>
        </div>
        <p className="text-sm text-muted-foreground">
          © {new Date().getFullYear()} NeuroRoute. Intelligent Green AI Routing.
        </p>
      </div>
    </div>
  </footer>
);

export default Footer;
