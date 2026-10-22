---
name: "ceviri"
description: "{{KANAL_ADI}} 4. aşama: Türkçe senaryoyu {{HEDEF_DIL}} dilinin kurallarıyla yeniden yazar, ilk 4 paragrafı hook puanıyla güçlendirir, sonda {{HEDEF_DIL}} öz-denetim yapar."
---

# Aşama 4 — {{HEDEF_DIL}} final

Esas: `01_Anayasa` (§4, §5, §6, §7 {{HEDEF_DIL}} doğallık, §8, §9), `02_Defter F`, onaylı konu kartı ve Türkçe senaryo.
Sıra sabittir: **1 uyarlama → 2 hook → 3 denetim.** Ara hâller gösterilmez.

## Adım 1 — Çeviri değil, {{HEDEF_DIL}} yeniden yazım
- Anlam, yapı, paragraf sırası ve senaryo etiketleri korunur. Başka köşeli parantezli işaret eklenmez.
  **Paragraf sayısı Türkçe metinle aynıdır.**
- Türkçe cümle sırası birebir taşınmaz; her cümle, dili ana dili olarak konuşan biri nasıl söylerse öyle kurulur. Hitap
  01_Anayasa §1'deki gibi baştan sona tutarlıdır.
- Kültürel kalıntılar hedef kitleye uyarlanır. Teknik jargon azaltılır, ihtiyat kipi korunur.
- 01_Anayasa §7 kuralları uygulanır.
- **Uzunluk:** {{HEDEF_DIL}} metin için KANAL AYARLARI'ndaki kelime aralığı (etiketler hariç). Kısa kalırsa sahne ve somut
  örnekle genişletilir; dolgu eklenmez.
- Seslendirme tag'i EKLENMEZ (5. aşamanın işi).

## Adım 2 — Hook: yalnızca ilk 4 paragraf
3 versiyon yaz (mevcut dahil), her birini 10 üzerinden puanla: ilk cümle ≤10 kelime ve somut (2) · ~8. sn'de beklenti
kırılması (2) · 30 sn içinde net vaat ve açık döngü (2) · 4. paragraf güçlü "kal" cümlesi (2) · başlık, kapak ve açılış
anıyla uyumlu, 02_Defter F'deki açılışlardan farklı (2). En yükseğini seç; KANAL AYARLARI'ndaki hook eşiğinin altındaysa
düzelt ve yeniden puanla. 5. paragraftan sonrasına dokunma.

## Adım 3 — {{HEDEF_DIL}} öz-denetim (no-ai-slop + humanizer mantığı)
İkili karşıtlık en fazla 2 · dolgu kelimeler · şişirme · üçlemeler · sahte ifşa girişleri · kesik dram zinciri · retorik
soru-cevap en fazla 2 · aforizma formülü · Türkçe/İngilizceden çeviri kokan söz dizimi · koç/terapist kalıpları · belirsiz
otorite · uzun tire · tekdüze ritim · kanal kalıp sayacı (02_Defter F). Son okuma: ana dili konuşan biri bunu böyle söyler
mi? Seslendirmede nefes almaya izin veriyor mu? Denetimden sonra kelime sayısı yeniden kontrol edilir.

## Çıktı
1. `{{KOD_ONEKI}}-0X_4_senaryo_{{HEDEF_DIL_KODU}}.md`: yalnız etiketli final metin. Sonunda:
   ```
   Words: NNNN · Paragraphs: NN
   Açılış tipi: … · Kal cümlesi: ¶4 · Köprü tipi: … · CTA tipi: … · Hook puanı: X/10 · Defterle çakışma: yok
   Bilgi kazancı: 1) … 2) … 3) …
   Metafor: kapalı ¶… · açıklayan ¶… · dönüşmüş ¶…
   Kalıp sayaçları: …
   ```
2. Sohbet cevabı: en fazla 5 satır özet · hook puan tablosu (3 satır) · kontrol satırları (`Kelime NNNN ✓ · Paragraf
   sayısı TR ile aynı ✓ · Hook ≥ eşik ✓ · Öz-denetim: N kalıp düzeltildi`) · durum kartı
   `Bekleyen: ONAY 4 | Sonraki: sahne`.

## Düzeltme turu
Yalnızca değişen paragraflar; kelime sayısı yeniden verilir.
