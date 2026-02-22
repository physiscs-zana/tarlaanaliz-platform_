// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-027: Sezonluk abonelik listesi çekimi.
'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import { listSubscriptions } from '../services/subscriptionService';
import type { SubscriptionItem } from '../services/subscriptionService';

export interface UseSubscriptionsResult {
  readonly subscriptions: readonly SubscriptionItem[];
  readonly isLoading: boolean;
  readonly error: string | null;
  readonly refetch: () => Promise<void>;
}

export function useSubscriptions(token: string | null): UseSubscriptionsResult {
  const [subscriptions, setSubscriptions] = useState<readonly SubscriptionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscriptions = useCallback(async () => {
    if (!token) {
      setSubscriptions([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await listSubscriptions(token);
      setSubscriptions(response.items);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : 'Subscriptions load failed');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void fetchSubscriptions();
  }, [fetchSubscriptions]);

  return useMemo(
    () => ({ subscriptions, isLoading, error, refetch: fetchSubscriptions }),
    [subscriptions, isLoading, error, fetchSubscriptions]
  );
}
