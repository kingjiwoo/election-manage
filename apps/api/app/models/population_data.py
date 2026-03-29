from datetime import datetime
from sqlalchemy import Float, String, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PopulationData(Base):
    """서울시 생활인구 수집 데이터"""

    __tablename__ = "population_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    district_code: Mapped[str] = mapped_column(String(10), index=True)   # 행정동 코드
    district_name: Mapped[str] = mapped_column(String(100))
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    total_population: Mapped[int | None] = mapped_column(Integer)
    male_population: Mapped[int | None] = mapped_column(Integer)
    female_population: Mapped[int | None] = mapped_column(Integer)

    # 연령대별 (10대~60대+)
    age_10s: Mapped[int | None] = mapped_column(Integer)
    age_20s: Mapped[int | None] = mapped_column(Integer)
    age_30s: Mapped[int | None] = mapped_column(Integer)
    age_40s: Mapped[int | None] = mapped_column(Integer)
    age_50s: Mapped[int | None] = mapped_column(Integer)
    age_60s_plus: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CongestionData(Base):
    """Tmap 실시간 혼잡도 수집 데이터"""

    __tablename__ = "congestion_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    spot_id: Mapped[int] = mapped_column(index=True)   # CampaignSpot.id 참조
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    congestion_level: Mapped[int | None] = mapped_column(Integer)   # 1~5
    congestion_score: Mapped[float | None] = mapped_column(Float)   # 정규화 0~1

    raw_data: Mapped[str | None] = mapped_column(String(2000))  # JSON 원본

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
