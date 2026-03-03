BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

# Title
Clean Architecture (Platform Baseline)

## Scope
Katman sınırları, bağımlılık yönleri ve API yüzeyi kuralını tanımlar.

## Owners
- Staff Backend Architect
- Domain Lead

## Last updated
2026-03-03

## SSOT references
- KR-081 (Contract-First / Schema Gates)
- KR-018 / KR-082 (Radiometric Calibration + Spektral Kapasite)
- KR-033 (Ödeme + Manuel Onay)
- KR-070 (Worker Isolation — katman izolasyonu)
- KR-071 (One-way Data Flow)

## Layer model
- `core`: entity/value object/domain policy.
- `application`: use-case, orchestrator, port arayüzleri.
- `presentation`: `src/presentation/api` tek dış API yüzeyi.
- `infrastructure`: DB, queue, storage, external gateway adapter.

## Dependency rule
- Dıştan içe bağımlılık serbest, içeriden dışa bağımlılık yalnızca port üzerinden.
- `presentation -> application -> core`.
- `infrastructure` yalnızca port implement eder.

## Contract-first
- OpenAPI/şema değişmeden handler/use-case davranışı değiştirilmez (KR-081).
- Request/response biçimi contract sürümüne bağlıdır.

## Anti-patterns
- `core` içinde framework import.
- `presentation` içinde SQL/business rule.
- `infrastructure` içinde domain kararının gömülmesi.
- `src/api` gibi ikinci API yüzeyi açılması.

## Verify
- Katmanlar arası import lint.
- Use-case birim testleri.
- API contract testleri.

## Checklists
### Preflight
- Değişiklik katman etkisi çıkarıldı.
- Port sözleşmeleri güncellendi.

### Operate
- Contract uyumsuzluğu için 4xx/5xx trendleri izleniyor.
- Integration adapter hata oranları izleniyor.

### Postmortem
- Sınır ihlali yapan kod refactor edildi.
- Mimari karar kaydı güncellendi.

## Related docs
- `docs/api/openapi.yaml`
- `docs/architecture/event_driven_design.md`
- `docs/views/VIEW_SDLC.md`
