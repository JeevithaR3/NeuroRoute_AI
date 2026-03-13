import { ReactNode } from "react";
import SectionWrapper from "./SectionWrapper";

const DocPage = ({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) => (
  <div className="min-h-screen">
    <SectionWrapper className="pt-28 pb-10">
      <h1 className="text-4xl md:text-5xl font-bold mb-4">{title}</h1>
      <p className="text-lg text-muted-foreground max-w-2xl">{subtitle}</p>
    </SectionWrapper>
    <div className="container pb-20 space-y-12">{children}</div>
  </div>
);

export default DocPage;
