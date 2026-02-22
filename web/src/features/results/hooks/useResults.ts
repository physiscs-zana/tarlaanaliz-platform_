// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-071: AI çıktıları yalnızca NDVI/NDRE veri gösterimi için kullanılır.
'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import { listMissionResults } from '../services/resultService';
import type { ResultListItem } from '../services/resultService';

export interface UseResultsResult {
  readonly results: readonly ResultListItem[];
  readonly isLoading: boolean;
  readonly error: string | null;
  readonly refetch: () => Promise<void>;
}

export function useResults(missionId: string | null, token: string | null): UseResultsResult {
  const [results, setResults] = useState<readonly ResultListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = useCallback(async () => {
    if (!missionId || !token) {
      setResults([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await listMissionResults(missionId, token);
      setResults(response.items);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : 'Results load failed');
    } finally {
      setIsLoading(false);
    }
  }, [missionId, token]);

  useEffect(() => {
    void fetchResults();
  }, [fetchResults]);

  return useMemo(
    () => ({ results, isLoading, error, refetch: fetchResults }),
    [results, isLoading, error, fetchResults]
  );
}
