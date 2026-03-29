"use client";

import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";

const OrgTree = dynamic(() => import("@/components/OrgTree"), { ssr: false });

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface GraphNode {
  id: string;
  name: string;
  label: string;
  [key: string]: unknown;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

const LABEL_KO: Record<string, string> = {
  Candidate: "후보자",
  CoreMember: "핵심 당원",
  Supporter: "지지자",
  Organization: "조직",
};

const LABEL_COLOR: Record<string, string> = {
  Candidate: "bg-red-500",
  CoreMember: "bg-blue-500",
  Supporter: "bg-green-500",
  Organization: "bg-amber-500",
};

export default function OrgPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["org-tree"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/org/tree`);
      if (!res.ok) throw new Error("API 오류");
      const json = await res.json();
      return json.data as { nodes: GraphNode[]; links: GraphLink[] };
    },
  });

  const { data: blanks } = useQuery({
    queryKey: ["blank-regions"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/org/blank-regions`);
      if (!res.ok) throw new Error("API 오류");
      const json = await res.json();
      return json.data as string[];
    },
  });

  const nodeCount = data?.nodes.length ?? 0;
  const byLabel = data?.nodes.reduce<Record<string, number>>((acc, n) => {
    acc[n.label] = (acc[n.label] ?? 0) + 1;
    return acc;
  }, {}) ?? {};

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* 헤더 */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">조직 인맥 트리</h1>
        <div className="flex items-center gap-4 text-sm text-gray-400">
          {Object.entries(LABEL_KO).map(([key, label]) => (
            <span key={key} className="flex items-center gap-1.5">
              <span className={`w-2.5 h-2.5 rounded-full ${LABEL_COLOR[key]}`} />
              {label} ({byLabel[key] ?? 0})
            </span>
          ))}
          <span className="text-gray-500">전체 {nodeCount}명</span>
        </div>
      </header>

      {/* 메인 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 그래프 */}
        <div className="flex-1">
          {isLoading && (
            <div className="flex h-full items-center justify-center text-gray-400">
              로딩 중...
            </div>
          )}
          {isError && (
            <div className="flex h-full items-center justify-center text-red-400">
              API 서버에 연결할 수 없습니다.
            </div>
          )}
          {data && (
            <OrgTree nodes={data.nodes} links={data.links} />
          )}
        </div>

        {/* 사이드바: 공백 지역 */}
        {blanks && blanks.length > 0 && (
          <aside className="w-64 border-l border-gray-700 p-4 overflow-y-auto">
            <h2 className="text-sm font-semibold text-amber-400 mb-3">
              ⚠ 공백 지역 ({blanks.length}곳)
            </h2>
            <ul className="space-y-1.5 text-sm text-gray-300">
              {blanks.map((name) => (
                <li key={name} className="px-2 py-1 bg-gray-800 rounded">
                  {name}
                </li>
              ))}
            </ul>
          </aside>
        )}
      </div>
    </div>
  );
}
