// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
export interface SWRLikeConfig {
  dedupingInterval: number;
  revalidateOnFocus: boolean;
  errorRetryCount: number;
  errorRetryInterval: number;
}

export function useSWRConfig(overrides?: Partial<SWRLikeConfig>): SWRLikeConfig {
  return {
    dedupingInterval: overrides?.dedupingInterval ?? 10_000,
    revalidateOnFocus: overrides?.revalidateOnFocus ?? false,
    errorRetryCount: overrides?.errorRetryCount ?? 2,
    errorRetryInterval: overrides?.errorRetryInterval ?? 1_500
  };
}
