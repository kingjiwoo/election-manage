"""유세지 스코어링 엔진

공식: (실시간 혼잡도 × 0.4) + (거주 인구 밀도 × 0.3) - (최근 방문 페널티 × 0.3)
"""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign_spot import CampaignSpot
from app.models.population_data import CongestionData, PopulationData

logger = logging.getLogger(__name__)

WEIGHT_CONGESTION = 0.4
WEIGHT_POPULATION = 0.3
WEIGHT_PENALTY = 0.3

# 방문 페널티: 며칠 내 방문 시 패널티 적용
PENALTY_DAYS = 7


class ScoringService:

    async def _get_latest_congestion_score(
        self, db: AsyncSession, spot_id: int
    ) -> float:
        """최근 혼잡도 스코어 조회 (없으면 0.5 기본값)"""
        result = await db.execute(
            select(CongestionData.congestion_score)
            .where(CongestionData.spot_id == spot_id)
            .order_by(CongestionData.measured_at.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return float(row) if row is not None else 0.5

    async def _get_population_score(
        self, db: AsyncSession, district_code: str | None
    ) -> float:
        """행정동 인구 스코어 (최근 데이터 기준, 없으면 0.5)"""
        if not district_code:
            return 0.5

        result = await db.execute(
            select(PopulationData.total_population)
            .where(PopulationData.district_code == district_code)
            .order_by(PopulationData.measured_at.desc())
            .limit(1)
        )
        population = result.scalar_one_or_none()
        if population is None:
            return 0.5

        # 인구수를 0~1로 정규화 (최대 50,000 기준)
        return min(float(population) / 50_000, 1.0)

    def _calc_visit_penalty(self, last_visited_at: datetime | None) -> float:
        """방문 페널티 계산 (7일 이내 방문 시 최대 1.0)"""
        if last_visited_at is None:
            return 0.0
        now = datetime.now(timezone.utc)
        days_since = (now - last_visited_at).days
        if days_since >= PENALTY_DAYS:
            return 0.0
        return 1.0 - (days_since / PENALTY_DAYS)

    def calc_score(
        self,
        congestion_score: float,
        population_score: float,
        visit_penalty: float,
    ) -> float:
        score = (
            congestion_score * WEIGHT_CONGESTION
            + population_score * WEIGHT_POPULATION
            - visit_penalty * WEIGHT_PENALTY
        )
        return round(max(0.0, min(1.0, score)), 4)

    async def score_spot(
        self,
        db: AsyncSession,
        spot: CampaignSpot,
        district_code: str | None = None,
    ) -> CampaignSpot:
        """단일 유세지 스코어 갱신"""
        congestion = await self._get_latest_congestion_score(db, spot.id)
        population = await self._get_population_score(db, district_code)
        penalty = self._calc_visit_penalty(spot.last_visited_at)

        spot.congestion_score = congestion
        spot.population_score = population
        spot.visit_penalty = penalty
        spot.score = self.calc_score(congestion, population, penalty)
        spot.score_updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(spot)
        return spot

    async def score_all(self, db: AsyncSession) -> list[CampaignSpot]:
        """전체 유세지 스코어 일괄 갱신"""
        result = await db.execute(select(CampaignSpot))
        spots = list(result.scalars().all())

        for spot in spots:
            await self.score_spot(db, spot)

        logger.info(f"스코어 갱신 완료: {len(spots)}개")
        return spots

    async def mark_visited(self, db: AsyncSession, spot_id: int) -> CampaignSpot | None:
        """방문 처리 (페널티 적용 시작)"""
        spot = await db.get(CampaignSpot, spot_id)
        if not spot:
            return None
        spot.last_visited_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(spot)
        return spot


scoring_service = ScoringService()
