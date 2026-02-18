# BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
"""
Amaç: Python paket başlangıcı; modül dışa aktarım (exports) ve namespace düzeni.
Sorumluluk: Python paket başlangıcı; import yüzeyini (public API) düzenler.
Girdi/Çıktı (Contract/DTO/Event): Girdi: method çağrıları. Çıktı: domain nesneleri, domain event’leri (gereken yerde).
Güvenlik (RBAC/PII/Audit): PII minimizasyonu; domain core’da dış dünya erişimi yok; audit gerektiren kararlar üst katmana taşınır.
Hata Modları (idempotency/retry/rate limit): Validation error; invariant violation; concurrency -> üst katmanda 409/Retry stratejisi.
Observability (log fields/metrics/traces): Domain core log tutmaz (tercihen); correlation_id üst katmanda taşınır.
Testler: Unit test (invariants), property-based (opsiyonel), serialization (gerekirse).
Bağımlılıklar: Sadece core/value objects ve standart kütüphane; harici IO bağımlılığı yok.
Notlar/SSOT: KR-015, KR-018, KR-033, KR-081 ile tutarlı kalır.
"""

__all__: list[str] = []
