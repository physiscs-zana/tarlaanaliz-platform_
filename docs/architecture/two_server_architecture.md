BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.

# Title
İki Sunucu Mimarisi — Platform Core + Data Pipeline

## Scope
Platform'un fiziksel iki sunucuya bölünme gerekçesini, bileşen yerleşimini, veritabanı
rol ayrımını, servisler arası iletişim kurallarını ve mevsimsel ölçekleme stratejisini
tanımlar. Veri akışı detayları `data_lifecycle_transfer.md`'de kanonik olarak
tanımlanmıştır; bu doküman **dağıtım topolojisini** belirler.

## Owners
- Staff Backend Architect
- Security Lead
- DevOps Lead

## Last updated
2026-03-01

## SSOT references
- KR-070 (Worker Isolation & Egress Policy)
- KR-071 (One-way Data Flow + Allowlist Yerleşimi)
- KR-072 (Dataset Lifecycle + Chain of Custody)
- KR-073 (Untrusted File Handling + AV1/AV2 + Sandbox)
- KR-081 (Contract-First / Schema Gates)
- KR-033 (Ödeme + Manuel Onay)
- KR-063 (Roller ve Yetkiler — RBAC)
- KR-050 (Kimlik Doğrulama)
- KR-018 (Radiometric Calibration Hard Gate)
- KR-030 (Drone Registry)
- KR-015 (Pilot Kapasite/Planlama)
- KR-028 (Mission Yaşam Döngüsü + SLA)
- KR-029 (YZ Eğitim Geri Bildirimi)

---

## §1 Bölme Gerekçesi

Platform, mantıksal olarak iki farklı sorumluluk alanına ayrılır. Bu ayrım üç ana
nedenle fiziksel sunucu düzeyine yükseltilmiştir:

### 1.1 Güvenlik İzolasyonu
Sunucu 2 (Data Pipeline) **güvenilmez dosyalar** işler: AV2 tarama, hash doğrulama,
sandbox dönüşüm (KR-073). Bu sunucu ele geçirilse bile kullanıcı PII verisine,
ödeme bilgilerine ve RBAC tablolarına **erişemez** (DB role ayrımı, bkz. §4).

### 1.2 Ters Orantılı Ölçekleme
- **Sunucu 1** yükü kullanıcı sayısıyla orantılıdır (API, SSR, auth) — düz büyüme.
- **Sunucu 2** yükü aktif drone sayısı ve uçuş sezonu ile orantılıdır — mevsimsel
  patlama (bkz. §8). Pipeline 3–5× büyürken Platform Core aynı kalabilir.

### 1.3 KR-071 Uyumu
SSOT [KR-071] tek yönlü veri akışını zorunlu kılar. Mantıksal ayrım, ağ katmanında
fiziksel ayrıma yükseltilerek "varsayılan reddet" (deny-by-default) güvencesi
güçlendirilmiştir: Sunucu 2'ye internet erişimi kapalıdır (KR-070).

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                         DAĞITIM TOPOLOJİSİ                              │
  │                                                                          │
  │  ┌────────────────────────┐         ┌────────────────────────┐          │
  │  │  SUNUCU 1              │         │  SUNUCU 2              │          │
  │  │  Platform Core         │         │  Data Pipeline         │          │
  │  │                        │         │                        │          │
  │  │  ● Kullanıcı-facing    │         │  ● Dosya işleme        │          │
  │  │  ● API + SSR           │         │  ● AV2 + hash verify   │          │
  │  │  ● Auth + RBAC         │         │  ● AI Worker           │          │
  │  │  ● Ödeme + SLA         │         │  ● Kalibrasyon gate    │          │
  │  │                        │         │                        │          │
  │  │  İnternet: AÇIK        │         │  İnternet: KAPALI      │          │
  │  │  (Cloudflare arkası)   │         │  (yalnızca iç ağ)      │          │
  │  └───────────┬────────────┘         └───────────┬────────────┘          │
  │              │                                   │                       │
  │              └──────────┬──────────┬─────────────┘                       │
  │                         │          │                                     │
  │                    ┌────▼──┐  ┌────▼───┐                                │
  │                    │  DB   │  │RabbitMQ│                                │
  │                    │(PgSQL)│  │(Queue) │                                │
  │                    └───────┘  └────────┘                                │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘
