// BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
// Route sabitleri: routes.ts
// API endpoint'leri: features/*/services/*.ts
// Auth sabitleri: authStorage.ts

export const AUTH_TOKEN_TTL_MS = 24 * 60 * 60 * 1000; // 24 saat
export const COOKIE_TOKEN_KEY = 'ta_token';
export const COOKIE_ROLE_KEY = 'ta_role';
export const API_TIMEOUT_MS = 10_000;
