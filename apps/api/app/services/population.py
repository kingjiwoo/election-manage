"""서울시 생활인구 공공데이터 수집 서비스"""
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.population_data import PopulationData

logger = logging.getLogger(__name__)

# 서울시 우리마을가게 상권분석서비스 - 생활인구 API
# 공공데이터포털: https://www.data.go.kr
PUBLIC_DATA_BASE_URL = "https://openapi.seoul.go.kr:8088"


class PopulationService:
    def __init__(self):
        self.api_key = settings.public_data_api_key

    async def fetch_living_population(
        self, district_code: str, target_date: str
    ) -> list[dict]:
        """서울시 생활인구 데이터 조회

        Args:
            district_code: 행정동 코드 (예: '1168010800')
            target_date: 조회 날짜 (YYYYMMDD)
        """
        if not self.api_key:
            logger.warning("PUBLIC_DATA_API_KEY가 설정되지 않았습니다.")
            return []

        service = "VwsmAdstrdInfoInqireService"
        url = f"{PUBLIC_DATA_BASE_URL}/{self.api_key}/json/{service}/1/100"
        params = {
            "STDR_DE": target_date,
            "ADSTRD_CODE_SE": district_code,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                return data.get(service, {}).get("row", [])
            except httpx.HTTPError as e:
                logger.error(f"공공데이터 API 오류: {e}")
                return []

    def parse_row(self, row: dict) -> dict:
        """API 응답 행을 파싱"""
        def safe_int(val) -> int | None:
            try:
                return int(float(val)) if val not in (None, "", "null") else None
            except (ValueError, TypeError):
                return None

        return {
            "district_code": str(row.get("ADSTRD_CODE_SE", "")),
            "district_name": str(row.get("ADSTRD_NM", "")),
            "total_population": safe_int(row.get("TOT_LVPOP_CO")),
            "male_population": safe_int(row.get("ML_LVPOP_CO")),
            "female_population": safe_int(row.get("FML_LVPOP_CO")),
            "age_10s": safe_int(row.get("AGRDE_10_LVPOP_CO")),
            "age_20s": safe_int(row.get("AGRDE_20_LVPOP_CO")),
            "age_30s": safe_int(row.get("AGRDE_30_LVPOP_CO")),
            "age_40s": safe_int(row.get("AGRDE_40_LVPOP_CO")),
            "age_50s": safe_int(row.get("AGRDE_50_LVPOP_CO")),
            "age_60s_plus": safe_int(row.get("AGRDE_60_ABOVE_LVPOP_CO")),
        }

    async def collect_and_save(
        self, db: AsyncSession, district_code: str, target_date: str
    ) -> list[PopulationData]:
        """생활인구 수집 후 DB 저장"""
        rows = await self.fetch_living_population(district_code, target_date)
        records = []

        for row in rows:
            parsed = self.parse_row(row)
            record = PopulationData(
                **parsed,
                measured_at=datetime.now(timezone.utc),
            )
            db.add(record)
            records.append(record)

        if records:
            await db.commit()
            for r in records:
                await db.refresh(r)

        return records


population_service = PopulationService()
