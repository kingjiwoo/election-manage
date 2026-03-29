from datetime import datetime
from sqlalchemy import Float, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CampaignSpot(Base):
    """유세지 후보 지점"""

    __tablename__ = "campaign_spots"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String(500))
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    spot_type: Mapped[str] = mapped_column(String(50))  # apartment, station, market 등

    # 스코어링
    score: Mapped[float | None] = mapped_column(Float)
    congestion_score: Mapped[float | None] = mapped_column(Float)
    population_score: Mapped[float | None] = mapped_column(Float)
    visit_penalty: Mapped[float] = mapped_column(Float, default=0.0)

    last_visited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    score_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
