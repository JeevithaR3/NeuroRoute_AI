import { motion } from "framer-motion";
import { ReactNode } from "react";

const SectionWrapper = ({ children, className = "", id }: { children: ReactNode; className?: string; id?: string }) => (
  <motion.section
    id={id}
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-50px" }}
    transition={{ duration: 0.6, ease: "easeOut" }}
    className={`py-20 ${className}`}
  >
    <div className="container">{children}</div>
  </motion.section>
);

export default SectionWrapper;
