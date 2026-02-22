// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// Merkezi erişilebilirlik bağlamı: prefers-reduced-motion medya sorgusu.
'use client';

import { createContext, useContext, useEffect, useMemo, useState } from 'react';

interface AccessibilityContextValue {
  /** True when the user has requested reduced motion via OS/browser preferences. */
  readonly prefersReducedMotion: boolean;
}

const AccessibilityContext = createContext<AccessibilityContextValue>({
  prefersReducedMotion: false,
});

export function useReducedMotion(): boolean {
  const context = useContext(AccessibilityContext);
  return context.prefersReducedMotion;
}

export function AccessibilityProvider({ children }: { children: React.ReactNode }) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mq.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  const value = useMemo<AccessibilityContextValue>(
    () => ({ prefersReducedMotion }),
    [prefersReducedMotion]
  );

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
}
