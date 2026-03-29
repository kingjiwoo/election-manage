"""Claude API 기반 유세 전략 리포트 생성 서비스"""
import logging
from typing import AsyncIterator

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.campaign_spot import CampaignSpot

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
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

    unscored = [s for s in spots if s.score is None]

    return f"""당신은 선거 캠프 전략 전문가입니다.
아래 데이터를 바탕으로 {candidate_name} 후보의 유세 전략 리포트를 작성해주세요.

## 유세지 스코어 상위 {len(top_spots)}곳
{spot_lines}

## 미산정 유세지
{len(unscored)}곳 (아직 스코어 데이터 없음)

---
다음 항목으로 리포트를 작성해주세요:

1. **핵심 요약** (3줄 이내)
2. **최우선 유세지 TOP 3** — 각각 방문을 권장하는 이유
3. **시간대별 유세 전략** — 오전/오후/저녁 배분
4. **주의 사항** — 방문 패널티가 높은 지역, 데이터 보완 필요 지역
5. **다음 액션 아이템** — 구체적인 실행 계획 3가지

리포트는 한국어로, 실무 담당자가 바로 활용할 수 있도록 구체적으로 작성해주세요."""


class ReportService:
    def __init__(self):
        self._client: anthropic.AsyncAnthropic | None = None

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        if self._client is None:
            self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def generate(
        self,
        db: AsyncSession,
        candidate_name: str = "후보",
    ) -> str:
        """전략 리포트 생성 (전체 텍스트 반환)"""
        if not settings.anthropic_api_key:
            return "ANTHROPIC_API_KEY가 설정되지 않았습니다."

        result = await db.execute(select(CampaignSpot))
        spots = list(result.scalars().all())

        if not spots:
            return "등록된 유세지가 없습니다. 먼저 유세지를 등록하고 스코어를 갱신해주세요."

        prompt = _build_prompt(spots, candidate_name)

        message = await self.client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    async def generate_stream(
        self,
        db: AsyncSession,
        candidate_name: str = "후보",
    ) -> AsyncIterator[str]:
        """전략 리포트 스트리밍 생성"""
        if not settings.anthropic_api_key:
            yield "ANTHROPIC_API_KEY가 설정되지 않았습니다."
            return

        result = await db.execute(select(CampaignSpot))
        spots = list(result.scalars().all())

        if not spots:
            yield "등록된 유세지가 없습니다."
            return

        prompt = _build_prompt(spots, candidate_name)

        async with self.client.messages.stream(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text


report_service = ReportService()
