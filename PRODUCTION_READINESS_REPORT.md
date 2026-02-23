# TarlaAnaliz Platform — Production Readiness Report

**Tarih:** 2026-02-23
**Durum:** ❌ CANLIYA ALINMAYA HAZIR DEĞİL
**Risk Seviyesi:** YÜKSEK

---

## Yönetici Özeti

GitHub Actions'da testlerin yeşil görünmesi, platformun canlıya alınmaya hazır olduğu anlamına **gelmiyor**. Kapsamlı bir inceleme sonucunda, CI pipeline'ının önemli bir kısmının sahte (stub/echo) adımlardan oluştuğu, "integration" ve "e2e" testlerinin gerçek entegrasyon testi yapmadığı, ve canlı ortamda doğrudan sömürülebilecek **kritik güvenlik açıkları** bulunduğu tespit edilmiştir.

Aşağıda bulgular 4 kategoride sunulmaktadır:

| Kategori | Kritik | Yüksek | Orta | Düşük |
|----------|--------|--------|------|-------|
| Güvenlik | 3 | 5 | 3 | 1 |
| Test & CI/CD | 2 | 4 | 2 | 0 |
| Altyapı & Dağıtım | 1 | 3 | 2 | 2 |
| Frontend | 1 | 3 | 3 | 1 |
| **TOPLAM** | **7** | **15** | **10** | **4** |

---

## 1. KRİTİK BULGULAR (Canlıya Almadan Önce Mutlaka Çözülmeli)

### 🔴 KRTK-1: Auth Endpoint'inde Hardcoded Demo Kimlik Bilgileri

**Dosya:** `src/presentation/api/v1/endpoints/auth.py`

Auth endpoint'i, `+905555555555` telefon numarası ve `1234` PIN ile giriş yapılmasına izin veren **in-memory sahte bir auth servisi** kullanmaktadır. Bu servis **varsayılan dependency** olarak bağlanmıştır ve gerçek bir auth servisi enjekte etmek için bir mekanizma yoktur. Canlıya bu şekilde çıkılırsa, herkes demo kimlik bilgileriyle sisteme girebilir.

**Düzeltme:** Gerçek telefon + OTP doğrulama servisi (NetGSM/Twilio entegrasyonu) implement edilmeli. In-memory stub yalnızca `APP_ENV=development` ile sınırlandırılmalı.

---

### 🔴 KRTK-2: JWT Secret Varsayılan Değerle Çalışıyor

**Dosyalar:** `src/infrastructure/config/settings.py`, `src/presentation/api/settings.py`

İki ayrı JWT secret tanımı var:
- `TARLA_JWT_SECRET_KEY` → varsayılan: `"CHANGE-ME-IN-PRODUCTION"`
- `API_JWT_SECRET` → varsayılan: `"dev-only-secret"`

Her ikisi de production ortamında override edilmediğinde uygulama **hatasız başlar** ve bilinen bir secret ile JWT üretir. Bu, herhangi bir saldırganın geçerli JWT token oluşturmasına olanak tanır.

**Düzeltme:** `@model_validator` ile production ortamında varsayılan secret kullanılırsa uygulama başlatılmasını engelleyen bir guard eklenmeli. İki farklı settings sistemi birleştirilmeli.

---

### 🔴 KRTK-3: CORS Varsayılan `*` (Wildcard)

**Dosya:** `src/infrastructure/config/settings.py` (satır 50), `src/presentation/api/settings.py` (satır 47)

CORS origin varsayılan olarak `*` (tüm domainler). Production ortamında override edilmezse, herhangi bir domain'den API çağrısı yapılabilir.

**Düzeltme:** Varsayılan değer boş liste olmalı. Production'da açık origin listesi zorunlu kılınmalı.

---

### 🔴 KRTK-4: Integration/E2E Testleri Gerçek Entegrasyon Testi Yapmıyor

**Dizin:** `tests/integration/`, `tests/e2e/`

"Integration" testleri:
- `test_field_repository.py` ve `test_mission_repository.py` → test dosyası içinde tanımlanan **in-memory fake repository** test ediyor, gerçek PostgreSQL bağlantısı yok
- `test_event_bus.py` → domain event serialization testi, gerçek RabbitMQ yok
- `test_api_*.py` → domain entity'leri fixture üzerinden test ediyor, HTTP endpoint çağrısı yok
- Tüm E2E testleri domain method'ları doğrudan çağırıyor, HTTP client yok

**Sonuç:** Gerçek veritabanı, message broker veya HTTP endpoint'i ile sıfır entegrasyon testi var.

---

### 🔴 KRTK-5: CI/CD Pipeline Büyük Oranda Sahte

