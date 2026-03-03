BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

# Title
Training Feedback Architecture

## Scope
Expert review çıktılarının dataset kürasyonuna, model değerlendirmesine ve release gate sürecine akışını tanımlar.

## Owners
- ML Platform Lead
- Expert Operations Lead
- Security Engineer

## Last updated
2026-03-03

## SSOT references
- KR-070 (Worker Isolation — AI izolasyonu)
- KR-071 (One-way Data Flow)
- KR-018 / KR-082 (Radiometric Calibration + Spektral Kapasite)
- KR-081 (Contract-First / Schema Gates)
- KR-072 (Dataset Lifecycle — training data provenance)

## Feedback loop
1. Expert review sonucu etiketlenir.
2. Dataset curation pipeline adayları toplar.
3. Model eval metrikleri hesaplanır.
4. Release gate kararı verilir (offline -> online).

## Boundary controls
- AI worker izole çalışır; inbound kapalı, job yalnızca queue ile alınır (KR-070).
- Veri akışı tek yönlüdür; sonuçlar platforma türev olarak döner (KR-071).
- Ham veri işleminde calibration hard gate korunur (KR-018/KR-082).
- Dataset kanıt zinciri (manifest/hash/signature) training data provenance için korunur (KR-072).
- Platforma dönüş yalnızca tanımlı şema ile yapılır (KR-081).

## Operate
- Her model sürümü için lineage kaydı tutulur.
- Gating sonucu auditlenir.
- Başarısız eval durumunda otomatik rollback uygulanır.

## Observability
- `dataset_acceptance_ratio`
- `model_eval_pass_rate`
- `release_gate_block_total`

## Failure modes
- Düşük veri kalitesi -> curation reject.
- Model drift -> online rollout durdurma.
- Yetkisiz model erişimi -> anında revoke + incident.

## Checklists
### Preflight
- Veri kaynağı ve etiket kalite eşiği doğrulandı.
- Gating kriterleri sürümle birlikte kaydedildi.

### Operate
- Eval ve drift metrikleri izleniyor.
- Rollout kararları audit dashboard’da kayıtlı.

### Postmortem
- Geri alınan sürümün kök nedeni raporlandı.
- Koruma stratejisi güncellemesi yapıldı.

## Related docs
- `docs/security/model_protection_strategy.md`
- `docs/architecture/expert_portal_design.md`
- `docs/views/VIEW_SDLC.md`
