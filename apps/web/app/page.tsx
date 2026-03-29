"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const FEATURES = [
  {
    href: "/org",
    icon: "🔗",
    title: "조직 인맥 트리",
    description: "지지자·핵심 당원 관계를 그래프로 시각화하고 공백 지역을 탐지합니다.",
    color: "border-blue-500/40 hover:border-blue-500",
    badge: "Neo4j",
  },
  {
    href: "/map",
    icon: "📍",
    title: "유세지 지도",
    description: "스코어링 공식으로 최적 유세지를 추천하고 방문 이력을 관리합니다.",
    color: "border-amber-500/40 hover:border-amber-500",
    badge: "Kakao Maps",
  },
  {
    href: "/report",
    icon: "📋",
    title: "전략 리포트",
    description: "Claude·GPT·Gemini로 데이터 기반 유세 전략 리포트를 자동 생성합니다.",
    color: "border-green-500/40 hover:border-green-500",
    badge: "AI",
  },
];

export default function HomePage() {
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/health`);
      return res.json();
    },
    retry: false,
  });

  const { data: spots } = useQuery({
    queryKey: ["spots-summary"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/spots`);
      const json = await res.json();
      return json.data as { id: number; score: number | null }[];
    },
    retry: false,
  });

  const apiOnline = health?.data?.status === "ok";
  const spotCount = spots?.length ?? 0;
  const scoredCount = spots?.filter((s) => s.score !== null).length ?? 0;

  return (
    <div className="flex-1 bg-gray-950 text-white">
      {/* 히어로 */}
      <section className="px-8 py-12 border-b border-gray-800">
        <div className="max-w-3xl">
          <h1 className="text-3xl font-bold mb-3">선거 캠프 관리 시스템</h1>
          <p className="text-gray-400 text-lg">
            Graph DB 기반 조직 관리 + 실시간 유동인구 데이터로 최적 유세지를 추천합니다.
          </p>
          <div className="mt-4 flex items-center gap-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${apiOnline ? "bg-green-500" : "bg-red-500"}`} />
            <span className="text-gray-400">
              API 서버 {apiOnline ? "연결됨" : "연결 안됨 (localhost:8000)"}
            </span>
          </div>
        </div>
      </section>

      {/* 통계 */}
      <section className="px-8 py-6 border-b border-gray-800 flex gap-8">
        {[
          { label: "등록 유세지", value: spotCount },
          { label: "스코어 산정", value: scoredCount },
          { label: "미산정", value: spotCount - scoredCount },
        ].map((stat) => (
          <div key={stat.label}>
            <p className="text-2xl font-bold">{stat.value}</p>
            <p className="text-sm text-gray-400">{stat.label}</p>
          </div>
        ))}
      </section>

      {/* 기능 카드 */}
      <section className="px-8 py-8">
        <h2 className="text-lg font-semibold mb-5 text-gray-300">주요 기능</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl">
          {FEATURES.map((f) => (
            <Link
              key={f.href}
              href={f.href}
              className={`block p-5 bg-gray-900 border rounded-lg transition-colors ${f.color}`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">{f.icon}</span>
                <span className="text-xs px-2 py-0.5 bg-gray-800 text-gray-400 rounded">
                  {f.badge}
                </span>
              </div>
              <h3 className="font-semibold mb-1">{f.title}</h3>
              <p className="text-sm text-gray-400">{f.description}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* 빠른 시작 */}
      <section className="px-8 py-6 border-t border-gray-800">
        <h2 className="text-sm font-semibold text-gray-500 mb-3">빠른 시작</h2>
        <ol className="flex flex-wrap gap-6 text-sm text-gray-400">
          {[
            { step: 1, label: "유세지 등록", path: "/map" },
            { step: 2, label: "스코어 갱신", path: "/map" },
            { step: 3, label: "조직원 등록", path: "/org" },
            { step: 4, label: "리포트 생성", path: "/report" },
          ].map(({ step, label, path }) => (
            <li key={step} className="flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-gray-700 text-xs flex items-center justify-center text-white">
                {step}
              </span>
              {label}
              <span className="text-gray-600">{path}</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
