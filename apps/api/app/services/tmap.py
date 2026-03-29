"""SKT Tmap 실시간 혼잡도 API 클라이언트"""
import json
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.population_data import CongestionData

logger = logging.getLogger(__name__)

TMAP_BASE_URL = "https://apis.openapi.sk.com/tmap"


class TmapService:
    def __init__(self):
        self.app_key = settings.skt_tmap_app_key
        self.headers = {
            "appKey": self.app_key,
            "Content-Type": "application/json",
        }

    async def get_congestion(self, lat: float, lng: float) -> dict | None:
        """특정 좌표의 혼잡도 조회"""
        if not self.app_key:
            logger.warning("SKT_TMAP_APP_KEY가 설정되지 않았습니다.")
            return None

        url = f"{TMAP_BASE_URL}/poi/congestion"
        params = {"version": 1, "lat": lat, "lon": lng}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url, headers=self.headers, params=params)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as e:
                logger.error(f"Tmap API 오류: {e}")
                return None

    def normalize_congestion(self, level: int) -> float:
        """혼잡도 레벨(1~5)을 0~1 스코어로 정규화"""
        return (level - 1) / 4.0

    async def collect_and_save(
        self, db: AsyncSession, spot_id: int, lat: float, lng: float
    ) -> CongestionData | None:
        """혼잡도 수집 후 DB 저장"""
        data = await self.get_congestion(lat, lng)
        if data is None:
            return None

        level = data.get("congestionLevel", 3)
        record = CongestionData(
            spot_id=spot_id,
            measured_at=datetime.now(timezone.utc),
            congestion_level=level,
            congestion_score=self.normalize_congestion(level),
            raw_data=json.dumps(data, ensure_ascii=False)[:2000],
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record


tmap_service = TmapService()
