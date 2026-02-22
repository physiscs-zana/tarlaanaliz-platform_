// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-081: Contract-first tip tanımları.

import { http } from '@/lib/http';

export interface WeatherBlockItem {
  readonly reportId: string;
  readonly missionId: string;
  readonly blockedReason: string;
  readonly reportDate: string;
  readonly verifiedByAdmin: boolean;
  readonly createdAtIso: string;
}

export interface WeatherBlockListResponse {
  readonly items: readonly WeatherBlockItem[];
}

export interface WeatherBlockPayload {
  readonly missionId: string;
  readonly blockedReason: string;
  readonly reportDate: string;
}

export async function listWeatherBlocks(token: string): Promise<WeatherBlockListResponse> {
  return http<WeatherBlockListResponse>('/weather_block_reports', {
    method: 'GET',
    token,
  });
}

export async function reportWeatherBlock(
  payload: WeatherBlockPayload,
  token: string
): Promise<WeatherBlockItem> {
  return http<WeatherBlockItem>('/weather_block_reports', {
    method: 'POST',
    body: JSON.stringify(payload),
    token,
  });
}
