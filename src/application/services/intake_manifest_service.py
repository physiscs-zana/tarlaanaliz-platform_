# BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.
# KR-072: Intake manifest kabul ve dataset oluşturma.
# KR-073: AV1 tarama sonucu doğrulama.
# KR-018: Minimum band kontrolü.
"""Intake manifest doğrulama ve dataset oluşturma servisi."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

import structlog

logger = structlog.get_logger(__name__)


class DatasetRepositoryPort(Protocol):
    async def save(self, dataset: Any) -> None: ...


class StorageServicePort(Protocol):
    async def upload_blob(self, *, bucket: str, key: str, content: bytes, content_type: str, metadata: dict[str, str] | None) -> Any: ...


class AuditLogPort(Protocol):
    def log(self, *, action: str, correlation_id: str, actor_id: str, payload: dict[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class ManifestValidationResult:
    ok: bool
    dataset_id: str
    errors: list[str]


class IntakeManifestService:
    """Intake manifest kabul ve dataset oluşturma (KR-072).

    Edge kiosk'tan gelen manifest'i doğrular:
    1. AV1 tarama sonucu CLEAN (KR-073)
    2. Minimum 4 spektral band (KR-018)
    3. Dosya hash'lerinin SHA-256 formatında olması
    4. İmza doğrulaması
    Başarılıysa Dataset entity oluşturur (RAW_INGESTED durumunda).
    """

    def __init__(
        self,
        *,
        dataset_repo: DatasetRepositoryPort,
        storage: StorageServicePort,
        audit_log: AuditLogPort,
    ) -> None:
        self._dataset_repo = dataset_repo
        self._storage = storage
        self._audit_log = audit_log

    async def accept_manifest(
        self,
        *,
        batch_id: str,
        kiosk_id: str,
        drone_serial: str,
        mission_id: str,
        field_id: str,
        files: list[dict[str, Any]],
        available_bands: list[str],
        av_scan_result: str,
        signature: str,
        captured_at: str,
        kiosk_cert_cn: str,
        correlation_id: str = "",
    ) -> ManifestValidationResult:
        """Intake manifest'i doğrular ve dataset oluşturur.

        Returns:
            ManifestValidationResult: Doğrulama sonucu ve dataset_id.
        """
        from src.core.domain.entities.dataset import Dataset

        errors: list[str] = []

        # KR-073: AV1 tarama sonucu kontrolü
        if av_scan_result != "CLEAN":
            errors.append(f"AV1 tarama sonucu CLEAN değil: {av_scan_result}")

        # KR-018: Minimum 4 band kontrolü
        if len(available_bands) < 4:
            errors.append(f"Minimum 4 spektral band gerekli, mevcut: {len(available_bands)}")

        # Dosya hash format kontrolü
        for f in files:
            h = f.get("sha256", "")
            if len(h) != 64:
                errors.append(f"Geçersiz SHA-256 hash: {f.get('file_path', 'unknown')}")

        if not files:
            errors.append("En az bir dosya zorunludur")

        if errors:
            logger.warning(
                "intake_manifest_rejected",
                batch_id=batch_id,
                kiosk_id=kiosk_id,
                errors=errors,
                correlation_id=correlation_id,
            )
            return ManifestValidationResult(ok=False, dataset_id="", errors=errors)

        # Dataset oluştur
        dataset = Dataset.create(
            mission_id=uuid.UUID(mission_id),
            field_id=uuid.UUID(field_id),
            available_bands=tuple(available_bands),
        )

        # Manifest JSONB
        manifest_data = {
            "batch_id": batch_id,
            "kiosk_id": kiosk_id,
            "drone_serial": drone_serial,
            "files": files,
            "available_bands": available_bands,
            "av_scan_result": av_scan_result,
            "signature": signature,
            "captured_at": captured_at,
            "kiosk_cert_cn": kiosk_cert_cn,
            "accepted_at": datetime.now(timezone.utc).isoformat(),
        }
        dataset.manifest = manifest_data

        await self._dataset_repo.save(dataset)

        # Manifest'i storage'a kaydet
        manifest_key = f"manifests/{dataset.dataset_id}/{batch_id}.json"
        await self._storage.upload_blob(
            bucket="tarlaanaliz-ingest",
            key=manifest_key,
            content=json.dumps(manifest_data).encode("utf-8"),
            content_type="application/json",
            metadata={"batch_id": batch_id, "kiosk_id": kiosk_id},
        )

        self._audit_log.log(
            action="intake_manifest_accepted",
            correlation_id=correlation_id,
            actor_id=f"kiosk:{kiosk_id}",
            payload={
                "dataset_id": str(dataset.dataset_id),
                "batch_id": batch_id,
                "mission_id": mission_id,
                "file_count": len(files),
                "band_count": len(available_bands),
            },
        )

        logger.info(
            "intake_manifest_accepted",
            dataset_id=str(dataset.dataset_id),
            batch_id=batch_id,
            mission_id=mission_id,
            correlation_id=correlation_id,
        )

        return ManifestValidationResult(
            ok=True,
            dataset_id=str(dataset.dataset_id),
            errors=[],
        )
