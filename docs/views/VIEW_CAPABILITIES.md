BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

# Title
VIEW: Platform Capabilities

## Scope
Ana ürün kabiliyetlerini giriş/çıkış/sınır/KR referansı ile listeler.

## Owners
- Product Architect
- Platform Owner

## Last updated
2026-03-03

## SSOT references
- KR-015 (Pilot Kapasite/Planlama)
- KR-018 / KR-082 (Radiometric Calibration + Spektral Kapasite)
- KR-033 (Ödeme + Manuel Onay)
- KR-081 (Contract-First / Schema Gates)
- KR-070–KR-073 (Security & Isolation)
- KR-084 (Termal Veri İşleme)

## Capability map
### Calibration & QC gate
- Input: mission payload, calibration record, QC report
- Output: analysis eligibility signal
- Boundary: gate geçmeden analysis başlatılmaz
- KR: KR-018

### Payment processing
- Input: payment intent, receipt
- Output: approved/paid veya rejected state
- Boundary: manuel onay + audit zorunlu
- KR: KR-033

### Weekly planning
- Input: subscription demand, field workload, weather signal
- Output: weekly assignments, reschedule actions
- Boundary: kapasite ve çoklu pilot kuralı
- KR: KR-015

### Spektral kapasite algılama & graceful degradation
- Input: drone bant sınıfı (BASIC_4BAND / EXTENDED_5BAND / THERMAL)
- Output: uyarlanmış indeks haritaları ve raporlama derinliği
- Boundary: eksik bant → analiz durdurulmaz, kapsamı daraltılır
- KR: KR-018/KR-082

### Termal veri işleme (sulama stresi)
- Input: LWIR (8–14 μm) bant, canopy sıcaklık
- Output: CWSI haritası, sulama stresi uyarısı
- Boundary: termal bant yoksa bu katman atlanır (graceful degradation)
- KR: KR-084

### Dataset lifecycle & chain of custody
- Input: SD kart verileri, manifest, hash
- Output: doğrulanmış dataset (9 durumlu state machine)
- Boundary: hash mismatch / AV fail → REJECTED_QUARANTINE
- KR: KR-072, KR-073

### Expert review
- Input: analysis artifacts
- Output: reviewed labels, feedback events
- Boundary: RBAC + audit + PII minimizasyonu
- KR: KR-081, KR-063, KR-066

### SLA dashboard
- Input: latency/error/event telemetry
- Output: breach summary, breach list
- Boundary: observability veri bütünlüğü + correlation_id
- KR: KR-081, KR-028

## Checklists
### Preflight
- Capability sınırları güncel.
- Giriş/çıkış alanları API contract ile uyumlu.

### Operate
- Capability bazlı metrikler izleniyor.
- Sınır ihlalleri alarmlanıyor.

### Postmortem
- Yeni öğrenimler capability haritasına işlendi.
- Sahiplikler güncellendi.

## Related docs
- `docs/api/openapi.yaml`
- `docs/architecture/subscription_scheduler_design.md`
- `docs/architecture/data_lifecycle_transfer.md`
- `docs/TARLAANALIZ_SSOT_v1_2_0.txt`
