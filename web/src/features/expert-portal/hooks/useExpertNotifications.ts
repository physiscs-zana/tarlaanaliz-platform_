// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-019: Expert portal review sayısı değişimi bildirim olarak izlenir.
'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { listPendingReviews } from '../services/expertReviewService';

const POLL_INTERVAL_MS = 30_000;

export interface UseExpertNotificationsResult {
  readonly unreadCount: number;
  readonly isLoading: boolean;
  readonly error: string | null;
}

export function useExpertNotifications(token: string | null): UseExpertNotificationsResult {
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const previousCountRef = useRef<number | null>(null);

  const poll = useCallback(async () => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      const response = await listPendingReviews(token);
      const queued = response.items.filter((item) => item.status === 'queued').length;
      if (previousCountRef.current !== null && queued > previousCountRef.current) {
        setUnreadCount((prev) => prev + (queued - (previousCountRef.current ?? 0)));
      } else if (previousCountRef.current === null) {
        setUnreadCount(queued);
      }
      previousCountRef.current = queued;
      setError(null);
    } catch (pollError) {
      setError(pollError instanceof Error ? pollError.message : 'Notification poll failed');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void poll();
    const interval = setInterval(() => { void poll(); }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [poll]);

  return useMemo(
    () => ({ unreadCount, isLoading, error }),
    [unreadCount, isLoading, error]
  );
}
