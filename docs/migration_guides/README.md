# Migration Guides

> BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.

**Owners:** Staff Backend Architect, Platform Owner
**Last updated:** 2026-02-23
**SSOT references:** GOVERNANCE_PACK_v1_0_0 § Change Control, KR-041 (Şema Uyumluluğu)

---

## Amaç

Bu dizin, **kırıcı değişiklik (breaking change)** içeren her sürüm yükseltmesine eşlik eden
migration rehberlerini barındırır.

GOVERNANCE_PACK kuralı: bir breaking change içeren PR, burada bir migration guide dosyasıyla
birlikte gelmelidir. Aksi takdirde `test_no_breaking_changes` CI kapısı PR'ı reddeder.

---

## Klasör Yapısı

```
docs/migration_guides/
├── README.md                     ← bu dosya
└── v<MAJOR.MINOR.PATCH>.md       ← her kırıcı sürüm için bir dosya
```

Örnek: `v2_0_0.md` — API response şemasında kırıcı değişiklik.

---

## Migration Guide Şablonu

Yeni bir kırıcı değişiklik için aşağıdaki şablonu kopyalayın:

```markdown
# Migration Guide: v<MAJOR.MINOR.PATCH>

**Tarih:** YYYY-MM-DD
**Breaking change sınıfı:** API | DB Schema | Event Contract | Config
**KR referansları:** KR-xxx, KR-yyy

## Özet

Tek cümleyle değişikliğin kapsamı.

## Kırıcı Değişiklikler

| Alan | Eski Değer | Yeni Değer |
|------|-----------|-----------|
| ... | ... | ... |

## Migration Adımları

1. ...
2. ...
3. ...

## Rollback

1. ...

## Etkilenen Servisler / Bağımlılıklar

- ...

## Test Koşulları

- [ ] ...
```

---

## Kurallar (GOVERNANCE_PACK § 3 — Change Control)

| Değişiklik sınıfı | Gereksinim |
|-------------------|-----------|
| doc-only | Migration guide gerekmez |
| non-breaking | Migration guide gerekmez; CHANGELOG güncellemesi yeterli |
| **breaking** | **Migration guide zorunlu** (bu dizinde yeni `.md` dosyası) |

SemVer: breaking change → MAJOR bump. Non-breaking feature → MINOR bump. Düzeltme → PATCH bump.
