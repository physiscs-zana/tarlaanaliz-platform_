// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
// KR-071: Correlation ID üretimi correlation.ts kanonik kaynağından yapılır.
import { useMemo } from 'react';

import {
  createCorrelationId,
  createRequestId as createReqId,
  toCorrelationHeaders,
} from '@/lib/correlation';

export function useCorrelationId(seed?: string) {
  const corrId = useMemo(() => seed ?? createCorrelationId(), [seed]);

  const createRequestId = () => createReqId();

  const withTraceHeaders = (headers?: HeadersInit, requestId?: string): HeadersInit => ({
    ...(headers ?? {}),
    ...toCorrelationHeaders({ corrId, requestId: requestId ?? createRequestId() }),
  });

  return {
    corrId,
    createRequestId,
    withTraceHeaders,
  };
}
