// 공통 API 응답 구조
export interface ApiResponse<T> {
  data: T | null;
  error: ApiError | null;
  meta: ApiMeta;
}

export interface ApiError {
  code: string;
  message: string;
}

export interface ApiMeta {
  total?: number;
  page?: number;
  pageSize?: number;
}

// 조직 관련 타입
export interface Candidate {
  id: string;
  name: string;
  district: string;
}

export interface CoreMember {
  id: string;
  name: string;
  phone?: string;
  region: string;
}

export interface Supporter {
  id: string;
  name: string;
  phone?: string;
  address?: string;
  introducedBy?: string;
}

// 유세지 관련 타입
export interface CampaignSpot {
  id: string;
  name: string;
  lat: number;
  lng: number;
  score: number;
  congestionScore: number;
  populationScore: number;
  visitPenalty: number;
  lastVisitedAt?: string;
}
