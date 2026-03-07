# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
# KR-072: Dataset ingestion pipeline — intake manifest kabul ve dataset oluşturma.
# KR-073: İki aşamalı AV tarama gate.
# KR-071: mTLS zorunlu (middleware'de kontrol edilir).
"""Edge kiosk intake manifest ve dataset ingestion endpoint'leri."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Optional, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ingest", tags=["ingest"])


# --- Request / Response DTOs ---

class FileHashEntry(BaseModel):
    file_path: str = Field(min_length=1)
    sha256: str = Field(min_length=64, max_length=64)
    size_bytes: int = Field(gt=0)


class IntakeManifestRequest(BaseModel):
    """Edge kiosk'tan gelen intake manifest (KR-072)."""
    batch_id: str = Field(min_length=10, max_length=64)
    kiosk_id: str = Field(min_length=3, max_length=64)
    drone_serial: str = Field(min_length=3, max_length=64)
    mission_id: str = Field(min_length=1)
    field_id: str = Field(min_length=1)
    files: list[FileHashEntry] = Field(min_length=1)
    available_bands: list[str] = Field(min_length=4)
    av_scan_result: str = Field(pattern="^CLEAN$")
    signature: str = Field(min_length=1)
    captured_at: str = Field(min_length=1)


class DatasetResponse(BaseModel):
    dataset_id: str
    mission_id: str
    field_id: str
    status: str
    batch_id: str


class DatasetStatusResponse(BaseModel):
    dataset_id: str
    status: str
    updated_at: str


class DatasetListResponse(BaseModel):
    items: list[DatasetStatusResponse]


# --- Service Protocol ---

class IngestService(Protocol):
    async def accept_manifest(
        self, *, manifest: IntakeManifestRequest, kiosk_cert_cn: str, correlation_id: str
    ) -> DatasetResponse: ...

    async def get_dataset_status(self, *, dataset_id: str) -> DatasetStatusResponse: ...

    async def list_datasets_by_mission(self, *, mission_id: str) -> list[DatasetStatusResponse]: ...

    async def transition_dataset(
        self, *, dataset_id: str, target_status: str, metadata: dict[str, Any]
    ) -> DatasetStatusResponse: ...


# --- In-Memory Stub (Öncelik 3'te gerçek impl ile değiştirilecek) ---

@dataclass(slots=True)
class _InMemoryIngestService:
    async def accept_manifest(
        self, *, manifest: IntakeManifestRequest, kiosk_cert_cn: str, correlation_id: str
    ) -> DatasetResponse:
        dataset_id = str(uuid.uuid4())
        return DatasetResponse(
            dataset_id=dataset_id,
            mission_id=manifest.mission_id,
            field_id=manifest.field_id,
            status="RAW_INGESTED",
            batch_id=manifest.batch_id,
        )

    async def get_dataset_status(self, *, dataset_id: str) -> DatasetStatusResponse:
        return DatasetStatusResponse(
            dataset_id=dataset_id,
            status="RAW_INGESTED",
            updated_at="2026-03-07T00:00:00Z",
        )

    async def list_datasets_by_mission(self, *, mission_id: str) -> list[DatasetStatusResponse]:
        return []

    async def transition_dataset(
        self, *, dataset_id: str, target_status: str, metadata: dict[str, Any]
    ) -> DatasetStatusResponse:
        return DatasetStatusResponse(
            dataset_id=dataset_id,
            status=target_status,
            updated_at="2026-03-07T00:00:00Z",
        )


def get_ingest_service(request: Request) -> IngestService:
    services = getattr(request.app.state, "services", None)
    if services is not None:
        svc = services.get("ingest_service")
        if svc is not None:
            return svc
    return _InMemoryIngestService()


def _get_kiosk_cn(request: Request) -> str:
    """mTLS sertifikasından CN çıkar (middleware tarafından set edilir)."""
    mtls_info = getattr(request.state, "mtls_client_info", None)
    if mtls_info and hasattr(mtls_info, "common_name"):
        return str(mtls_info.common_name)
    return getattr(request.state, "client_cert_cn", "unknown")


def _get_corr_id(request: Request) -> str:
    return getattr(request.state, "corr_id", "")


# --- Endpoints ---

@router.post(
    "/manifests",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Intake manifest kabul et (KR-072, KR-071 mTLS zorunlu)",
)
async def accept_intake_manifest(
    request: Request,
    manifest: IntakeManifestRequest,
    service: IngestService = Depends(get_ingest_service),
) -> DatasetResponse:
    """Edge kiosk'tan intake manifest kabul eder ve dataset oluşturur.

    mTLS middleware tarafından cihaz kimliği doğrulanır (KR-071).
    AV1 tarama sonucu CLEAN olmalıdır (KR-073).
    Minimum 4 spektral band zorunludur (KR-018).
    """
    kiosk_cn = _get_kiosk_cn(request)
    corr_id = _get_corr_id(request)
    return await service.accept_manifest(
        manifest=manifest, kiosk_cert_cn=kiosk_cn, correlation_id=corr_id
    )


@router.get(
    "/datasets/{dataset_id}",
    response_model=DatasetStatusResponse,
    summary="Dataset durumunu sorgula (KR-072)",
)
async def get_dataset_status(
    dataset_id: str,
    service: IngestService = Depends(get_ingest_service),
) -> DatasetStatusResponse:
    return await service.get_dataset_status(dataset_id=dataset_id)


@router.get(
    "/datasets",
    response_model=DatasetListResponse,
    summary="Mission'a ait dataset'leri listele",
)
async def list_datasets(
    mission_id: str,
    service: IngestService = Depends(get_ingest_service),
) -> DatasetListResponse:
    items = await service.list_datasets_by_mission(mission_id=mission_id)
    return DatasetListResponse(items=items)


class TransitionRequest(BaseModel):
    target_status: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.post(
    "/datasets/{dataset_id}/transition",
    response_model=DatasetStatusResponse,
    summary="Dataset durum geçişi (KR-072 state machine)",
)
async def transition_dataset(
    dataset_id: str,
    body: TransitionRequest,
    service: IngestService = Depends(get_ingest_service),
) -> DatasetStatusResponse:
    return await service.transition_dataset(
        dataset_id=dataset_id, target_status=body.target_status, metadata=body.metadata
    )
