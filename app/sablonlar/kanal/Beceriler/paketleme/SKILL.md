---
name: "paketleme"
description: "{{KANAL_ADI}} 6. aşama: montaj öncesi 5 başlık + TO puanı, hipotez test eden kapak A/B, açıklama taslağı, sabit yorum; montaj sonrası yalnızca bölümler ve nihai açıklama."
---

# Aşama 6 — Yayın paketi

Esas: `03_Aktif_Video.md` (kart + {{HEDEF_DIL}} final), `01_Anayasa` (§9 paketleme, §10 sabit metinler),
`02_Defter` (C dersler, D kullanılmış kapak yazıları, F başlık kalıbı kaydı). Metin yeniden yazılmaz; yeni iddia eklenmez.
Bütün yayın metinleri {{HEDEF_DIL}}.

## Mesaj 1 — Montaj öncesi paket
### 1. Başlık (5 aday)
Her aday: `Başlık · kalıp · karakter sayısı · TO puanı /10 · tek cümle gerekçe`. TO kriterleri (her biri 2 puan):
tanınma hızı · ilk 40 karakterde merak ya da replik · arama ve konu netliği · kapakla birlikte çalışma · vaat–içerik uyumu.
≤60 karakter. 5 adayda en az 3 farklı kalıp; kalıp rotasyonu 02_Defter F'ye uyar. Sonuç: 1 seçim + 2 yedek.

### 2. Kapak A ve B
Kart kapak fikri geliştirilir. Kanal kapak stili 01_Anayasa §9'dadır. Her kapak: duygu · tek nesne · kapak yazısı (2–4
kelime) + 1 alternatif · yerleşim · başlıkla ilişkisi · açılış anıyla bağı · İngilizce prompt. A ile B yalnız bir hipotezi
test eder (02_Defter C2). Kurallar: telefon testi (~160 px'de okunur) · kapak yazısı başlığı tekrarlamaz · 02_Defter
D'deki son 6 kapak yazısıyla tekrar yok · görselde yazı üretilmez · Flow yasaklı kelimeleri promptta da kullanılmaz.

### 3. Açıklama taslağı (bölümsüz)
Sıra: ilk 2 satır (~150 kr, konu + doğal arama kelimeleri) · kısa özet (1–3 cümle) · abone satırı (01_Anayasa §10) ·
bölüm bloğu (hedef dildeki karşılığıyla, ör. `Chapters:` / `Capitoli:`; bu mesajda boş) · yorum sorusu · kimlik cümlesi · tam 5 hashtag (biri kanal adı) · yasal uyarı.

### 4. Sabit yorum
Tek, kısa, anlatıcının tonunda bir soru; CTA ile aynı cümle olmaz.

### 5. DEFTER KAYDI (uygulama 02_Defter'e işler)
```
DEFTER KAYDI · {{KOD_ONEKI}}-0X
A: başlık "…" · kapak A/B yazıları · metafor · motor · durum "Yayına hazır"
D: kapak yazıları + hook sahnesi + metafor + kullanılan bilgi kazançları
E: verilen söz (videonun sonundaki soru) · portföy notu
F: açılış tipi · ilk cümle · kal cümlesi kalıbı · köprü tipi · CTA kalıbı · başlık kalıbı
Mekanik etiketler: hook tipi · başlık kalıbı · kapak duygusu · CTA tipi · süre (uygulama ekler)
```
`A:` satırındaki başlık çift tırnak içinde yazılır.

### Mesaj 1 çıktısı
1. `{{KOD_ONEKI}}-0X_6_paket.md`: bölüm 1–5.
2. Sohbet cevabı: en fazla 5 satır özet · kontrol satırları (`Başlık NN kr ≤60 ✓ · 5 adayda ≥3 kalıp ✓ · Kapak A/B tek
   hipotez ✓ · Kapak yazısı tekrarsız ✓ · 5 hashtag ✓ · Yasal uyarı ✓`) · durum kartı `Bekleyen: ONAY 5`.

## Mesaj 2 — Montaj sonrası (uygulama bölüm zamanlarını ve ilk cümleleri verir)
- Yalnız bölüm bloğu ve nihai açıklama. Başlık, kapak ve sabit yorum yeniden yazılmaz.
- Zaman damgaları kesindir: değiştirilmez, yuvarlanmaz, birleştirilmez. Her bölüm için 2–6 kelimelik doğal başlık.
- Çıktı: `{{KOD_ONEKI}}-0X_6_aciklama_final.md` (tam nihai açıklama, bölümler dolu) · kontrol satırı
  (`Bölüm N · 0:00 ✓ · ≥10 sn ✓`) · durum kartı `Aşama 6/6 · tamam`.
