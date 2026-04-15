/**
 * components/ui/PageTransition.tsx
 * =================================
 * Wrapper con fade + slide suave al montar cada página.
 */

import type { ReactNode } from "react";
import { motion } from "framer-motion";

export function PageTransition({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.22, ease: "easeOut" }}
      className="h-full"
    >
      {children}
    </motion.div>
  );
}
