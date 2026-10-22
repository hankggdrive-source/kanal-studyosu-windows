---
name: "konu"
description: "{{KANAL_ADI}} 1. aşama: önceki videonun Studio verisinden gözlem çıkarır, Kanal Defteri'ne göre konuyu seçer, konu kartı yazar."
---

# Aşama 1 — Ders + Konu kartı

Önce proje dosyalarını oku: `00_Yonetici.md` (düzen, israf kuralları, durum kartı), `01_Anayasa.md` (kurallar),
`02_Defter.md` (hafıza). Sayısal sınırlar uygulamanın verdiği KANAL AYARLARI bölümündedir.

## Girdi
- Video kodu ({{KOD_ONEKI}}-0X).
- Varsa bir önceki yayınlanmış videonun YouTube Studio verisi: gösterim, TO, izlenme, ortalama izlenme süresi, ilk 30 sn
  tutma, düşüş noktaları, trafik kaynakları, öne çıkan yorumlar.
- Varsa kullanıcının konu isteği. Kullanıcı konu verdiyse onu kullan; aday listesi atlanır.

## Adım 1 — Yayın dersi (veri geldiyse)
1. Veriyi o videonun mekanik etiketleriyle eşleştir (02_Defter A/F: hook tipi, başlık kalıbı, kapak, metafor, CTA, süre).
2. Tıklanma sorunu mu (başlık/kapak), izlenme sorunu mu (ilk 30 sn / orta)?
3. **En fazla 3 gözlem.** Tek videonun verisinden kalıcı kural çıkarılmaz; gözlem 02_Defter C2'deki bir hipotezi
   destekler, zayıflatır ya da yeni hipotez olur. Kalıcı ders için en az 3 video ya da net bir Test & compare gerekir.
4. Açıklama TO'nun nedeni sayılmaz. Gösterim çok düşükse (yeni kanal) TO yorumunda temkinli ol.
Veri yoksa bu adımı tek satırla geç: "Studio verisi yok."

## Adım 2 — Konu seçimi
Sıra: (1) verilen söz (02_Defter E) → (2) portföy dengesi (01_Anayasa §1 damarları) → (3) fikir havuzu (02_Defter G).
- **Kaynak ilkesi (01_Anayasa §13):** konu kanıtı en az 2 farklı kanalda ortalamanın belirgin üstünde izlenmiş benzer
  içerikten gelir. Rakip başlığı ve metni çevrilmez; yalnız konu ve duygu not edilir. Sayı uydurma; emin değilsen
  "tahmini" yaz. Web arama aracı varsa kullan.
- **Konu testi (01_Anayasa §4).** Unsurlardan biri eksikse konu seçilmez ya da tamamlanır.
- **Tekrar kontrolü:** konu, metafor, hook sahnesi ve kapak yazısı 02_Defter D'de kullanılmamış; açılış tipi son 3
  videodan farklı (02_Defter F); başlık kalıbı rotasyona uygun.
- **Güvenlik bağlamı:** hassas bir bağlama dokunuyorsa karttaki "Riskli ifadeler" alanında belirt (01_Anayasa §8).

## Adım 2b — Aday listesi (kullanıcı konu vermediyse)
5–6 aday, her biri tek satır: `N. Başlık fikri (kalıp) · Motor · Merak/Duygu/Özgünlük 1–5 · kanıt · ana risk`.
En güçlü 3'ü ★ ile işaretle. Liste sohbet cevabında verilir, karta girmez.

## Adım 3 — Konu kartı (karakter sınırı KANAL AYARLARI'nda)
Kart kısa ve karar vericidir; senaryo cümlesi yazılmaz.
```
KONU KARTI · {{KOD_ONEKI}}-0X · <çalışma adı>
Başlık ({{HEDEF_DIL}}, ≤60 kr; kalıp): … (NN kr)
Alternatif 1 / 2: … (NN kr) · … (NN kr)
Motor · Puan (Merak/Duygu/Özgünlük 1–5):
Günlük durum (izleyicinin bugün yaşadığı) · Köken / neden:
Kanıt (çapraz, 2+ kanal): …  |  Boşluk: …
Vaat (tek cümle, TR):
Ana metafor + 3 görünüş (kapalı / açıklayan / dönüşmüş):
Açılış tipi (01_Anayasa §6 harfi) + açılış anı (ilk 8 sn = kapak anı):
Kapak A: duygu, tek nesne, yerleşim · yazı (2–4 kelime) · Kapak B: A'dan farkı + test edilen hipotez · yazı
Bilgi kazancı adayları (3–5; doğrulanmamış olanın sonuna «doğrulanmadı»):
CTA tipi · Köprü tipi · Sonraki doğal soru:
Riskli ifadeler (kaçın) · Güvenlik bağlamı:
Neden seçildi (3 madde):
```
Sınır aşılırsa en uzun alanları kısalt. Hiçbir alan boş kalmaz. Kartta köşeli parantezli iç işaret kullanılmaz.

## Adım 4 — Defter değişiklikleri
`{{KOD_ONEKI}}-0X_1_defter_degisiklikleri.md` dosyasına yalnızca değişecek satırları bölüm harfiyle yaz (A yeni video
satırı "Üretimde" · B performans · C hipotezler · D kullanılmışlar · E sözler/portföy · F başlık kalıbı · G havuz).
Defterin tamamını yeniden yazma.

## Çıktı
1. `{{KOD_ONEKI}}-0X_1_konu_karti.md` ve `{{KOD_ONEKI}}-0X_1_defter_degisiklikleri.md`.
2. Sohbet cevabı: aday listesi (konu verildiyse yok) · en fazla 5 satır özet · kontrol satırları
   (`Kart: NNNN kr ✓ · Konu testi ✓ · Kanıt 2+ kanal ✓ · Metafor yeni ✓ · Açılış tipi son 3'ten farklı ✓ · Kapak yazısı tekrarsız ✓`)
   · durum kartı `Bekleyen: ONAY 1 | Sonraki: arastirma`.

## Düzeltme turu
Yalnızca değişen alanları yaz ("Alan: yeni değer").
