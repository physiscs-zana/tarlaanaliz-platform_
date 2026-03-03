BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

# Title
VIEW: SDLC (Plan → Build → Test → Deploy → Operate)

## Scope
SDLC aşamalarını kontrol kapıları, observability ve runbook bağlantılarıyla gösterir.

## Owners
- Engineering Manager
- SRE Lead

## Last updated
2026-03-03

## SSOT references
- KR-018 / KR-082 (Radiometric Calibration + Spektral Kapasite)
- KR-033 (Ödeme + Manuel Onay)
- KR-081 (Contract-First / Schema Gates)
- KR-040–KR-043 (Güvenlik Kabul Kriterleri / SDLC Gates)
- KR-070–KR-073 (Security & Isolation)

## Stage view
- Plan: KR referansları ve etki analizi.
- Build: contract-first geliştirme.
- Test: API contract, gate doğrulamaları, yetki testleri.
- Deploy: rollout guard ve rollback planı.
- Operate: SLO/SLA metrikleri + runbook icrası.

## Critical gates
- Gate A (KR-018/KR-082): calibration + QC olmadan analysis yok; spektral kapasite algılaması.
- Gate B (KR-033): intent + receipt + manual approval + audit.
- Gate C (KR-081): contract uyumu olmadan release yok.
- Gate D (KR-040–043): güvenlik kabul kriterleri PR/CI/Release aşamalarında zorunlu.
- Gate E (KR-070–073): worker izolasyonu, one-way flow, AV tarama zinciri doğrulanmadan deploy yok.

## Observability hooks
- Correlation ID zorunlu.
- Endpoint bazlı 4xx/5xx ve latency trendleri.
- Incident sonrası postmortem aksiyon takibi.

## Checklists
### Preflight
- Release checklist ve gate testleri hazır.
- Runbook linkleri güncel.

### Operate
- Gate ihlali alarmları izleniyor.
- Incident akışı runbook’a göre yürütülüyor.

### Postmortem
- SDLC aşama kırılımında kök neden işlendi.
- Test veya gate boşlukları kapatıldı.

## Related docs
- `docs/runbooks/incident_response_sla_breach.md`
- `docs/runbooks/incident_response_payment_timeout.md`
- `docs/architecture/clean_architecture.md`
