// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// KR-071: AI çıktıları yalnızca NDVI/NDRE; karar mekanizması değil.
// KR-081: Contract-first tip tanımları.

import { http } from '@/lib/http';

export interface ResultData {
  readonly resultId: string;
  readonly missionId: string;
  readonly ndviData: Record<string, unknown> | null;
  readonly ndreData: Record<string, unknown> | null;
  readonly confidenceScore: number;
  readonly resultUrl: string | null;
  readonly createdAtIso: string;
}

export interface ResultListItem {
  readonly resultId: string;
  readonly missionId: string;
  readonly confidenceScore: number;
  readonly createdAtIso: string;
}

export interface ResultListResponse {
  readonly items: readonly ResultListItem[];
}

export async function getResult(missionId: string, token: string): Promise<ResultData> {
  return http<ResultData>(`/results/${missionId}`, {
    method: 'GET',
    token,
  });
}

export async function listMissionResults(
  missionId: string,
  token: string
): Promise<ResultListResponse> {
  return http<ResultListResponse>(`/results?mission_id=${encodeURIComponent(missionId)}`, {
    method: 'GET',
    token,
  });
}
