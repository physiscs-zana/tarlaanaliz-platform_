/* BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated. */
/* KR-081: Queue contract tipleri ile fetch edilir. */
/* KR-071: corr_id/request_id izleri request metadata olarak taşınır. */
'use client';

import { useCallback, useEffect, useMemo, useState } from "react";

import { listPendingReviews } from "../services/expertReviewService";
import type { ExpertQueueItem, ExpertQueueStats } from "../types";

export interface UseExpertQueueResult {
  readonly items: readonly ExpertQueueItem[];
  readonly stats: ExpertQueueStats;
  readonly isLoading: boolean;
  readonly error: string | null;
  readonly refetch: () => Promise<void>;
}

function computeStats(items: readonly ExpertQueueItem[]): ExpertQueueStats {
  return {
    total: items.length,
    queued: items.filter((item) => item.status === "queued").length,
    inReview: items.filter((item) => item.status === "in_review").length,
    completed: items.filter((item) => item.status === "completed").length,
  };
}

export function useExpertQueue(token: string | null): UseExpertQueueResult {
  const [items, setItems] = useState<readonly ExpertQueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQueue = useCallback(async () => {
    if (!token) {
      setItems([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await listPendingReviews(token);
      setItems(response.items as readonly ExpertQueueItem[]);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "Queue load failed");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void fetchQueue();
  }, [fetchQueue]);

  return useMemo(
    () => ({
      items,
      stats: computeStats(items),
      isLoading,
      error,
      refetch: fetchQueue,
    }),
    [error, fetchQueue, isLoading, items]
  );
}
