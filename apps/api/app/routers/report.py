"""전략 리포트 API"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.report import report_service

router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("")
async def generate_report(
    candidate_name: str = "후보",
    llm: str = "claude",
    db: AsyncSession = Depends(get_db),
):
    """전략 리포트 생성. llm: claude | gpt | gemini"""
    content = await report_service.generate(db, candidate_name, llm)
    return {"data": {"report": content, "llm": llm}, "error": None, "meta": {}}


@router.post("/stream")
async def generate_report_stream(
    candidate_name: str = "후보",
    llm: str = "claude",
    db: AsyncSession = Depends(get_db),
):
    """전략 리포트 스트리밍. llm: claude | gpt | gemini"""
    async def event_stream():
        async for chunk in report_service.generate_stream(db, candidate_name, llm):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain; charset=utf-8")
