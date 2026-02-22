# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
# KR-081: Contract-first test fixture configuration; domain entity fixtures used for explicit field assertions.
"""
Amaç: Pytest global fixtures ve test configuration.
Sorumluluk: Bağlamına göre beklenen sorumlulukları yerine getirir; SSOT v1.0.0 ile uyumlu kalır.
Girdi/Çıktı (Contract/DTO/Event): N/A
Güvenlik (RBAC/PII/Audit): N/A
Hata Modları (idempotency/retry/rate limit): N/A
Observability (log fields/metrics/traces): N/A
Testler: N/A
Bağımlılıklar: N/A
Notlar/SSOT: Tek referans: SSOT v1.0.0. Aynı kavram başka yerde tekrar edilmez.
"""

from __future__ import annotations

import importlib.util
from typing import Any

pytest_plugins = ["tests.fixtures.domain_fixtures"]


def pytest_addoption(parser: Any) -> None:
    parser.addini("asyncio_mode", "pytest-asyncio compatibility option")

    if importlib.util.find_spec("pytest_cov") is None:
        parser.addoption("--cov", action="store", default=None)
        parser.addoption("--cov-report", action="append", default=[])