```

---

## §2 Sunucu 1 — Platform Core

Kullanıcıya dönük tüm servisleri barındırır. İnternet erişimi Cloudflare üzerinden
filtrelenir.

### Bileşenler

| Bileşen | KR Ref | Açıklama |
|---------|--------|----------|
| FastAPI API | KR-081 | Tüm dış API endpoint'leri (`/api/v1/*`), `POST /api/v1/edge/ingest` dahil |
| Next.js SSR/Frontend | — | Web arayüzü + PWA |
| Scheduler (cron) | KR-015 | Abonelik takvimi, mission planlama, weather block yeniden zamanlama |
| Payment SM | KR-033 | Ödeme durum makinesi (PENDING → PAID → ... ) |
| Expert Portal | KR-029 | Uzman inceleme arayüzü |
| RBAC / Auth | KR-063, KR-050 | 12 kanonik rol, JWT, brute-force koruması |
| Pilot Planner | KR-015 | Seed+Pull iş dağıtım, kapasite yönetimi |
| SLA Monitor | KR-028 | Mission SLA takibi, breach alarm |
| Training Feedback API | KR-029 | YZ eğitim geri bildirim toplama (portal tarafı) |
| Presigned URL Generator | KR-072 | S3 quarantine-bucket için ön-imzalı yükleme URL'leri üretir |

### POST /api/v1/edge/ingest — Sunucu 1'de Kalır

**Gerekçe:** Bu endpoint yalnızca manifest JSON (< 1 KB) alır ve presigned S3 URL'leri
döner (bkz. `data_lifecycle_transfer.md` §1, §4). Büyük dosyalar Platform'u
**transit etmez**; EdgeKiosk dosyaları doğrudan S3 quarantine-bucket'a yazar.

```
EdgeKiosk                     Sunucu 1                        S3
   │                             │                              │
   │  POST /edge/ingest         │                              │
   │  (manifest JSON, <1KB)     │                              │
   │  mTLS + allowlist          │                              │
   │────────────────────────────►│                              │
   │                             │  manifest hash doğrula       │
   │                             │  drone_id → registry (KR-030)│
   │                             │  presigned URL üret           │
   │  200 OK                     │                              │
   │  {upload_urls, session_id}  │                              │
   │◄────────────────────────────│                              │
   │                             │                              │
   │  HTTP PUT (presigned URL)   │                              │
   │  ham dosyalar (~1 TB)       │                              │
   │─────────────────────────────┼─────────────────────────────►│
   │                             │                              │
   │                             │  S3 Event Notification       │
   │                             │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─►│
   │                             │                    Sunucu 2'yi tetikler
```

### Kaynak Profili

| Metrik | Değer |
|--------|-------|
| CPU | Hafif, sürekli (API/SSR) |
| RAM | 4–8 GB (Redis dahil) |
| Ölçekleme ekseni | Kullanıcı sayısı |
| Ağ | İnternet + Cloudflare |

---

## §3 Sunucu 2 — Data Pipeline

Güvenilmez dosya işleme, AV2 tarama, kalibrasyon doğrulama ve YZ analiz
iş yüklerini barındırır. **İnternete açık endpoint'i yoktur.** İş akışı
olay tetiklemeli (event-driven) çalışır: S3 Event Notification ve RabbitMQ
queue'ları üzerinden.

### Bileşenler

| Bileşen | KR Ref | Açıklama |
|---------|--------|----------|
| S3 Event Listener | KR-072 | Quarantine-bucket'a yeni dosya geldiğinde pipeline'ı tetikler |
| AV2 Scanner (sandbox) | KR-073 | Merkez antivirüs taraması, **ayrı konteyner** içinde çalışır (DB bağlantısı yok) |
| Hash Verifier (SHA-256) | KR-072 | Manifest'teki hash ile S3 nesnesinin hash'ini karşılaştırır |
| Calibration Gate | KR-018 | `requires_calibrated=true` → kalibrasyon kanıtı arar, QC raporu üretir |
| Evidence Bundle Builder | KR-072 | `scan_report_center.json` + `verification_report.json` + `calibration_result.json` paketler |
| Quarantine → Verified Mover | KR-073 | Tüm kontroller PASS → dosyaları S3 verified-bucket'a taşır (S3 COPY) |
| AI Worker (YZ analiz) | KR-070 | RabbitMQ'dan job alır (pull/poll), verified-bucket'tan dataset okur (read-only, mTLS) |
| Drone Registry Cache | KR-030 | Kayıtlı drone metadata'sının yerel kopyası (doğrulama amaçlı) |

### İş Akışı (Event-Driven)

```
                            ┌───────────────────────────────────────────┐
                            │            SUNUCU 2 — İÇ AKIŞ            │
                            │                                           │
S3 quarantine               │  ┌──────────┐    ┌──────────────┐        │
Event Notification ────────►│  │ AV2      │───►│ Hash         │        │
                            │  │ Scanner  │    │ Verifier     │        │
                            │  │(sandbox) │    │ (SHA-256)    │        │
                            │  └──────────┘    └──────┬───────┘        │
                            │                         │                │
                            │                  ┌──────▼───────┐        │
                            │                  │ Calibration  │        │
                            │                  │ Gate (KR-018)│        │
                            │                  └──────┬───────┘        │
                            │                         │                │
                            │              ┌──────────▼──────────┐     │
                            │              │ Evidence Bundle     │     │
                            │              │ Builder (KR-072)    │     │
                            │              └──────────┬──────────┘     │
                            │                         │                │
                            │                    ALL PASS?             │
                            │                   /        \             │
                            │                  ▼          ▼            │
                            │         ┌──────────┐  ┌────────────┐    │
                            │         │ S3 COPY  │  │ REJECTED   │    │
                            │         │ verified │  │ QUARANTINE │    │
                            │         └──────────┘  └────────────┘    │
                            │                                          │
  RabbitMQ                  │  ┌──────────┐    ┌──────────────┐       │
  job dispatch ────────────►│  │ AI Worker│───►│ DB write:    │       │
  (pull/poll)               │  │ (YZ)     │    │ analysis_jobs│       │
                            │  └──────────┘    │ .status =    │       │
                            │                  │ 'ANALYZED'   │       │
                            │                  └──────────────┘       │
                            └──────────────────────────────────────────┘
```

### HTTP Endpoint Yok — İçeriye Çağrı Kabul Etmez

SSOT [KR-070] gereği Worker (Sunucu 2) **inbound HTTP** kabul etmez. İş alma
yalnızca queue pull/poll ile olur. S3 Event Notification, S3 servisinin push
bildirimi olup doğrudan HTTP çağrısı değildir.

**Not:** SSOT [KR-070] ağ politikası matrisinde `Worker → Platform Results API: ALLOW
(outbound only, mTLS)` tanımlıdır. Paylaşılan DB modelinde (bkz. §4) bu HTTP
çağrısı **DB yazımı ile ikame edilir**: Worker sonucu doğrudan `analysis_jobs`
tablosuna yazar. Platform, kendi CQRS query handler'ları ile DB'yi okur.
Bu, KR-070'in "tek yönlü sonuç akışı" amacını korurken HTTP bağımlılığını ortadan
kaldırır.

### Kaynak Profili

| Metrik | Değer |
|--------|-------|
| CPU | Yoğun, anlık artış (AV2 tarama + YZ analiz) |
| RAM | 8–16 GB (AV motor + büyük dosya buffer) |
| Ölçekleme ekseni | Drone sayısı / uçuş sezonu |
| Ağ | İnternet ERİŞİLEMEZ — yalnızca iç ağ (S3, DB, Queue) |

---

## §4 Paylaşılan Veritabanı Katmanı

İki sunucu **aynı PostgreSQL instance'ını** paylaşır. Güvenlik ayrımı, veritabanı
rolleri (ROLE) ve tablo düzeyinde GRANT/REVOKE ile sağlanır.

### DB Role Erişim Matrisi

```
┌────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Role Erişim Matrisi                   │
│                                                                    │
│  ROLE: platform_core_rw                                            │
│  ├── users ──────────────── SELECT, INSERT, UPDATE                 │
│  ├── user_roles ─────────── SELECT, INSERT, UPDATE, DELETE         │
│  ├── cooperatives ───────── SELECT, INSERT, UPDATE                 │
│  ├── coop_memberships ───── SELECT, INSERT, UPDATE, DELETE         │
│  ├── fields ─────────────── SELECT, INSERT, UPDATE                 │
│  ├── field_crops ────────── SELECT, INSERT, UPDATE                 │
│  ├── missions ───────────── SELECT, INSERT, UPDATE                 │
│  ├── subscriptions ──────── SELECT, INSERT, UPDATE                 │
│  ├── price_snapshots ────── SELECT, INSERT                         │
│  ├── payment_intents ────── SELECT, INSERT, UPDATE                 │
│  ├── analysis_jobs ──────── SELECT, INSERT, UPDATE                 │
│  ├── calibration_records ── SELECT, INSERT, UPDATE                 │
│  ├── qc_reports ─────────── SELECT, INSERT, UPDATE                 │
│  ├── audit_logs ─────────── SELECT, INSERT (WORM: UPDATE/DELETE ✗) │
│  └── mission_route_files ── SELECT, INSERT, UPDATE                 │
│                                                                    │
│  ROLE: pipeline_rw                                                 │
│  ├── analysis_jobs ──────── SELECT, INSERT, UPDATE                 │
│  ├── calibration_records ── SELECT, INSERT, UPDATE                 │
│  ├── qc_reports ─────────── SELECT, INSERT, UPDATE                 │
│  ├── audit_logs ─────────── INSERT (WORM: yalnızca yazma)          │
│  └── missions ───────────── SELECT (status okuma amaçlı)           │
│                                                                    │
│  pipeline_rw ERİŞEMEZ:                                             │
│  ✗ users                                                           │
│  ✗ user_roles                                                      │
│  ✗ cooperatives                                                    │
│  ✗ coop_memberships                                                │
│  ✗ subscriptions                                                   │
│  ✗ payment_intents                                                 │
│  ✗ price_snapshots                                                 │
│  ✗ fields (PII: konum + sahip bilgisi)                             │
│  ✗ field_crops                                                     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Ek Katmanlar

| Bileşen | Kullanım | Notlar |
|---------|----------|--------|
| Redis | Cache + rate-limit | Sunucu 1'de birincil; Sunucu 2 gerekirse kendi instance'ı |
| RabbitMQ | İş dağıtımı (broker) | Sunucu 1 → publish, Sunucu 2 → consume (KR-070: pull/poll) |

---

## §5 Servisler Arası İletişim

**Temel ilke:** Microservice DEĞİL — paylaşımlı DB ile dikey yeterlilik
(shared-database modular monolith + isolated pipeline).

### İletişim Matrisi

```
┌──────────┐                                           ┌──────────┐
│ Sunucu 1 │                                           │ Sunucu 2 │
│ Platform │                                           │ Pipeline │
│          │                                           │          │
│  publish ├────────── RabbitMQ ──────────────────────►│ consume  │
│  (job)   │           (queue)                         │ (pull)   │
│          │                                           │          │
│  SELECT  │◄────────── PostgreSQL ───────────────────►│ INSERT/  │
│  (CQRS   │           (shared DB)                     │ UPDATE   │
│   read)  │                                           │ (write)  │
│          │                                           │          │
│  LISTEN  │◄────────── PG NOTIFY ────────────────────│ NOTIFY   │
│  (real-  │           (kanal)                         │ (event)  │
│   time)  │                                           │          │
│          │           ┌─────────┐                     │          │
│  URL üret├──────────►│   S3    │◄────────────────────┤ read/    │
│  (presign│           │ buckets │                     │ write    │
│   ed)    │           └─────────┘                     │ (move)   │
└──────────┘                                           └──────────┘

     ✗ Sunucu 2 → Sunucu 1: HTTP çağrısı YOK
     ✗ Sunucu 1 → Sunucu 2: Doğrudan TCP/HTTP YOK (KR-070: platform→worker DENY)
```

### Akış Kuralları

1. **Sunucu 1 → RabbitMQ → Sunucu 2:** İş bildirimi (dispatch). Sunucu 2 pull/poll
   ile alır. Sunucu 1 asla Sunucu 2'ye doğrudan push yapmaz (KR-070).
2. **Sunucu 2 → PostgreSQL:** Pipeline tamamlandığında sonuçları DB'ye yazar
   (`analysis_jobs.status = 'ANALYZED'`, `qc_reports`, `calibration_records`).
3. **Sunucu 1 ← PostgreSQL:** Platform, CQRS query handler'ları ile DB'yi okur.
4. **Gerçek zamanlı bildirim:** Sunucu 2 `NOTIFY pipeline_done, '{"job_id": "..."}'`
   gönderir. Sunucu 1 `LISTEN pipeline_done` ile anında haberdar olur.
5. **S3 Event → Sunucu 2:** Quarantine-bucket'a dosya geldiğinde S3, event
   notification ile Sunucu 2'nin pipeline'ını tetikler.
6. **HTTP çağrısı: HİÇBİR ZAMAN** — Ne Sunucu 2→Sunucu 1 ne de Sunucu 1→Sunucu 2
   yönünde doğrudan HTTP bağlantısı kurulmaz. Tüm iletişim DB, queue ve S3 event
   kanalları üzerinden gerçekleşir.

---

## §6 Güvenlik Kuralları

### Ağ Erişim Matrisi

| Kaynak → Hedef | Protokol | İzin | KR Ref |
|----------------|----------|------|--------|
| İnternet → Sunucu 1 | HTTPS 443 | Cloudflare WAF arkası | — |
| EdgeKiosk → Sunucu 1 (/edge/ingest) | HTTPS + mTLS | Allowlist (ikincil) + mTLS (birincil) | KR-071 |
| EdgeKiosk → S3 quarantine | HTTPS (presigned PUT) | Presigned URL ile | KR-072 |
| İnternet → Sunucu 2 | TCP * | **DENY** (tüm portlar) | KR-070 |
| Sunucu 1 → Sunucu 2 | TCP/HTTP | **DENY** | KR-070 |
| Sunucu 2 → Sunucu 1 | TCP/HTTP | **DENY** | KR-070 |
| Sunucu 2 → S3 (quarantine) | HTTPS | READ (AV2 + hash verify) | KR-073 |
| Sunucu 2 → S3 (verified) | HTTPS | WRITE (taşıma) | KR-072 |
| Sunucu 2 → S3 (verified) | HTTPS | READ (AI Worker, read-only, mTLS + kısa ömürlü token) | KR-070 |
| Sunucu 2 → PostgreSQL | TCP 5432 | `pipeline_rw` rolü | §4 |
| Sunucu 2 → RabbitMQ | AMQP | consume-only | KR-070 |

### AV2 Sandbox İzolasyonu (KR-073)

```
┌─────────────────────────────────────────────────────┐
│  Sunucu 2                                           │
│                                                     │
│  ┌───────────────┐      ┌───────────────────────┐  │
│  │ Pipeline      │      │ AV2 Sandbox           │  │
│  │ Orchestrator  │─────►│ (ayrı konteyner)      │  │
│  │               │      │                       │  │
│  │ ● DB bağlantısı      │ ● DB bağlantısı YOK   │  │
│  │ ● Queue erişimi      │ ● Ağ: sadece S3 read  │  │
│  │ ● S3 erişimi  │      │ ● /tmp/sandbox/ lokal │  │
│  │               │◄─────│ ● Çıktı: scan_report  │  │
│  └───────────────┘      └───────────────────────┘  │
│                                                     │
│  Dosya scratch alanı: /tmp/pipeline/ (lokal)        │
│  Tarama scratch: /tmp/sandbox/ (AV konteyner lokal) │
│  Doğrulanmış dosyalar → S3 verified-bucket          │
│  DB'ye yalnızca EvidenceBundleRef (UUID + S3 path)  │
└─────────────────────────────────────────────────────┘
```

**Kritik kurallar:**
- AV2 sandbox konteynerinin **DB bağlantısı yoktur** — yalnızca dosya giriş/çıkış
- Sandbox konteyner ağı kısıtlıdır: yalnızca S3 quarantine-bucket READ
- Dosyalar **asla** Platform Core (Sunucu 1) üzerinden transit etmez (KR-071)
- Quarantine'da kalan dosyalar 7 gün sonra alarm tetikler (ops izleme)

### İki Aşamalı Tarama Zinciri (KR-073)

| Aşama | Konum | Çıktı | Amacı |
|-------|-------|-------|-------|
| AV1 | EdgeKiosk (saha) | `scan_report_edge.json` | Bariz zararlıyı erken yakala |
| AV2 | Sunucu 2 (merkez sandbox) | `scan_report_center.json` | İkinci kontrol + kurcalama ispatı |

Her iki aşamada **hash doğrulama** ve **dosya tipi whitelist** zorunludur (KR-072).

---

## §7 Dağıtım Yaşam Döngüsü

### Bağımsız Deploy

Sunucu 1 ve Sunucu 2 **bağımsız** deploy edilebilir. Aşağıdaki koşullar sağlandığı
sürece birinin güncellenmesi diğerini **etkilemez**:

| Koşul | Açıklama | KR Ref |
|-------|----------|--------|
| DB şema uyumu | Alembic migration'lar iki taraf için uyumlu | KR-081 |
| Queue mesaj formatı | RabbitMQ mesaj şeması sürümlü (contract-first) | KR-081 |
| S3 bucket yapısı | quarantine/verified bucket adları ve IAM politikaları tutarlı | KR-072 |

### Deploy Sırası (Breaking Change Durumunda)

1. DB migration (her iki sunucuyu da destekleyen "expand" fazı)
2. Sunucu 2 deploy (yeni şemayı okuyabilir)
3. Sunucu 1 deploy (yeni şemayı okuyabilir)
4. DB migration temizlik ("contract" fazı — eski sütun/tablo kaldırma)

---

## §8 Mevsimsel Ölçekleme

### İki Farklı Yük Profili

Platform'un iki sunucusu **farklı mevsimsel yük profillerine** sahiptir:

```
       Oca  Şub  Mar  Nis  May  Haz  Tem  Ağu  Eyl  Eki  Kas  Ara
       ─────────────────────────────────────────────────────────────
S1     ░░░  ░░░  ░░░  ░░░  ░░░  ░░░  ░░░  ░░░  ░░░  ███  ███  ███
(API)  düşük                                         yüksek (hasat
       (kış)                                          sonuç talebi)

S2     ░░░  ░░░  ░░░  ░░░  ███  ███  ███  ███  ███  ██░  ░░░  ░░░
(Pipe) düşük           yüksek (drone uçuş + veri toplama sezonu)
       ─────────────────────────────────────────────────────────────
```

| Sunucu | Peak Dönem | Neden | Ölçekleme |
|--------|-----------|-------|-----------|
| Sunucu 1 (Platform Core) | Ekim–Aralık | Hasat sonucu görüntüleme, rapor talebi, kooperatif toplu işlemleri | Rate limit multiplier 2–3× (`seasonal_config.yaml`) |
| Sunucu 2 (Data Pipeline) | Mayıs–Ekim | Aktif drone uçuşları, yoğun veri toplama, AV tarama + YZ analiz hacmi | Yeni pipeline instance'ları ile horizontal scale (3–5×) |

### Ölçekleme Stratejisi

**Sunucu 1:** `seasonal_config.yaml` rate-limit profilleri ile mevcut kapasite
yönetilir. Gerekirse replica sayısı artırılır (K8s HPA).

**Sunucu 2:** Mayıs–Ekim döneminde:
- AV2 sandbox konteyner sayısı artırılır (paralel tarama)
- AI Worker replica sayısı artırılır (paralel analiz)
- RabbitMQ consumer sayısı orantılı büyütülür
- Ekim sonrası instance'lar geri çekilir (scale-down)

---

## Checklists

### Preflight
- DB role'leri (`platform_core_rw`, `pipeline_rw`) oluşturuldu ve GRANT/REVOKE doğru.
- Ağ politikaları (firewall / K8s NetworkPolicy) §6 matrisine uygun.
- S3 bucket IAM politikaları `data_lifecycle_transfer.md` §6 erişim kontrol matrisine uygun.
- RabbitMQ mesaj şemaları sürümlü ve CI doğrulaması geçiyor (KR-081).
- AV2 sandbox konteyneri DB bağlantısız çalışıyor (izolasyon doğrulaması).

### Operate
- Sunucu 2 inbound bağlantı denemesi izleniyor → alarm (KR-070).
- `pipeline_rw` rolünün erişmemesi gereken tablolara sorgu denemesi izleniyor.
- Quarantine-bucket dosya yaşı izleniyor (7+ gün → alarm).
- Mevsimsel ölçekleme geçişleri loglanıyor.
- RabbitMQ queue derinliği izleniyor (backpressure alarm).

### Postmortem
- Sunucu bölme kararının SLA üzerindeki etkisi değerlendirildi.
- Pipeline scale-up/down geçişlerinde veri kaybı olmadığı doğrulandı.
- DB role ayrımının güvenlik ihlali senaryosundaki etkisi test edildi.

## Related docs
- `docs/architecture/data_lifecycle_transfer.md` — Veri akışı ve transfer detayları (kanonik)
- `docs/architecture/clean_architecture.md` — Katman sınırları ve bağımlılık kuralları
- `docs/architecture/event_driven_design.md` — Event tipleri ve idempotency
- `docs/architecture/training_feedback_architecture.md` — YZ eğitim geri bildirim döngüsü
- `docs/architecture/adaptive_rate_limiting.md` — Rate limiting ve mevsimsel profiller
- `config/rate_limits/seasonal_config.yaml` — Mevsimsel rate-limit konfigürasyonu
- `deploy/k8s/deployment.yaml` — K8s dağıtım manifest'i
- `deploy/k8s/network-policy.yaml` — K8s ağ politikaları
- `docs/api/openapi.yaml` — OpenAPI 3.1.0 spesifikasyonu
- `contracts/schemas/edge/` — EdgeKiosk ingest contract şemaları
