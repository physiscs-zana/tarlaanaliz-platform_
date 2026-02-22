// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-019: Expert portal review kuyruğu; SLA 4 saat.
// KR-081: Contract-first tip tanımları.
'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import { listPendingReviews } from '../services/expertReviewService';
import type { PendingReviewItem } from '../services/expertReviewService';

export interface UseExpertReviewsResult {
  readonly reviews: readonly PendingReviewItem[];
  readonly isLoading: boolean;
  readonly error: string | null;
  readonly refetch: () => Promise<void>;
}

export function useExpertReviews(token: string | null): UseExpertReviewsResult {
  const [reviews, setReviews] = useState<readonly PendingReviewItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReviews = useCallback(async () => {
    if (!token) {
      setReviews([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await listPendingReviews(token);
      setReviews(response.items);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : 'Reviews load failed');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void fetchReviews();
  }, [fetchReviews]);

  return useMemo(
    () => ({ reviews, isLoading, error, refetch: fetchReviews }),
    [reviews, isLoading, error, fetchReviews]
  );
}
