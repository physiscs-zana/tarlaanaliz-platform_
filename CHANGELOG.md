# Changelog

Tum onemli degisiklikler bu dosyada belgelenir.
Format [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) standardina,
surumleme [SemVer](https://semver.org/) politikasina uyar.

SSOT Referansi: `docs/TARLAANALIZ_SSOT_v1_2_0.txt` — KR-000 surumleme politikasi.

## [Unreleased]

### Changed

- SSOT v1.0.0 → v1.2.0'a yukseltildi (`docs/TARLAANALIZ_SSOT_v1_2_0.txt`)
- docs/ altindaki 25 dosya SSOT v1.2.0 ile senkronize edildi
- Proje kok dosyalari (README, AGENTS, MANIFEST, DIRECTORY_TREE) SSOT v1.2.0 referanslari ile guncellendi
- Arsivlenen dosyalar `docs/archive/2026-02/` altina tasinmisti (LLM Brief, Playbook, eski SSOT)

### Added

- Proje iskelet yapisi (scaffold) olusturuldu (v3.2.2 agac yapisi)
- SSOT v1.2.0 dokumani (`docs/TARLAANALIZ_SSOT_v1_2_0.txt`) — 6 BOLUM + EK-SOP-SEC
- Governance Pack v1.0.0 (`docs/governance/GOVERNANCE_PACK_v1_0_0.md`)
- KR Registry navigasyon indeksi (`docs/kr/kr_registry.md`)
- ADR-001 Nine State Machine karari (`docs/adr/ADR-001-nine-state-machine.md`)
- Migration guides dizini (`docs/migration_guides/`)
- Clean Architecture katman yapisi: `src/core/`, `src/application/`, `src/infrastructure/`, `src/presentation/`
- CQRS pattern: commands + queries ayriligi
- Domain entities: User, Field, Mission, Pilot, Expert, Subscription, PaymentIntent, AnalysisJob
- Value objects: ParcelRef, Geometry, Money, MissionStatus, ConfidenceScore, CropType, Province, Role
- Domain events: Field, Mission, Payment, Subscription, Analysis, Expert lifecycle olaylari
- Domain services: CalibrationValidator, CapacityManager, MissionPlanner, PricebookCalculator, SLAMonitor
- Repository ports: 20+ repository interface tanimi
- External ports: PaymentGateway, SMSGateway, StorageService, ParcelGeometryProvider, EventBus
- Infrastructure adapters: SQLAlchemy, Redis, RabbitMQ, S3/MinIO, Cloudflare, TKGM/MEGSIS
- Alembic migration framework: 16 migration sablonu
- FastAPI endpoint iskeletleri: 15+ endpoint
- Frontend (Next.js) feature modules: subscriptions, results, expert-portal, weather-block, training-feedback
- i18n destek yapisi: tr, ar, ku
- Test scaffolding: unit, integration, e2e, performance

## [3.2.2] - 2026-02-08

### Added

- Baslangic surumu; platform tree v3.2.2 FINAL olarak sabitlendi
- KR-033 PaymentIntent tablolari ve odeme akisi migration'i
- KR-082 Kalibrasyon ve QC kayit tablolari migration'i
- WeatherBlockReport tablolari migration'i
- Frontend CI workflow (build + lint + e2e)

### Security

- KR-040/KR-041 SDLC kapilari tanimla ndi
- KR-050 Telefon + PIN kimlik modeli belirlendi
- KR-063 RBAC matrisi (12 rol) dokumante edildi
- KR-066 PII ayriligi kurallari belirlendi
- KR-070 YZ izolasyonu ve tek yonlu akis politikasi belirlendi
