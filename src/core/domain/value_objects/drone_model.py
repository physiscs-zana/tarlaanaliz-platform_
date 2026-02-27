# PATH: src/core/domain/value_objects/drone_model.py
# DESC: DroneModel VO; drone model + sensor band dogrulama (KR-030).

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar


class DroneModelError(Exception):
    """DroneModel domain invariant ihlali."""


# KR-018: Analiz icin minimum gerekli bandlar
REQUIRED_BANDS: frozenset[str] = frozenset({"green", "red", "red_edge", "nir"})


@dataclass(frozen=True)
class DroneModel:
    """Drone modeli deger nesnesi (KR-030).

    Immutable (frozen=True); olusturulduktan sonra degistirilemez.
    Domain core'da dis dunya erisimi yoktur (IO, log yok).

    SSOT'a gore desteklenen drone/sensor kombinasyonlari:
    - DJI Mavic 3M (birincil/onerilen, goreli radyometri)
    - DJI Matrice 350 RTK + Sentera 6X
    - WingtraOne Gen II + MicaSense RedEdge-P
    - Parrot Anafi USA + Sequoia+
    - AgEagle eBee X + Altum-PT

    Invariants:
    - model_id bos olamaz.
    - manufacturer bos olamaz.
    - bands en az REQUIRED_BANDS icermeli (KR-018/KR-030).
    """

    model_id: str
    manufacturer: str
    model_name: str
    sensor: str
    bands: tuple[str, ...]
    min_gsd_cm: float
    radiometry_type: str  # "relative" | "absolute"
    phase: int = 1

    # Gecerli radyometri tipleri
    _VALID_RADIOMETRY: ClassVar[frozenset[str]] = frozenset({"relative", "absolute"})

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise DroneModelError("model_id bos olamaz")
        if not isinstance(self.manufacturer, str) or not self.manufacturer.strip():
            raise DroneModelError("manufacturer bos olamaz")
        if not isinstance(self.bands, tuple):
            object.__setattr__(self, "bands", tuple(self.bands))
        if self.radiometry_type not in self._VALID_RADIOMETRY:
            raise DroneModelError(
                f"Gecersiz radiometry_type: '{self.radiometry_type}'. "
                f"Gecerli degerler: {sorted(self._VALID_RADIOMETRY)}"
            )

    @property
    def band_set(self) -> frozenset[str]:
        """Band listesini frozenset olarak dondurur."""
        return frozenset(self.bands)

    def has_required_bands(self) -> bool:
        """KR-018: Minimum band gereksinimini kontrol eder."""
        return REQUIRED_BANDS.issubset(self.band_set)

    @property
    def missing_required_bands(self) -> frozenset[str]:
        """Eksik zorunlu bandlari dondurur."""
        return REQUIRED_BANDS - self.band_set

    def supports_thermal(self) -> bool:
        """Termal band destegi var mi?"""
        return "thermal" in self.band_set

    @property
    def is_absolute_radiometry(self) -> bool:
        """Mutlak radyometrik kalibrasyon destegi."""
        return self.radiometry_type == "absolute"

    def to_dict(self) -> dict[str, Any]:
        """Serilestirme icin dict donusumu."""
        return {
            "model_id": self.model_id,
            "manufacturer": self.manufacturer,
            "model_name": self.model_name,
            "sensor": self.sensor,
            "bands": list(self.bands),
            "min_gsd_cm": self.min_gsd_cm,
            "radiometry_type": self.radiometry_type,
            "phase": self.phase,
        }

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.model_name} ({self.sensor})"

    def __repr__(self) -> str:
        return f"DroneModel(model_id='{self.model_id}', manufacturer='{self.manufacturer}')"
