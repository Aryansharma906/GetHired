"use client";

import { LazyMotion, domAnimation, m, MotionConfig } from "framer-motion";
import type { ReactNode } from "react";

/** One small motion boundary. Honors the OS preference and never delays controls. */
export function WorkspaceMotion({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <MotionConfig reducedMotion="user">
      <LazyMotion features={domAnimation} strict>
        <m.div className={className} initial={false} animate={{ opacity: 1 }}>
          {children}
        </m.div>
      </LazyMotion>
    </MotionConfig>
  );
}

export function Reveal({ children, className, delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  return (
    <m.div
      className={className}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </m.div>
  );
}
