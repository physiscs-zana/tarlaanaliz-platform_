BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

# Title
Event-Driven Design Notes

## Scope
Domain/integration/audit event ayrımı, idempotency ve correlation id propagasyonunu tanımlar.

## Owners
- Backend Architect
- Integration Lead

## Last updated
2026-03-03

## SSOT references
- KR-033 (Ödeme + Manuel Onay)
- KR-081 (Contract-First / Schema Gates)
- KR-072 (Dataset Lifecycle — event-driven state machine)
- KR-070 (Worker Isolation — job dispatch events)

## Event types
- Domain events: iç süreç geçişleri (örn. payment state update).
- Integration events: dış sistem entegrasyonu için yayınlanan olaylar.
- Audit events: değişmez iz kayıtları.

## Idempotency
- Tüm komut endpointlerinde `idempotency_key` desteklenir.
- Aynı anahtarla gelen tekrar isteklerde deterministic yanıt döner.

## Correlation id propagation
- Girişte `X-Correlation-ID` okunur/üretilir.
- Event payload ve log satırlarında taşınır.
- Runbook analizlerinde temel iz sürme anahtarıdır.

## Outbox (optional)
- Transactional outbox, DB commit sonrası güvenli publish için önerilir.
- Re-delivery durumunda consumer idempotent olmalıdır.

## Failure modes
- Consumer duplicate processing -> idempotency store.
- Outbox backlog -> queue alarm + backpressure.
- Correlation id kaybı -> observability gap alarmı.

## Example masked log
```text
ts=2026-02-18T11:10:00Z event=payment.approval.pending correlation_id=corr_7f1... subject=usr_123
```

## Checklists
### Preflight
- Event şema sürümü belirlendi.
- Idempotency key davranışı test edildi.

### Operate
- Queue lag metrikleri izleniyor.
- Correlation id kapsama oranı izleniyor.

### Postmortem
- Duplicate veya kayıp event kök neden analizi tamamlandı.
- Şema veya consumer guard kuralları güncellendi.

## Related docs
- `docs/TARLAANALIZ_SSOT_v1_2_0.txt` (KR-033 ödeme akışı kanonik kaynağı)
- `docs/api/openapi.yaml`
- `docs/runbooks/incident_response_payment_timeout.md`
- `docs/architecture/data_lifecycle_transfer.md`
