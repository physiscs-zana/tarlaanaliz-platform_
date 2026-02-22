// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-027: Sezonluk abonelik otomasyonu; haftalık planlama token'ları.
// KR-081: Contract-first tip tanımları.

import { http } from '@/lib/http';

export interface SubscriptionItem {
  readonly subscriptionId: string;
  readonly userId: string;
  readonly cropType: string;
  readonly seasonStart: string;
  readonly seasonEnd: string;
  readonly isActive: boolean;
  readonly createdAtIso: string;
}

export interface SubscriptionListResponse {
  readonly items: readonly SubscriptionItem[];
}

export interface SubscriptionPayload {
  readonly cropType: string;
  readonly seasonStart: string;
  readonly seasonEnd: string;
}

export async function listSubscriptions(token: string): Promise<SubscriptionListResponse> {
  return http<SubscriptionListResponse>('/subscriptions', {
    method: 'GET',
    token,
  });
}

export async function getSubscription(
  subscriptionId: string,
  token: string
): Promise<SubscriptionItem> {
  return http<SubscriptionItem>(`/subscriptions/${subscriptionId}`, {
    method: 'GET',
    token,
  });
}

export async function createSubscription(
  payload: SubscriptionPayload,
  token: string
): Promise<SubscriptionItem> {
  return http<SubscriptionItem>('/subscriptions', {
    method: 'POST',
    body: JSON.stringify(payload),
    token,
  });
}
