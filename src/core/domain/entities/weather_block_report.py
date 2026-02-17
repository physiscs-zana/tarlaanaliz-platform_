# PATH: src/core/domain/entities/weather_block_report.py
# DESC: WeatherBlockReport; hava nedeniyle ucus iptal kanit/akis modeli.
# SSOT: KR-015-5 (hava engeli reschedule token tuketmez)
"""
WeatherBlockReport domain entity.

Hava engeli (Weather Block) / force majeure nedeniyle yapilan ertelemeler
reschedule token TUKETMEZ; sistem otomatik yeniden planlar ve audit log'a yazar
(KR-015-5).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeatherBlockReport:
    """Hava kosulu nedeniyle ucus engeli raporu.

    * KR-015-5 -- Weather Block nedeniyle erteleme reschedule token tuketmez.
    * Sistem otomatik yeniden planlama yapar ve audit log'a yazar.
    """

    weather_block_id: uuid.UUID
    mission_id: uuid.UUID
    field_id: uuid.UUID
    reported_at: datetime
    reason: str  # e.g. "wind_speed_exceeded", "rain", "fog"
    created_at: datetime
    block_start: datetime | None = None
    block_end: datetime | None = None
    notes: str | None = None
    resolved: bool = False

    # ------------------------------------------------------------------
    # Invariants
    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        if not self.reason or not self.reason.strip():
            raise ValueError("reason is required for weather block report")
