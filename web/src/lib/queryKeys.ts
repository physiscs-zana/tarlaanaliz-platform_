// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

export const queryKeys = {
  auth: ['auth'] as const,
  fields: ['fields'] as const,
  missions: ['missions'] as const,
  payments: ['payments'] as const,
  subscriptions: ['subscriptions'] as const,
  results: ['results'] as const,
  auditLogs: ['auditLogs'] as const,
  featureFlags: ['featureFlags'] as const,
  byId: (scope: string, id: string) => [scope, id] as const,
  paged: (scope: string, page: number, pageSize: number) => [scope, 'paged', page, pageSize] as const
};
