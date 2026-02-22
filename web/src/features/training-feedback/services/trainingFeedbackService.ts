// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-081: Contract-first tip tanımları.

import { http } from '@/lib/http';

export type FeedbackType = 'ndvi_incorrect' | 'ndre_incorrect' | 'confidence_wrong' | 'other';

export interface FeedbackPayload {
  readonly analysisJobId: string;
  readonly isCorrect: boolean;
  readonly feedbackType: FeedbackType;
  readonly notes?: string;
}

export interface FeedbackResponse {
  readonly feedbackId: string;
  readonly analysisJobId: string;
  readonly createdAtIso: string;
}

export async function submitFeedback(
  payload: FeedbackPayload,
  token: string
): Promise<FeedbackResponse> {
  return http<FeedbackResponse>('/training_feedback', {
    method: 'POST',
    body: JSON.stringify(payload),
    token,
  });
}
