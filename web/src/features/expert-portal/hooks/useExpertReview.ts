/* BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated. */
/* KR-081: Review detail contract-first tip ile yüklenir. */
/* KR-071: corr_id/request_id izleri request metadata olarak taşınır. */
'use client';

import { useCallback, useEffect, useState } from "react";

import { getReviewDetail } from "../services/expertReviewService";
import type { ExpertReviewDetail } from "../types";

export interface UseExpertReviewResult {
  readonly review: ExpertReviewDetail | null;
  readonly isLoading: boolean;
  readonly error: string | null;
  readonly refetch: () => Promise<void>;
}

export function useExpertReview(reviewId: string, token: string | null): UseExpertReviewResult {
  const [review, setReview] = useState<ExpertReviewDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReview = useCallback(async () => {
    if (!reviewId || !token) {
      setReview(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const detail = await getReviewDetail(reviewId, token);
      setReview(detail as ExpertReviewDetail);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "Review load failed");
    } finally {
      setIsLoading(false);
    }
  }, [reviewId, token]);

  useEffect(() => {
    void fetchReview();
  }, [fetchReview]);

  return {
    review,
    isLoading,
    error,
    refetch: fetchReview,
  };
}
