# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
# KR-070: Worker tam izolasyon — inbound HTTP yasak; queue consume-only.
# KR-072: Dataset CALIBRATED_SCANNED_CENTER_OK → DISPATCHED_TO_WORKER geçişi.
# KR-018: Kalibrasyon hard gate.
"""Worker dispatch service: dataset'i worker kuyruğuna gönderir."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

import structlog

logger = structlog.get_logger(__name__)


class EventBusPort(Protocol):
    async def publish(self, event: Any) -> None: ...


class DatasetRepositoryPort(Protocol):
    async def get_by_id(self, dataset_id: uuid.UUID) -> Any: ...
    async def save(self, dataset: Any) -> None: ...


class AnalysisJobRepositoryPort(Protocol):
    async def save(self, job: Any) -> None: ...


@dataclass(frozen=True, slots=True)
class DispatchResult:
    dataset_id: str
    analysis_job_id: str
    status: str
    dispatched_at: str


class WorkerDispatchService:
    """Dataset'i analiz için worker kuyruğuna gönderir (KR-070, KR-072).

    Akış:
    1. Dataset'in CALIBRATED_SCANNED_CENTER_OK durumunda olduğunu doğrula
    2. is_ready_for_analysis kontrolü (kalibrasyon, AV raporları, hash)
    3. AnalysisJob oluştur
    4. Dataset'i DISPATCHED_TO_WORKER durumuna geçir
    5. AnalysisRequested event'i yayınla (worker consume edecek)
    """

    def __init__(
        self,
        *,
        dataset_repo: DatasetRepositoryPort,
        job_repo: AnalysisJobRepositoryPort,
        event_bus: EventBusPort,
    ) -> None:
        self._dataset_repo = dataset_repo
        self._job_repo = job_repo
        self._event_bus = event_bus

    async def dispatch_to_worker(
        self,
        *,
        dataset_id: uuid.UUID,
        crop_type: str,
        analysis_type: str = "standard",
        model_id: str = "default",
        model_version: str = "1.0",
        correlation_id: str = "",
    ) -> DispatchResult:
        """Dataset'i worker kuyruğuna gönder.

        Args:
            dataset_id: Gönderilecek dataset.
            crop_type: Ürün tipi (analiz parametresi).
            analysis_type: Analiz tipi (standard, detailed).
            model_id: YZ model kimliği.
            model_version: Model versiyonu.
            correlation_id: İzleme ID.

        Returns:
            DispatchResult: Gönderim sonucu.

        Raises:
            ValueError: Dataset analiz için hazır değilse.
            RuntimeError: Dataset bulunamazsa.
        """
        from src.core.domain.entities.analysis_job import AnalysisJob, AnalysisJobStatus
        from src.core.domain.events.analysis_events import AnalysisRequested
        from src.core.domain.value_objects.dataset_status import DatasetStatus

        dataset = await self._dataset_repo.get_by_id(dataset_id)
        if dataset is None:
            raise RuntimeError(f"Dataset bulunamadı: {dataset_id}")

        if not dataset.is_ready_for_analysis:
            raise ValueError(
                f"Dataset analiz için hazır değil. "
                f"Durum: {dataset.status}, "
                f"Kalibrasyon: {dataset.is_calibrated}, "
                f"AV1: {dataset.av1_report_uri is not None}, "
                f"AV2: {dataset.av2_report_uri is not None}, "
                f"Bantlar: {len(dataset.available_bands)}"
            )

        # AnalysisJob oluştur
        job_id = uuid.uuid4()
        band_count = len(dataset.available_bands)
        band_class = "EXTENDED_5BAND" if band_count >= 5 else "BASIC_4BAND"

        job = AnalysisJob(
            analysis_job_id=job_id,
            mission_id=dataset.mission_id,
            field_id=dataset.field_id,
            crop_type=crop_type,
            analysis_type=analysis_type,
            model_id=model_id,
            model_version=model_version,
            requires_calibrated=True,
            calibration_record_id=str(uuid.uuid4()),
            available_bands=dataset.available_bands,
            band_class=band_class,
            status=AnalysisJobStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        await self._job_repo.save(job)

        # Dataset durumunu güncelle
        dataset.transition_to(
            DatasetStatus.DISPATCHED_TO_WORKER,
            worker_job_id=job_id,
            manifest_update={"dispatched_at": datetime.now(timezone.utc).isoformat()},
        )
        await self._dataset_repo.save(dataset)

        # Event yayınla — worker bu event'i consume edecek
        event = AnalysisRequested(
            mission_id=dataset.mission_id,
            field_id=dataset.field_id,
            crop_type=crop_type,
            requires_calibrated=True,
            available_bands=dataset.available_bands,
        )
        await self._event_bus.publish(event)

        logger.info(
            "worker_dispatch_completed",
            dataset_id=str(dataset_id),
            analysis_job_id=str(job_id),
            band_class=band_class,
            correlation_id=correlation_id,
        )

        return DispatchResult(
            dataset_id=str(dataset_id),
            analysis_job_id=str(job_id),
            status="DISPATCHED_TO_WORKER",
            dispatched_at=datetime.now(timezone.utc).isoformat(),
        )
