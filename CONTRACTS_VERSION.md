# Contracts Version — Surum Sabitleme (Pinning)

> **KR-081** Contract-First: Backend, Frontend ve Worker ayni API/Event semasini
> konustugunun garantisi bu dosya ile saglanir.

## Aktif Contract Surumu

| Alan | Deger |
|------|-------|
| **Contract Set Version** | `2.0.1` |
| **Schema Draft** | JSON Schema draft 2020-12 |
| **SSOT Referansi** | `docs/TARLAANALIZ_SSOT_v1_2_0.txt` — KR-081 |
| **Checksum Dosyasi** | `CONTRACTS_SHA256.txt` |
| **Son Guncelleme** | 2026-03-07 |
| **Contracts Checksum (SHA-256)** | `12b7ebcea698b44bfc4203d79147588f6bce9f102c03c741f5c67c61f727cee2` |

## Contract Listesi

| Contract | Schema ID | Surum | Durum | v2.0.0 Degisiklikler |
|----------|-----------|-------|-------|---------------------|
| AnalysisJob | `analysis_job.v1` | 1.1.0 | Aktif | — |
| AnalysisResult | `analysis_result.v1` | 1.1.0 | Aktif | — |
| PaymentIntent v1 | `payment_intent.v1` | 1.0.0 | Deprecated | v2 ile degistirildi |
| PaymentIntent v2 | `payment_intent.v2` | 2.0.0 | Aktif | +receipt_blob_id, +admin_user_id, +rejection_reason, +admin_note, +field_id, +REFUNDED durumu |
| PaymentStatus v1 | `payment_status.v1` | 2.0.0 | Aktif | -APPROVED, -EXPIRED (breaking) |
| PaymentStatus v2 | `payment_status.v2` | 2.0.0 | Aktif | -APPROVED, -EXPIRED (breaking) |
| PaymentMethod | `payment_method.v1` | 2.0.0 | Aktif | IBAN dekont upload endpointi |
| DroneType | `drone_type.enum.v1` | 2.0.0 | Aktif | Yeni enum (drone-agnostik mimari) |
| AI Feedback | `ai.feedback.v1` | 1.0.0 | Aktif | — |
| Training Export (CLS) | `training.feedback.cls.v1` | 1.0.0 | Aktif | — |
| Training Export (GEO) | `training.feedback.geo.v1` | 1.0.0 | Aktif | — |
| DatasetIngestRequest | `dataset_ingest_request.v1` | 1.1.0 | Aktif | — |
| DatasetIngestResponse | `dataset_ingest_response.v1` | 1.0.0 | Aktif | — |

## v2.0.0 Breaking Changes (Migration Gerektiren)

| Degisiklik | Detay | Migration |
|-----------|-------|-----------|
| `payment_status` APPROVED kaldirildi | Kanonik onay durumu `PAID`'dir | APPROVED -> PAID |
| `payment_status` EXPIRED kaldirildi | Admin karariyla CANCELLED yapilir | EXPIRED -> CANCELLED |
| `payment_method` IBAN akisi | E-posta yerine uygulama ici dekont upload | POST /payments/intents/{id}/upload-receipt |
| `payment_intent.v2` zorunlu alanlar | admin_note/rejection_reason zorunlu | Migration guide: docs/migration_guides/payment_intent_v1_to_v2.md |

## Surumleme Kurali (SemVer)

- **v1.x**: Geriye uyumlu (backward compatible) eklemeler serbest (optional field eklenebilir)
- **v2.0**: Breaking change; bu dosya + `CONTRACTS_SHA256.txt` zorunlu guncellenir
- Breaking change tespit edildiginde CI pipeline merge'u engeller (KR-041)

## Uyumluluk Matrisi

| Servis | Minimum Contract Version | Notlar |
|--------|--------------------------|--------|
| Backend (Platform) | 2.0.1 | payment_intent v2, APPROVED/EXPIRED kaldirildi |
| AI Worker | 1.0.0 | Tuketici (AnalysisJob) + uretici (AnalysisResult) |
| Frontend (PWA) | 2.0.1 | payment_status degisiklikleri yansitilmali |
| Edge Kiosk | 1.1.0 | Uretici: available_bands zorunlu |
