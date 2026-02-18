# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
"""
Amaç: Test modülü; davranış doğrulama ve regresyon engeli.
Sorumluluk: Bağlamına göre beklenen sorumlulukları yerine getirir; SSOT v1.0.0 ile uyumlu kalır.
Girdi/Çıktı (Contract/DTO/Event): N/A
Güvenlik (RBAC/PII/Audit): N/A
Hata Modları (idempotency/retry/rate limit): N/A
Observability (log fields/metrics/traces): N/A
Testler: N/A
Bağımlılıklar: N/A
Notlar/SSOT: Tek referans: SSOT v1.0.0. Aynı kavram başka yerde tekrar edilmez. KR-018 hard gate: calibrated/QC kanıtı olmadan AnalysisJob başlatılmamalıdır.
"""

from __future__ import annotations

import uuid

import pytest

from src.core.domain.entities.analysis_job import AnalysisJob, AnalysisJobStatus


def _job() -> AnalysisJob:
    return AnalysisJob(
        analysis_job_id=uuid.uuid4(),
        mission_id=uuid.uuid4(),
        field_id=uuid.uuid4(),
        crop_type="WHEAT",
        analysis_type="MULTISPECTRAL",
        model_id="model-1",
        model_version="1.0.0",
        status=AnalysisJobStatus.PENDING,
        created_at=__import__("datetime").datetime(2026, 1, 1),
        updated_at=__import__("datetime").datetime(2026, 1, 1),
    )


def test_kr018_start_fails_without_calibration() -> None:
    with pytest.raises(ValueError, match="KR-018"):
        _job().start_processing()


def test_kr018_start_succeeds_with_calibration() -> None:
    job = _job()
    job.attach_calibration(uuid.uuid4())
    job.start_processing()

    assert job.status == AnalysisJobStatus.PROCESSING
