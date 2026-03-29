"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const KakaoMap = dynamic(() => import("@/components/KakaoMap"), { ssr: false });

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Spot {
  id: number;
  name: string;
  lat: number;
  lng: number;
  score: number | null;
  spot_type: string;
  visit_penalty: number;
  congestion_score: number | null;
  population_score: number | null;
  last_visited_at: string | null;
}

const SPOT_TYPE_LABEL: Record<string, string> = {
  apartment: "아파트 단지",
  station: "역세권",
  market: "시장/상가",
  etc: "기타",
};

function ScoreBar({ value, color }: { value: number | null; color: string }) {
  return (
    <div className="w-full bg-gray-700 rounded-full h-1.5">
      <div
        className="h-1.5 rounded-full transition-all"
        style={{ width: `${(value ?? 0) * 100}%`, backgroundColor: color }}
      />
    </div>
  );
}

export default function MapPage() {
  const queryClient = useQueryClient();
  const [selectedSpot, setSelectedSpot] = useState<Spot | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["spots"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/spots`);
      const json = await res.json();
      return json.data as Spot[];
    },
  });

  const scoreAll = useMutation({
    mutationFn: () =>
      fetch(`${API_BASE}/api/spots/score-all`, { method: "POST" }).then((r) => r.json()),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["spots"] }),
  });

  const markVisited = useMutation({
    mutationFn: (id: number) =>
      fetch(`${API_BASE}/api/spots/${id}/visit`, { method: "POST" }).then((r) => r.json()),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["spots"] }),
  });

  const spots = data ?? [];
  const topSpots = [...spots].sort((a, b) => (b.score ?? 0) - (a.score ?? 0)).slice(0, 10);

  return (
    <div className="flex flex-1 min-h-0 bg-gray-900 text-white">
      {/* 사이드바 */}
      <aside className="w-72 flex flex-col border-r border-gray-700">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h1 className="font-bold text-lg">유세지 추천</h1>
          <button
            onClick={() => scoreAll.mutate()}
            disabled={scoreAll.isPending}
            className="text-xs px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded disabled:opacity-50"
          >
            {scoreAll.isPending ? "갱신 중..." : "스코어 갱신"}
          </button>
        </div>

        {/* 범례 */}
        <div className="px-4 py-2 border-b border-gray-700 flex gap-3 text-xs text-gray-400">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" />고득점</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500" />중간</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" />저득점</span>
        </div>

        {/* 상위 유세지 목록 */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <p className="text-center text-gray-400 mt-8">로딩 중...</p>
          ) : topSpots.length === 0 ? (
            <p className="text-center text-gray-500 mt-8 text-sm">
              등록된 유세지가 없습니다.
            </p>
          ) : (
            topSpots.map((spot, idx) => (
              <button
                key={spot.id}
                onClick={() => setSelectedSpot(spot)}
                className={`w-full text-left px-4 py-3 border-b border-gray-700 hover:bg-gray-800 transition-colors ${
                  selectedSpot?.id === spot.id ? "bg-gray-800" : ""
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm truncate">
                    <span className="text-gray-500 mr-1">#{idx + 1}</span>
                    {spot.name}
                  </span>
                  <span className="text-xs text-gray-400 ml-2 shrink-0">
                    {spot.score !== null ? `${(spot.score * 100).toFixed(1)}점` : "—"}
                  </span>
                </div>
                <ScoreBar
                  value={spot.score}
                  color={spot.score !== null && spot.score >= 0.7 ? "#ef4444" : spot.score !== null && spot.score >= 0.4 ? "#f59e0b" : "#22c55e"}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {SPOT_TYPE_LABEL[spot.spot_type] ?? spot.spot_type}
                </p>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* 지도 + 상세 */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 relative">
          <KakaoMap spots={spots} onSpotClick={setSelectedSpot} />
          {!process.env.NEXT_PUBLIC_KAKAO_JS_KEY && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-950/80">
              <p className="text-gray-400 text-sm">
                NEXT_PUBLIC_KAKAO_JS_KEY를 설정하면 지도가 표시됩니다.
              </p>
            </div>
          )}
        </div>

        {/* 선택 유세지 상세 */}
        {selectedSpot && (
          <div className="h-40 border-t border-gray-700 p-4 flex gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h2 className="font-bold">{selectedSpot.name}</h2>
                <span className="text-xs px-2 py-0.5 bg-gray-700 rounded">
                  {SPOT_TYPE_LABEL[selectedSpot.spot_type]}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div>
                  <p className="text-gray-400 text-xs mb-0.5">종합 스코어</p>
                  <p className="font-bold text-lg">
                    {selectedSpot.score !== null ? `${(selectedSpot.score * 100).toFixed(1)}점` : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-0.5">혼잡도</p>
                  <p>{selectedSpot.congestion_score !== null ? `${(selectedSpot.congestion_score * 100).toFixed(0)}%` : "—"}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs mb-0.5">인구 밀도</p>
                  <p>{selectedSpot.population_score !== null ? `${(selectedSpot.population_score * 100).toFixed(0)}%` : "—"}</p>
                </div>
              </div>
            </div>
            <div className="flex flex-col justify-center gap-2">
              <button
                onClick={() => markVisited.mutate(selectedSpot.id)}
                disabled={markVisited.isPending}
                className="px-4 py-2 bg-green-700 hover:bg-green-600 rounded text-sm disabled:opacity-50"
              >
                방문 처리
              </button>
              <p className="text-xs text-gray-500 text-center">
                {selectedSpot.last_visited_at
                  ? `마지막: ${new Date(selectedSpot.last_visited_at).toLocaleDateString("ko-KR")}`
                  : "미방문"}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
