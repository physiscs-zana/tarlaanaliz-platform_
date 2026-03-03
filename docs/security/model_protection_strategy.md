BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.

# Title
Security Strategy: Model Protection

## Scope
Model varlıklarının korunması, erişim kontrolleri ve güvenli release pipeline yaklaşımını tanımlar.

## Owners
- ML Security Lead
- Platform Security Engineer

## Last updated
2026-03-03

## SSOT references
- KR-070 (Worker Isolation — AI izolasyonu)
- KR-071 (One-way Data Flow)
- KR-018 / KR-082 (Radiometric Calibration + Spektral Kapasite)
- KR-081 (Contract-First / Schema Gates)

## Protection principles
- Model edge cihazlarda dağıtılmaz.
- Ağırlıklar şifreli depolama + erişim politikasıyla korunur.
- Model erişimi servis hesabı ve kısa ömürlü kimlik bilgileriyle sınırlandırılır.

## Controls
- Artifact imzalama ve doğrulama.
- Watermarking (opsiyonel) ve misuse tespiti.
- Snapshot erişimleri için audit zorunluluğu.

## Secure pipeline (offline -> online)
1. Offline eval tamamlanır.
2. Güvenlik kontrol listesi geçilir.
3. Release gate onayı alınır.
4. Online rollout kontrollü yapılır.

## KR-018 relation
- Model pipeline’a giren verilerde calibration ve QC gate zorunludur.

## Failure modes
- Yetkisiz artifact kopyası.
- İmza doğrulama atlanması.
- Gating bypass girişimi.

## Checklists
### Preflight
- Artifact imza politikası aktif.
- Erişim rolleri güncel.

### Operate
- Model erişim logları izleniyor.
- Anomali tespitleri incident hattına bağlı.

### Postmortem
- Sızıntı/ihlalde erişimler revoke edildi.
- Koruma katmanları güncellendi.

## Related docs
- `docs/architecture/training_feedback_architecture.md`
- `docs/architecture/expert_portal_design.md`
- `docs/TARLAANALIZ_SSOT_v1_2_0.txt`
