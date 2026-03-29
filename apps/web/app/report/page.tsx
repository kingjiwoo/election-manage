"use client";

import { useState, useRef } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ReportPage() {
  const [candidateName, setCandidateName] = useState("");
  const [selectedLlm, setSelectedLlm] = useState("claude");
  const [report, setReport] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const reportRef = useRef<HTMLDivElement>(null);

  const LLM_OPTIONS = [
    { value: "claude", label: "Claude", sub: "claude-sonnet-4-6" },
    { value: "gpt", label: "GPT", sub: "gpt-4o" },
    { value: "gemini", label: "Gemini", sub: "gemini-2.0-flash" },
  ];

  async function generateReport() {
    const name = candidateName.trim() || "후보";
    setReport("");
    setError("");
    setIsLoading(true);

    try {
      const res = await fetch(
        `${API_BASE}/api/report/stream?candidate_name=${encodeURIComponent(name)}&llm=${selectedLlm}`,
        { method: "POST" }
      );

      if (!res.ok || !res.body) {
        throw new Error(`API 오류 (${res.status})`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setReport((prev) => prev + chunk);
        // 자동 스크롤
        requestAnimationFrame(() => {
          reportRef.current?.scrollTo(0, reportRef.current.scrollHeight);
        });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "알 수 없는 오류");
    } finally {
      setIsLoading(false);
    }
  }

  function copyReport() {
    navigator.clipboard.writeText(report);
  }

  return (
    <div className="flex flex-col flex-1 min-h-0 bg-gray-900 text-white">
      {/* 헤더 */}
      <header className="px-6 py-4 border-b border-gray-700 flex items-center gap-4">
        <h1 className="text-xl font-bold">유세 전략 리포트</h1>
        <span className="text-xs text-gray-400 px-2 py-0.5 bg-gray-800 rounded">
          Powered by Claude
        </span>
      </header>

      <div className="flex flex-1 overflow-hidden gap-0">
        {/* 설정 패널 */}
        <aside className="w-64 border-r border-gray-700 p-5 flex flex-col gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1.5">후보자 이름</label>
            <input
              type="text"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              placeholder="김철수"
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* LLM 선택 */}
          <div>
            <label className="block text-sm text-gray-400 mb-1.5">LLM 선택</label>
            <div className="flex flex-col gap-1.5">
              {LLM_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setSelectedLlm(opt.value)}
                  className={`flex items-center justify-between px-3 py-2 rounded border text-sm transition-colors ${
                    selectedLlm === opt.value
                      ? "border-blue-500 bg-blue-500/10 text-blue-300"
                      : "border-gray-600 bg-gray-800 text-gray-300 hover:border-gray-500"
                  }`}
                >
                  <span className="font-medium">{opt.label}</span>
                  <span className="text-xs text-gray-500">{opt.sub}</span>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={generateReport}
            disabled={isLoading}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 rounded font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                생성 중...
              </span>
            ) : (
              "리포트 생성"
            )}
          </button>

          {report && (
            <button
              onClick={copyReport}
              className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
            >
              클립보드 복사
            </button>
          )}

          <div className="mt-auto text-xs text-gray-500 space-y-1">
            <p>· 등록된 유세지 스코어 데이터 기반</p>
            <p>· 스코어 갱신 후 생성 권장</p>
          </div>
        </aside>

        {/* 리포트 뷰어 */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {error && (
            <div className="mx-6 mt-4 px-4 py-3 bg-red-900/50 border border-red-700 rounded text-sm text-red-300">
              {error}
            </div>
          )}

          {!report && !isLoading && (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
              <p className="text-lg mb-2">리포트가 없습니다</p>
              <p className="text-sm">후보자 이름을 입력하고 리포트를 생성하세요.</p>
            </div>
          )}

          {(report || isLoading) && (
            <div
              ref={reportRef}
              className="flex-1 overflow-y-auto p-6"
            >
              <div className="max-w-3xl mx-auto">
                <div className="prose prose-invert prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap font-sans text-sm text-gray-200 leading-relaxed">
                    {report}
                    {isLoading && (
                      <span className="inline-block w-1.5 h-4 bg-blue-400 animate-pulse ml-0.5 align-middle" />
                    )}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
