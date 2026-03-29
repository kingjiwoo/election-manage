"""전략 리포트 생성 서비스 (멀티 LLM)"""
import logging
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign_spot import CampaignSpot
from app.services.llm import get_provider

logger = logging.getLogger(__name__)

MAX_SPOTS_IN_PROMPT = 10


def _build_prompt(spots: list[CampaignSpot], candidate_name: str) -> str:
    top_spots = sorted(
        [s for s in spots if s.score is not None],
        key=lambda s: s.score,
        reverse=True,
    )[:MAX_SPOTS_IN_PROMPT]

    spot_lines = "\n".join(
        f"- {s.name} (스코어 {s.score:.2f} | 혼잡도 {s.congestion_score or 0:.2f} | 인구 {s.population_score or 0:.2f} | 방문패널티 {s.visit_penalty:.2f})"
        for s in top_spots
    )
    unscored = len([s for s in spots if s.score is None])

    return f"""당신은 선거 캠프 전략 전문가입니다.
아래 데이터를 바탕으로 {candidate_name} 후보의 유세 전략 리포트를 작성해주세요.

## 유세지 스코어 상위 {len(top_spots)}곳
{spot_lines if spot_lines else "스코어 데이터 없음 — 먼저 스코어를 갱신해주세요."}

## 미산정 유세지
{unscored}곳

---
다음 항목으로 리포트를 작성해주세요:

1. **핵심 요약** (3줄 이내)
2. **최우선 유세지 TOP 3** — 각각 방문을 권장하는 이유
3. **시간대별 유세 전략** — 오전/오후/저녁 배분
4. **주의 사항** — 방문 패널티가 높은 지역, 데이터 보완 필요 지역
5. **다음 액션 아이템** — 구체적인 실행 계획 3가지

리포트는 한국어로, 실무 담당자가 바로 활용할 수 있도록 구체적으로 작성해주세요."""


class ReportService:

    async def generate(
        self,
        db: AsyncSession,
        candidate_name: str = "후보",
        llm: str = "claude",
    ) -> str:
        result = await db.execute(select(CampaignSpot))
        spots = list(result.scalars().all())
        if not spots:
            return "등록된 유세지가 없습니다. 먼저 유세지를 등록하고 스코어를 갱신해주세요."
        provider = get_provider(llm)
        return await provider.generate(_build_prompt(spots, candidate_name))

    async def generate_stream(
        self,
        db: AsyncSession,
        candidate_name: str = "후보",
        llm: str = "claude",
    ) -> AsyncIterator[str]:
        result = await db.execute(select(CampaignSpot))
        spots = list(result.scalars().all())
        if not spots:
            yield "등록된 유세지가 없습니다."
            return
        provider = get_provider(llm)
        async for chunk in provider.stream(_build_prompt(spots, candidate_name)):
            yield chunk


report_service = ReportService()
