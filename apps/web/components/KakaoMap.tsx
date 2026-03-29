"use client";

import { useEffect, useRef } from "react";

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

interface Props {
  spots: Spot[];
  onSpotClick?: (spot: Spot) => void;
}

declare global {
  interface Window {
    kakao: {
      maps: {
        load: (callback: () => void) => void;
        Map: new (container: HTMLElement, options: object) => KakaoMap;
        LatLng: new (lat: number, lng: number) => KakaoLatLng;
        Marker: new (options: object) => KakaoMarker;
        InfoWindow: new (options: object) => KakaoInfoWindow;
        Circle: new (options: object) => KakaoCircle;
        event: { addListener: (target: object, type: string, handler: () => void) => void };
      };
    };
  }
  interface KakaoMap { setCenter: (latlng: KakaoLatLng) => void }
  interface KakaoLatLng {}
  interface KakaoMarker { setMap: (map: KakaoMap | null) => void; getPosition: () => KakaoLatLng }
  interface KakaoInfoWindow { open: (map: KakaoMap, marker: KakaoMarker) => void; close: () => void }
  interface KakaoCircle { setMap: (map: KakaoMap | null) => void }
}

function scoreToColor(score: number | null): string {
  if (score === null) return "#6b7280";
  if (score >= 0.7) return "#ef4444";
  if (score >= 0.4) return "#f59e0b";
  return "#22c55e";
}

function scoreToRadius(score: number | null): number {
  return 100 + (score ?? 0.5) * 300;
}

export default function KakaoMap({ spots, onSpotClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<KakaoMap | null>(null);
  const markersRef = useRef<KakaoMarker[]>([]);
  const circlesRef = useRef<KakaoCircle[]>([]);
  const infoWindowRef = useRef<KakaoInfoWindow | null>(null);

  useEffect(() => {
    const appKey = process.env.NEXT_PUBLIC_KAKAO_JS_KEY;
    if (!appKey || !containerRef.current) return;

    const script = document.createElement("script");
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${appKey}&autoload=false`;
    script.async = true;
    document.head.appendChild(script);

    script.onload = () => {
      window.kakao.maps.load(() => {
        if (!containerRef.current) return;
        const map = new window.kakao.maps.Map(containerRef.current, {
          center: new window.kakao.maps.LatLng(37.5665, 126.978),
          level: 8,
        });
        mapRef.current = map;
        renderSpots(map);
      });
    };

    return () => {
      document.head.removeChild(script);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (mapRef.current) renderSpots(mapRef.current);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [spots]);

  function renderSpots(map: KakaoMap) {
    // 기존 마커/원 제거
    markersRef.current.forEach((m) => m.setMap(null));
    circlesRef.current.forEach((c) => c.setMap(null));
    markersRef.current = [];
    circlesRef.current = [];

    spots.forEach((spot) => {
      const position = new window.kakao.maps.LatLng(spot.lat, spot.lng);

      // 스코어 원
      const circle = new window.kakao.maps.Circle({
        map,
        center: position,
        radius: scoreToRadius(spot.score),
        strokeWeight: 1,
        strokeColor: scoreToColor(spot.score),
        strokeOpacity: 0.8,
        fillColor: scoreToColor(spot.score),
        fillOpacity: 0.2,
      });
      circlesRef.current.push(circle);

      // 마커
      const marker = new window.kakao.maps.Marker({ map, position });
      markersRef.current.push(marker);

      // 클릭 시 인포윈도우
      window.kakao.maps.event.addListener(marker, "click", () => {
        infoWindowRef.current?.close();
        const iw = new window.kakao.maps.InfoWindow({
          content: `
            <div style="padding:8px 12px;font-size:13px;min-width:140px">
              <strong>${spot.name}</strong><br/>
              <span>스코어: ${spot.score !== null ? (spot.score * 100).toFixed(1) + "점" : "미산정"}</span><br/>
              <span style="color:#6b7280;font-size:11px">${spot.spot_type}</span>
            </div>
          `,
        });
        iw.open(map, marker);
        infoWindowRef.current = iw;
        onSpotClick?.(spot);
      });
    });
  }

  return (
    <div ref={containerRef} className="w-full h-full" />
  );
}
