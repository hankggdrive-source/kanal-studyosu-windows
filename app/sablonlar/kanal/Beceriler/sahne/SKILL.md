---
name: "sahne"
description: "{{KANAL_ADI}} 5. aşama: {{HEDEF_DIL}} finalden üretim paketi çıkarır (ElevenLabs metni, Flow görsel promptları, ilk 6 sahne Veo3, montaj planı) ve kendini kontrol eder."
---

# Aşama 5 — Üretim paketi

Esas: `03_Aktif_Video.md` (konu kartı + {{HEDEF_DIL}} final), `01_Anayasa` (§2 anlatıcı/karakter, §3 görsel kimlik),
`00_Yonetici`. Etiketler, karakter, yasaklı kelimeler, izinli olumsuzlamalar, tag kuralları ve maskot kuralı KANAL
AYARLARI'ndadır.

**{{HEDEF_DIL}} metnin kelimelerine dokunulmaz:** yeniden yazılmaz, çevrilmez, özetlenmez. Yalnız sahnelere bölünür ve
ölçülü tag eklenir.

## Adım 1 — Sahne bölme
- Sahne, tek görsel fikri taşıyan en küçük anlatı birimidir. Eylem, nesne, zaman, ton ya da metafor↔gerçek değişiyorsa
  paragraf 2+ sahneye bölünür; çok kısa ardışık beat'ler birleştirilir.
- Süreler: ilk ~30 sn ≈ 6 sahne, 4–6 sn. Sonra 4–10 sn. Sessiz sahne yoktur.
- Ana metaforun 3 görünüşü planlanan paragraflarda görselleşir; nesne tasarımı aynı kalır.
- Işık arkı: açılış/mekanizma yumuşak ve okunaklı → farkındalık dengeli → final sıcak. Mekân, saat ve nesneler sahneler
  arasında tutarlı; aynı kamera planı art arda 3 kez yok.

## Adım 2 — A · ElevenLabs metni (`_5A_elevenlabs.txt`)
- Her paragraf = bir sahne, sırayla; aralarda tek boş satır. Başlık, numara, senaryo etiketi ve açıklama satırı yok.
- Yalnız KANAL AYARLARI'ndaki ses tag'leri kullanılır; tag'li paragraf oranı sınırın altında kalır; paragrafta en fazla
  1 tag, paragrafın en başında; aynı tag art arda iki paragrafta yok. `<break>`, SSML ve izinli set dışında köşeli
  parantezli not yasak. Duraklama noktalamayla yapılır.

## Adım 3 — B · Flow görsel promptları (`_5B_gorsel_promptlari.txt`)
- Sahne başına bir prompt, İngilizce, tek satır; aralarda bir boş satır. Numara ve başlık yok. Prompt sayısı A'daki
  paragraf sayısına EŞİTTİR. Her prompt tek başına çalışır.
- Biçim: karakter/yok + eylem + mekân + ana nesne + 2–3 ikincil detay + duygu + kamera + ışık + stil çapası (01_Anayasa §3).
  - Karakter sahnesi: karakter etiketi tanımlıysa prompt onunla başlar; görünüş tarif edilmez, yalnız poz, duygu ve eylem.
    Karakter görünmüyorsa etiket yazılmaz.
  - Metafor: karakter yok, tek sembol, gerçek ortam. Şema: karakter yok, yazı yok, ok/şekil dili (şema çapası).
- **Flow güvenliği (bağlayıcı):** yasaklı kelimeler hiçbir biçimde kullanılmaz. Olumsuzlama yok: istenmeyeni yazma, olanı
  tarif et; yalnız izinli teknik olumsuzlamalar kullanılır. Hassas metin sahnelerinde görsel yalnız sakin mekân ve nesnedir.
- Maskot sahnelerinde (Adım 5) promptun sonuna `calm uncluttered lower-left corner` eklenir.

## Adım 4 — C · Veo3 promptları (`_5C_veo3.md`)
İlk 6 sahne için hareket promptları: `Scene 01 → <English motion prompt>` … `Scene 06 → …`. Statik görseldeki duygu
hareket ettirilir; yeni hikâye, karakter, sert kamera, dudak senkronu ve yazı yok. Flow güvenliği burada da geçerli.

## Adım 5 — D · Montaj planı (`_5D_montaj_plani.tsv`)
Tek TSV, başlık satırı dahil (sahne sayısı + 1) satır. Sütunlar tam bu sırada:
`sahne	bolum	rol	duygu	hareket	odak	efekt	sonraki_gecis	maskot	gerekce`
- **sahne:** 0001… · **bolum:** §N · **rol:** kanca / anlatim / ani / metafor / farkindalik / pratik / guvenlik / cta /
  kapanis · **gerekce:** ≤8 kelime, Türkçe.
- **hareket:** YAKINLAS · UZAKLAS · SAGA · SOLA · ASAGI · YUKARI · NEFES. Aynı hareket en fazla 2 kez üst üste; KES ile
  bağlanan iki sahnede zıt yön yok.
- **odak:** hareketin yöneleceği öğe, B'deki nesne adıyla, kısa.
- **efekt:** duyguya göre: `ESKI_FOTO` (geçmiş/anı) · `VINYET` (içe kapanma, ağırlık, gerginlik) · `YUMUSAK_ISIK`
  (sıcaklık, umut, final) · gerekmiyorsa `-`. Aynı efekt 3'ten fazla art arda yok; toplam genelde %10–30.
- **sonraki_gecis:** KES %65–75 · KARISIM %15–25 · KARARMA yalnız bölüm değişiminde, en fazla 5 · ANI_GIRIS / ANI_CIKIS
  yalnız şimdi↔anı geçişlerinde · SAYFA en fazla 2 · ICERI en fazla 3 · son sahnede `-`.
- **maskot:** KANAL AYARLARI'nda maskot sırası varsa o sırayla, tam o kadar sahnede; diğerleri `-`. Maskot yoksa bütün
  satırlar `-`. Maskot sahneleri hüzünlü, güvenlik ya da CTA sahnesi olmaz; ≥6,5 sn; hareketi NEFES ya da YAKINLAS.

## Adım 6 — Kendi kontrolün (teslimden önce)
1. A metni, tag'ler çıkarılınca {{HEDEF_DIL}} finalin konuşulan metniyle kelimesi kelimesine aynı mı? 2. A = B = D − 1?
İlk 30 sn 5–7 sahne mi? 3. Tag oranı ve izinli set. 4. Yasaklı kelime ve izinsiz olumsuzlama yok; karakter etiketi yalnız
karakter görünen sahnelerde ve promptun başında. 5. Plan kuralları ve maskot. 6. Metafor 3 görünüş.

## Çıktı
1. Dört dosya: `{{KOD_ONEKI}}-0X_5A_elevenlabs.txt` · `{{KOD_ONEKI}}-0X_5B_gorsel_promptlari.txt` ·
   `{{KOD_ONEKI}}-0X_5C_veo3.md` · `{{KOD_ONEKI}}-0X_5D_montaj_plani.tsv`.
2. Sohbet cevabı: en fazla 5 satır özet · kontrol satırları (`Metin birebir ✓ · A=B=D NN ✓ · İlk 30 sn N sahne ✓ · Tag
   %NN ✓ · Yasaklı kelime 0 ✓ · KES %NN · KARARMA N · Maskot …`) · durum kartı `Sonraki: paketleme`.

## Düzeltme turu
Yalnızca değişen sahneler; görsel mantık hatası bildirilirse ilgili B promptu sadeleştirilir.
