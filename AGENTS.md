# TARLAANALIZ PLATFORM – AGENTS.md

## 1. Canonical Authority (BAĞLAYICI)
- `docs/TARLAANALIZ_SSOT_v1_2_0.txt` bu projede **tek kanonik kaynaktır**.
- Bu doküman bağlayıcıdır.
- Kurallar, kararlar ve limitler **tekrar yazılmaz**, yalnızca **KR referansı** ile kullanılır.
- SSOT ile çelişen hiçbir çıktı kabul edilemez.

## 2. Scope & Non-Goals
- Yapay zekâ **analiz yapar**, ilaçlama / müdahale kararı **vermez**.
- Operasyonel Playbook ve İş Planı içerikleri **koda gömülmez**.
- Bu repo bir **platform** reposudur; satış, ekonomi, fiyatlama mantığı içermez.

## 3. Coding Rules (ZORUNLU)
- Kod üretimi **contract / schema / interface first** yaklaşımıyla yapılır.
- Serbest yorum, örtük iş kuralı veya “tahmini” davranış eklenmez.
- Her üretilen dosyanın en üstünde şu header bulunur:

  `BOUND: TARLAANALIZ_SSOT_v1_2_0.txt – canonical rules are referenced, not duplicated.`

- Kod içinde iş kuralı geçen her yerde ilgili **KR kodu yorum satırıyla belirtilir**.

## 4. Planning & Operations Constraints (Özet Referans)
Aşağıdaki kurallar **yalnızca referans içindir**; detayları SSOT’tadır:

- **KR-015**: Pilot planlama, günlük kapasite, work_days ≤ 6, büyük alanlarda çoklu pilot
- **KR-016**: Görev / çıktı adlandırma standartları (KMZ, mission ids)
- **KR-018**: Radyometrik kalibrasyon **hard-gate** (kalibrasyonsuz analiz yok)
- **KR-033**: Ödeme + manuel onay + audit log
- **KR-071**: YZ izolasyonu ve tek yönlü (outbound) sonuç akışı
- **KR-081**: AnalysisJob – JSON Schema / contract-first zorunluluğu

## 5. Data & AI Boundaries
- Ham drone verisi (DN) **kalibrasyonsuz işlenmez**.
- YZ worker’ları **offline/izole** çalışır; platforma geri çağrı yapmaz.
- Çıktılar yalnızca tanımlı schema üzerinden platforma döner.

## 6. Repository Structure (Referans)
- Hedef dizin yapısı:
  `docs/tarlaanaliz_platform_tree_v3.2.2_FINAL_2026-02-08.txt`
- Yeni dosya veya klasör eklenmesi bu ağaca uygun olmalıdır.
- Aynı işi yapan mükerrer dosyalar oluşturulmaz.

## 7. Documents Available for Reference (OKUNUR, KOPYALANMAZ)
- `docs/TARLAANALIZ_SSOT_v1_2_0.txt`
- `docs/README.md` (dokümantasyon navigasyonu)
- `docs/governance/GOVERNANCE_PACK_v1_0_0.md` (SDLC & değişiklik kontrolü)
- `docs/kr/kr_registry.md` (KR indeks ve navigasyonu)
- Dosya açıklamaları ve envanter dokümanları

Bu dokümanlar **arka plan bilgisidir**.  
Kod üretiminde **metinleri tekrar edilmez**, yalnızca referans alınır.

## 8. Output Discipline
- Maksimum **10 dosya** tek batch’te üretilir.
- Kod + test odaklı çıktı verilir; uzun açıklama yazılmaz.
- Belirsizlik varsa kod yazılmaz, **uyarı verilir**.

---
