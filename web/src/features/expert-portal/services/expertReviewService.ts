// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-019: Expert portal review akışı; güven eşiği aşılmayan sonuçlar kuyruğa girer.
// KR-081: Contract-first tip tanımları.

import { http } from '@/lib/http';

export interface PendingReviewItem {
  readonly reviewId: string;
  readonly missionId: string;
  readonly fieldName: string;
  readonly priority: 'low' | 'medium' | 'high';
  readonly status: 'queued' | 'in_review' | 'completed';
  readonly createdAtIso: string;
}

export interface PendingReviewsResponse {
  readonly items: readonly PendingReviewItem[];
}

export interface ReviewDetail {
  readonly reviewId: string;
  readonly missionId: string;
  readonly notes: string;
  readonly confidenceScore: number;
  readonly ndviData: Record<string, unknown> | null;
  readonly ndreData: Record<string, unknown> | null;
  readonly createdAtIso: string;
  readonly updatedAtIso: string;
}

export interface ExpertReviewPayload {
  readonly confidenceAdjustment: number;
  readonly reviewNotes: string;
  readonly approved: boolean;
}

export async function listPendingReviews(token: string): Promise<PendingReviewsResponse> {
  return http<PendingReviewsResponse>('/expert_portal/reviews', {
    method: 'GET',
    token,
  });
}

export async function getReviewDetail(reviewId: string, token: string): Promise<ReviewDetail> {
  return http<ReviewDetail>(`/expert_portal/reviews/${reviewId}`, {
    method: 'GET',
    token,
  });
}

export async function submitReview(
  reviewId: string,
  payload: ExpertReviewPayload,
  token: string
): Promise<void> {
  await http<void>(`/expert_portal/reviews/${reviewId}/submit`, {
    method: 'POST',
    body: JSON.stringify(payload),
    token,
  });
}