**Dizin:** `.github/workflows/`

| Adım | İddia | Gerçek |
|------|-------|--------|
| Docker Build (`deploy-staging.yml`) | Image build & push | `echo "Docker build would run here"` |
| Staging Deploy | Staging'e deploy | 4 adet `echo` komutu |
| Migration Check (`ci.yml`) | Migration chain doğrulama | Sadece dosya isimleri listeler |
| Frontend Unit Test | Jest coverage | `console.log('Unit test suite is not configured yet')` |
| Frontend A11y Test | Erişilebilirlik testi | `console.log('Accessibility suite is not configured yet')` |
| pip-audit | Güvenlik taraması | `|| echo "Audit completed"` — asla fail etmez |
| Lighthouse | Performance audit | `|| echo "Lighthouse warnings only"` — hata yutulur |
| Ruff Format | Kod format kontrolü | Sadece **tek bir dosya** kontrol eder |

**Production deployment pipeline hiç mevcut değil.**

---

### 🔴 KRTK-6: Alembic Migration Zinciri Kırık

**Dosyalar:** `alembic/versions/xxxx_kr015_mission_segments.py`, `xxxx_kr015_seasonal_reschedule_tokens.py`

İki migration dosyası `xxxx_` prefix'i ile bırakılmış (timestamp atanmamış). Bu dosyalar migration zincirinde "multiple heads" oluşturarak `alembic upgrade head` komutunun başarısız olmasına neden olabilir.

**Düzeltme:** Bu migration'lara uygun timestamp verilmeli ya da tamamen kaldırılmalı. `alembic heads` ile zincir bütünlüğü doğrulanmalı.

---

### 🔴 KRTK-7: Frontend %55-60 Stub Dosyalardan Oluşuyor

Frontend'de:
- 26/45 sayfa `PlaceholderPage` (null render)
- 30 feature component `export {}` stub'ı
- 14 hook dosyası boş
- Sentry config stub (SDK kurulu değil)
- i18n JSON dosyaları boş
- Jest kurulu değil, sıfır unit test
- ESLint tüm `.ts/.tsx` dosyalarını **ignore** ediyor

---

## 2. YÜKSEK SEVİYE BULGULAR

### 🟠 YÜK-1: `/health` Endpoint'i Sahte
`main.py`'deki `/health` her zaman `{"status": "ok"}` döndürür. Mevcut `HealthChecker` sınıfı (DB, Redis, RabbitMQ kontrolü yapan) hiçbir yere bağlanmamış. Docker HEALTHCHECK bu endpoint'i kullanıyor — veritabanı çökse bile container "healthy" görünür.

### 🟠 YÜK-2: Rate Limiter Sadece In-Memory
Rate limiter `InMemorySlidingWindowStore` kullanıyor. Redis adapter'ı TODO stub. Dockerfile'da 4 worker tanımlı — her worker bağımsız rate limit state'i tutuyor. Saldırgan efektif olarak 4x rate limit elde eder.

### 🟠 YÜK-3: İki Ayrı Settings Sistemi
`src/infrastructure/config/settings.py` (Pydantic, `TARLA_` prefix) ve `src/presentation/api/settings.py` (dataclass, `os.getenv`) aynı kavramlar için farklı env var isimleri kullanıyor. JWT secret, CORS, debug mode gibi kritik ayarlar iki yerde farklı isimlerle tanımlı.

### 🟠 YÜK-4: `/docs`, `/redoc`, `/openapi.json` Varsayılan Açık
Production'da API dokümantasyon endpoint'leri tüm API yüzeyini açığa çıkarır. Environment-based disable mekanizması yok.

### 🟠 YÜK-5: Structlog/Logging Konfigürasyonu Yok
`structlog.configure()` çağrısı yok. PII scrubbing processor'ı yok. Hata handler'ları veya ORM debug modu hassas verileri log'lara yazabilir.

### 🟠 YÜK-6: Frontend Auth Middleware JWT Doğrulamıyor
`web/src/middleware.ts` cookie'deki `ta_token` ve `ta_role` değerlerini olduğu gibi güveniyor. Bir kullanıcı tarayıcıda `ta_role=admin` cookie'si oluşturarak admin paneline erişebilir.

### 🟠 YÜK-7: Güvenlik Header'ları Eksik (Frontend)
`next.config.mjs`'de CSP, X-Frame-Options, X-Content-Type-Options, HSTS, Referrer-Policy header'ları tanımlı değil.

### 🟠 YÜK-8: `pytest.skip` SyntaxError Maskeliyor
3 test dosyasında application modülü import edilirken SyntaxError oluşursa test **skip** ediliyor, **fail** etmiyor. Production kodu bozuk olsa bile CI yeşil kalır.

