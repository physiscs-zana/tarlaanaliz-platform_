// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

export const routes = {
  login: '/login',
  farmerHome: '/farmer',
  expertHome: '/expert',
  pilotHome: '/pilot',
  adminHome: '/admin',
  subscription: '/farmer/subscription',
  payments: '/farmer/payments',
  results: '/farmer/results'
} as const;

export type AppRoute = (typeof routes)[keyof typeof routes];
