# PATH: src/infrastructure/contracts/schema_registry.py
# DESC: Contract şemalarını (JSON Schema) versiyonlu yükleyen ve cache'leyen bileşen.
"""
SchemaRegistry: versiyonlu JSON Schema yönetimi ve cache.

Domain event'leri ve DTO'lar için contract şemalarını yükler, doğrular
ve bellek içi cache'ler. Şemalar dosya sisteminden veya dict olarak
kaydedilebilir.

SSOT: tarlaanaliz_platform_tree v3.2.2 FINAL.
KR-081: contract-first tasarım; şema uyumsuzluğu erken tespit edilir.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class SchemaValidationError(Exception):
    """Şema doğrulama hatası."""


class SchemaNotFoundError(KeyError):
    """İstenen şema bulunamadı."""


class SchemaRegistry:
    """Versiyonlu JSON Schema kaydı (KR-081).

    Şemaları (schema_name, version) çifti ile indeksler.
    Bellek içi dict cache kullanır; thread-safe değildir
    (async context'te tek event loop yeterlidir).

    Kullanım:
        registry = SchemaRegistry()
        registry.register("MissionAssigned", "1.0.0", {...})
        schema = registry.get("MissionAssigned", "1.0.0")
        registry.load_directory(Path("schemas/"))
    """

    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str], dict[str, Any]] = {}

    def register(
        self,
        schema_name: str,
        version: str,
        schema: dict[str, Any],
    ) -> None:
        """Şemayı kaydet veya güncelle.

        Args:
            schema_name: Şema adı (ör: "MissionAssigned").
            version: Semantik versiyon (ör: "1.0.0").
            schema: JSON Schema dict.

        Raises:
            ValueError: Geçersiz schema_name veya version.
        """
        if not schema_name or not schema_name.strip():
            raise ValueError("schema_name boş olamaz.")
        if not version or not version.strip():
            raise ValueError("version boş olamaz.")
        key = (schema_name.strip(), version.strip())
        self._schemas[key] = schema
        logger.debug(
            "schema_registered",
            schema_name=key[0],
            version=key[1],
        )

    def get(
        self,
        schema_name: str,
        version: str,
    ) -> dict[str, Any]:
        """Cache'ten şema döner.

        Args:
            schema_name: Şema adı.
            version: Semantik versiyon.

        Returns:
            JSON Schema dict.

        Raises:
            SchemaNotFoundError: Şema bulunamadığında.
        """
        key = (schema_name.strip(), version.strip())
        try:
            return self._schemas[key]
        except KeyError:
            raise SchemaNotFoundError(
                f"Şema bulunamadı: {key[0]} v{key[1]}. Kayıtlı şemalar: {sorted(self._schemas.keys())}"
            ) from None

    def has(self, schema_name: str, version: str) -> bool:
        """Şema mevcut mu?"""
        return (schema_name.strip(), version.strip()) in self._schemas

    def list_schemas(self) -> list[tuple[str, str]]:
        """Kayıtlı tüm (schema_name, version) çiftlerini döner."""
        return sorted(self._schemas.keys())

    def list_versions(self, schema_name: str) -> list[str]:
        """Belirli bir şemanın tüm versiyonlarını döner."""
        return sorted(version for name, version in self._schemas if name == schema_name.strip())

    def load_from_file(self, file_path: Path) -> tuple[str, str]:
        """Tek bir JSON Schema dosyasını yükler.

        Desteklenen dosya adı formatları:
          - <name>.v<N>.schema.json  → (name, "v<N>")   — contracts repo standardı
          - <name>.enum.v<N>.json    → (name, "v<N>")   — enum dosyaları
          - <name>.v<N>.json         → (name, "v<N>")   — eski enum formatı

        Args:
            file_path: Şema dosyasının yolu.

        Returns:
            (schema_name, version) tuple.

        Raises:
            ValueError: Dosya adı formatı geçersizse.
            FileNotFoundError: Dosya bulunamazsa.
            json.JSONDecodeError: Geçersiz JSON.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Şema dosyası bulunamadı: {file_path}")

        stem = file_path.stem  # e.g. "field.v1.schema" or "crop_type.enum.v1" or "payment_status.v2"
        schema_name, version = self._parse_filename(stem, file_path.name)

        content = file_path.read_text(encoding="utf-8")
        schema = json.loads(content)
        self.register(schema_name, version, schema)

        return (schema_name, version)

    @staticmethod
    def _parse_filename(stem: str, original_name: str) -> tuple[str, str]:
        """Dosya adından (schema_name, version) çıkarır.

        Örnekler:
          "field.v1.schema"          → ("field", "v1")
          "crop_type.enum.v1"        → ("crop_type", "v1")
          "payment_status.v2"        → ("payment_status", "v2")
          "payment_intent.v2.schema" → ("payment_intent", "v2")
        """
        parts = stem.split(".")
        # .schema suffix'ini kaldır
        if parts and parts[-1] == "schema":
            parts = parts[:-1]
        # .enum suffix'ini kaldır (version'dan önce)
        # Şimdi son eleman version olmalı (v1, v2, vN)
        version_idx = -1
        for i, part in enumerate(parts):
            if part.startswith("v") and part[1:].isdigit():
                version_idx = i
                break
        if version_idx < 1:
            raise ValueError(
                f"Dosya adı formatı geçersiz: '{original_name}'. "
                f"Beklenen: <name>.v<N>.schema.json veya <name>.enum.v<N>.json"
            )
        schema_name = ".".join(parts[:version_idx]).replace(".enum", "")
        version = parts[version_idx]
        return (schema_name, version)

    def load_directory(self, directory: Path, *, recursive: bool = False) -> int:
        """Dizindeki tüm .json şema dosyalarını yükler.

        Args:
            directory: Şema dosyalarının bulunduğu dizin.
            recursive: True ise alt dizinleri de tarar.

        Returns:
            Yüklenen şema sayısı.

        Raises:
            FileNotFoundError: Dizin bulunamazsa.
        """
        if not directory.exists():
            raise FileNotFoundError(f"Şema dizini bulunamadı: {directory}")

        pattern = "**/*.json" if recursive else "*.json"
        count = 0
        for file_path in sorted(directory.glob(pattern)):
            try:
                self.load_from_file(file_path)
                count += 1
            except (ValueError, json.JSONDecodeError) as exc:
                logger.warning(
                    "schema_load_skipped",
                    file=str(file_path),
                    error=str(exc),
                )

        logger.info("schema_directory_loaded", directory=str(directory), count=count, recursive=recursive)
        return count

    def get_by_key(self, schema_key: str) -> dict[str, Any]:
        """schema_key ile son versiyonu döner (ContractValidatorPort uyumu).

        schema_key örnekleri: "field", "mission", "analysis_job", "payment_intent"
        En yüksek versiyon numarasına sahip şemayı döner.
        """
        matching = [
            (name, ver) for name, ver in self._schemas if name == schema_key
        ]
        if not matching:
            raise SchemaNotFoundError(
                f"Şema bulunamadı: '{schema_key}'. Kayıtlı: {sorted(set(n for n, _ in self._schemas))}"
            )
        latest = sorted(matching, key=lambda x: x[1])[-1]
        return self._schemas[latest]

    def clear(self) -> None:
        """Tüm cache'lenmiş şemaları temizler."""
        self._schemas.clear()