---

## 3. CI'DA "YEŞİL" GÖRÜNME NEDENLERİ

Testlerin yeşil görünmesinin teknik açıklaması:

1. **Backend CI sadece unit test çalıştırıyor** — integration ve e2e testleri `--ignore` ile açıkça hariç tutuluyor
2. **Unit testler gerçekten iyi yazılmış** (~85% anlamlı) — domain logic'i doğru test ediyorlar
3. **Ancak integration/e2e testleri çalıştırılmadığı için** gerçek PostgreSQL, Redis, RabbitMQ, HTTP endpoint entegrasyonu hiç test edilmiyor
4. **Frontend unit test tamamen sahte** — `console.log` çıktısı, exit code 0
5. **Güvenlik taramaları asla fail etmiyor** — `|| echo` ile hata yutma
6. **Migration kontrolü** sadece dosya varlığını kontrol ediyor

---

## 4. POZİTİF BULGULAR (Yapılan İyi İşler)

Tamamen negatif bir tablo değil. Mimari temeller sağlam:

| Alan | Durum |
|------|-------|
| Clean Architecture + CQRS katmanlama | ✅ Doğru uygulanmış |
| Domain entity'lerde iş kuralları | ✅ State machine, validation, invariant'lar |
| Unit test kalitesi (domain) | ✅ %85 anlamlı, gerçek iş mantığı test eden |
| Middleware testleri (JWT, CORS, Rate Limit, Anomaly) | ✅ Çok iyi test edilmiş |
| Docker multi-stage build, non-root user | ✅ Doğru |
| SecretStr kullanımı | ✅ Hassas alanlar için |
| PII-aware domain modelleme | ✅ Encryption, masking |
| SSOT/KR governance sistemi | ✅ Disiplinli belgeleme |
| Pre-commit hooks (secret detection, lint) | ✅ Aktif |
| API presentation testleri (TestClient) | ✅ Gerçek API layer testi |

---

## 5. CANLIYA ALMA YOLCULUĞU — ÖNERİLEN ADIMLAR

### Faz 1: Güvenlik Kritikleri (BLOCKER)
- [ ] Hardcoded auth stub'ı kaldır, gerçek OTP servisi bağla
- [ ] JWT secret için production startup guard ekle
- [ ] CORS wildcard'ı kaldır, explicit origin zorunlu kıl
- [ ] İki settings sistemini birleştir
- [ ] Alembic migration zincirini düzelt

### Faz 2: Gerçek Entegrasyon Testi
- [ ] Testcontainers ile PostgreSQL integration testleri
- [ ] RabbitMQ event bus integration testleri
- [ ] HTTP endpoint integration testleri (TestClient + gerçek DB)
- [ ] CI'da integration testlerini aktif et

### Faz 3: CI/CD Pipeline Gerçekleştirme
- [ ] Docker build'i CI'da çalıştır
- [ ] Migration validation'ı gerçek `alembic upgrade head` ile yap
- [ ] Staging deployment pipeline'ını implement et
- [ ] pip-audit ve Lighthouse'dan `|| echo` kaldır
- [ ] Production deployment pipeline oluştur

### Faz 4: Production Altyapı
- [ ] `/health` endpoint'ine `HealthChecker` bağla
- [ ] Redis-backed rate limiter implement et
- [ ] Structlog konfigürasyonu ve PII processor ekle
- [ ] Production'da `/docs`, `/redoc` kapat
- [ ] Security header'ları ekle (CSP, HSTS, X-Frame-Options)

### Faz 5: Frontend Tamamlama
- [ ] Placeholder sayfaları implement et veya kaldır
- [ ] Jest kur, component unit testleri yaz
- [ ] Frontend auth middleware'e JWT doğrulama ekle
- [ ] Sentry entegrasyonunu gerçekleştir
- [ ] ESLint'i TypeScript dosyaları için aktif et

---

## Sonuç

**"Testler yeşil" ≠ "Canlıya hazır."**

Bu projede testlerin yeşil olması, yazılan unit testlerin kaliteli olmasından kaynaklanıyor — bu gerçekten iyi bir şey. Ancak CI pipeline'ı, integration/E2E test coverage'ı ve güvenlik konfigürasyonu production seviyesinde değil. Özellikle hardcoded auth credentials ve JWT secret varsayılanları, canlıya alınması halinde **doğrudan sömürülebilecek güvenlik açıklarıdır**.

Faz 1'deki güvenlik kritiklerinin çözülmesi, canlıya almanın **minimum ön koşuludur**.
