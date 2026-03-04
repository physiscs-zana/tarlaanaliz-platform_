// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
'use client';

import { useCallback, useMemo } from 'react';

export function useQueryState(key: string, initialValue = '') {
  const value = useMemo(() => {
    if (typeof window === 'undefined') return initialValue;
    const params = new URLSearchParams(window.location.search);
    return params.get(key) ?? initialValue;
  }, [initialValue, key]);

  const setValue = useCallback(
    (nextValue: string) => {
      if (typeof window === 'undefined') return;
      const url = new URL(window.location.href);
      if (!nextValue) {
        url.searchParams.delete(key);
      } else {
        url.searchParams.set(key, nextValue);
      }
      window.history.replaceState({}, '', url.toString());
    },
    [key]
  );

  return [value, setValue] as const;
}
