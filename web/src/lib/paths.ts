/* BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated. */
// Dinamik segment içeren route'lar için yardımcı fonksiyonlar.
// Sabit route'lar routes.ts'de tanımlıdır.

export const paths = {
  home: "/",
  auth: {
    login: "/login",
  },
  expert: {
    queue: "/queue",
    review: (reviewId: string) => `/review/${encodeURIComponent(reviewId)}`,
    reviewDetail: (id: string) => `/reviews/${encodeURIComponent(id)}`,
  },
  farmer: {
    field: (id: string) => `/fields/${encodeURIComponent(id)}`,
    mission: (id: string) => `/missions/${encodeURIComponent(id)}`,
    result: (missionId: string) => `/results/${encodeURIComponent(missionId)}`,
    createSubscription: "/subscriptions/create",
  },
} as const;
