import { Button } from "@/components/ui/button";
import SectionWrapper from "@/components/SectionWrapper";
import { useAuth } from "@/contexts/AuthContext";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  Zap, Cpu, Leaf, Globe, TrendingUp, Database,
  ArrowRight, Download, Github, Monitor, Terminal, BarChart3, Search, LogIn, UserPlus
} from "lucide-react";

const features = [
  { icon: Zap, title: "Smart Query Routing", desc: "Automatically routes queries to the most efficient AI model based on complexity analysis." },
  { icon: Cpu, title: "Hardware-Aware Selection", desc: "Detects available CPU, GPU, and memory to select models that match your infrastructure." },
  { icon: Leaf, title: "Carbon & Water Tracking", desc: "Monitors energy usage, CO₂ emissions, and water consumption per query." },
  { icon: Globe, title: "Browser AI Anywhere", desc: "Chrome extension lets you select text on any webpage and get instant AI responses." },
  { icon: TrendingUp, title: "Confidence Escalation", desc: "Automatically retries with a larger model if the initial response confidence is low." },
  { icon: Database, title: "Dataset Generation", desc: "Logs query metadata to generate datasets for training better routing algorithms." },
];

const Index = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <SectionWrapper className="pt-28 pb-16">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full bg-accent px-4 py-1.5 text-sm font-medium text-accent-foreground"
          >
            <Leaf className="h-4 w-4" /> Sustainable AI Infrastructure
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-5xl md:text-7xl font-bold leading-tight"
          >
            <span className="text-gradient">NeuroRoute</span>
            <br />
            Intelligent Green AI Router
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto"
          >
            A smart middleware that dynamically routes AI queries across multiple models for optimal performance, cost efficiency, and environmental sustainability.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="flex flex-wrap justify-center gap-4"
          >
            {user ? (
              <>
               <Button
  size="lg"
  className="bg-gradient-primary text-primary-foreground shadow-glow"
  asChild
>
  <a href="/neuroroute-extension.zip" download>
    <Download className="mr-2 h-4 w-4" /> Download Extension
  </a>
</Button>
                <Button
  size="lg"
  className="bg-gradient-primary text-primary-foreground shadow-glow"
  asChild
>
  <a href="/neuroroute-middleware-extension.zip" download>
    <Download className="mr-2 h-4 w-4" /> Download Middleware
  </a>
</Button>
                {/* <Button size="lg" variant="ghost" asChild>
                  <Link to="/architecture"><ArrowRight className="mr-2 h-4 w-4" /> View Documentation</Link>
                </Button> */}
              </>
            ) : (
              <>
                <Button size="lg" className="bg-gradient-primary text-primary-foreground shadow-glow" asChild>
                  <Link to="/signup"><UserPlus className="mr-2 h-4 w-4" /> Sign Up</Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link to="/login"><LogIn className="mr-2 h-4 w-4" /> Login</Link>
                </Button>
              </>
            )}
          </motion.div>
        </div>

        {/* Flow Diagram */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.7 }}
          className="mt-16 max-w-3xl mx-auto"
        >
          <div className="glass rounded-2xl p-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center">
              {[
                { icon: Globe, label: "User" },
                { icon: Monitor, label: "Browser Extension" },
                { icon: Zap, label: "NeuroRoute Middleware" },
                { icon: Cpu, label: "AI Models" },
                { icon: BarChart3, label: "Response" },
              ].map((step, i) => (
                <div key={step.label} className="flex items-center gap-3">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-14 h-14 rounded-xl bg-accent flex items-center justify-center">
                      <step.icon className="h-6 w-6 text-white" />
                    </div>
                    <span className="text-xs font-medium">{step.label}</span>
                  </div>
                  {i < 4 && <ArrowRight className="h-4 w-4 text-muted-foreground hidden md:block" />}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </SectionWrapper>

      {/* Problem */}
      <SectionWrapper className="bg-muted/50">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold">The Problem</h2>
          <p className="text-muted-foreground text-lg">
            Most applications send all queries to a single large language model, regardless of complexity.
          </p>
          <div className="grid sm:grid-cols-2 gap-4 text-left">
            {[
              "Unnecessary GPU usage for simple queries",
              "High latency from overloaded models",
              "Higher infrastructure costs",
              "Environmental impact from energy-intensive inference",
            ].map((item) => (
              <div key={item} className="glass rounded-xl p-5 flex items-start gap-3">
                <div className="h-2 w-2 rounded-full bg-destructive mt-2 shrink-0" />
                <span className="text-sm">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* Solution */}
      <SectionWrapper>
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold">The Solution</h2>
          <p className="text-muted-foreground text-lg">
            NeuroRoute introduces an intelligent middleware layer that optimizes every AI query.
          </p>
          <div className="grid sm:grid-cols-2 gap-4 text-left">
            {[
              "Analyzes query complexity in real-time",
              "Detects hardware availability",
              "Estimates environmental impact",
              "Routes to the optimal model automatically",
            ].map((item) => (
              <div key={item} className="glass rounded-xl p-5 flex items-start gap-3">
                <div className="h-2 w-2 rounded-full bg-primary mt-2 shrink-0" />
                <span className="text-sm">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* Features */}
      <SectionWrapper className="bg-muted/50">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">Features</h2>
          <p className="mt-3 text-muted-foreground">Everything you need for intelligent AI routing.</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {features.map((f) => (
            <div key={f.title} className="glass rounded-xl p-6 space-y-3 hover:shadow-glow transition-shadow duration-300">
              <div className="w-12 h-12 rounded-lg bg-accent flex items-center justify-center">
                <f.icon className="h-6 w-6 text-white" />
              </div>
              <h3 className="font-semibold text-lg">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </SectionWrapper>

      {/* Demo Placeholders */}
      <SectionWrapper>
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">See It In Action</h2>
          <p className="mt-3 text-muted-foreground">Screenshots from the NeuroRoute ecosystem.</p>
        </div>
        <div className="grid sm:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {[
            { icon: Monitor, label: "Browser Extension Popup" },
            { icon: Terminal, label: "Middleware CLI Dashboard" },
            { icon: Search, label: "Model Routing Logs" },
            { icon: BarChart3, label: "Query Analysis Results" },
          ].map((d) => (
            <div key={d.label} className="glass rounded-xl aspect-video flex flex-col items-center justify-center gap-3">
              <d.icon className="h-10 w-10 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">{d.label}</span>
              <span className="text-xs text-muted-foreground/60">Screenshot placeholder</span>
            </div>
          ))}
        </div>
      </SectionWrapper>

      {/* Download / CTA */}
      <SectionWrapper className="bg-muted/50">
        <div className="max-w-2xl mx-auto text-center space-y-8">
          <h2 className="text-3xl md:text-4xl font-bold">Get Started</h2>
          <p className="text-muted-foreground">
            {user
              ? "Download NeuroRoute and start routing smarter today."
              : "Create an account to access downloads, documentation, and all features."}
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            {user ? (
              <>
                <Button size="lg" className="bg-gradient-primary text-primary-foreground shadow-glow">
                  <Download className="mr-2 h-4 w-4" /> Browser Extension
                </Button>
                <Button size="lg" variant="outline">
                  <Terminal className="mr-2 h-4 w-4" /> Middleware
                </Button>
                {/* GitHub Button with link */}
                <Button size="lg" variant="outline" asChild>
                  <a
                    href="https://github.com/JeevithaR3/NeuroRoute_AI"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Github className="mr-2 h-4 w-4" /> GitHub
                  </a>
                </Button>
              </>
            ) : (
              <>
                <Button size="lg" className="bg-gradient-primary text-primary-foreground shadow-glow" asChild>
                  <Link to="/signup"><UserPlus className="mr-2 h-4 w-4" /> Sign Up Free</Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link to="/login"><LogIn className="mr-2 h-4 w-4" /> Login</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </SectionWrapper>

      {/* Why Unique */}
      <SectionWrapper>
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">Why NeuroRoute?</h2>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {[
            "Environment-aware AI routing",
            "Plug-and-play model architecture",
            "Browser AI assistance on any webpage",
            "Dynamic model switching",
            "Built-in sustainability metrics",
            "Dataset generation for future AI optimization",
          ].map((item) => (
            <div key={item} className="glass rounded-xl p-5 flex items-start gap-3">
              <Zap className="h-5 w-5 text-primary mt-0.5 shrink-0" />
              <span className="font-medium text-sm">{item}</span>
            </div>
          ))}
        </div>
      </SectionWrapper>
    </div>
  );
};

export default Index;