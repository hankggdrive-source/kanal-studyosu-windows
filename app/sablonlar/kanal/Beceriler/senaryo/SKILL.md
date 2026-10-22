---
name: "senaryo"
description: "{{KANAL_ADI}} 3. aşama: onaylı outline'dan tam Türkçe senaryo yazar, no-ai-slop ve humanizer mantığını Türkçeye uyarlayarak kendini denetler."
---

# Aşama 3 — Tam Türkçe senaryo + Türkçe öz-denetim

Esas: `01_Anayasa` (§2 anlatıcı, §4 metot, §5 yapı, §6 tekrar yasağı, §8 güvenlik, §12 metafor bankası), `02_Defter F`,
onaylı konu kartı ve outline. Bu metin sonra {{HEDEF_DIL}} diline yeniden yazılacak; çeviri yapılmaz.

## Adım 1 — Yazım
- **Uzunluk:** Türkçe çalışma metni için KANAL AYARLARI'ndaki kelime aralığı (etiketler sayılmaz).
- **Paragraf = anlam birimi.** Her paragrafın başında bir senaryo etiketi bulunur (karakter sahnesi / metafor / şema;
  adları KANAL AYARLARI'nda). İlk ~30 saniyedeki paragraflara ayrıca ilk-30-sn etiketi eklenir (~6 beat). Paragraflar
  1–4 cümle; sonraki aşamada her paragraf bir sahne olacak.
- **Outline'a sadık kal:** bölüm sırası, açılış tipi ve kapak anı (ilk 8 sn), 4. paragrafta kal cümlesi, metaforun 3
  görünüşü, bilgi kazancı yerleri ve iddia sınıfları ("Kullanma" iddiaları metne girmez, "Dikkatli ifade" olanlar ihtimal
  kipinde), orta-video açık döngüsü, güvenlik cümlesi (varsa), CTA ve köprü tipi, sabit imza (01_Anayasa §5, {{HEDEF_DIL}}
  olarak yazılır).
- **Anlatıcının sesi:** 01_Anayasa §2'deki gibi.
- **Somut:** Her soyut fikir bir gündelik sahneye bağlanır; soyut cümleden sonra hemen örnek gelir.
- **Kaynak:** doğrulanmış bilgi cümleleri outline'daki doğru ifadeyle. Künye, sayı ve yüzde yok. Emin olunmayan iddia
  metne girmez ya da ihtimal kipinde; metinde köşeli parantezli işaret bırakılmaz. Doğrulanması gereken iddia sohbet
  cevabındaki «Açık noktalar» satırında paragraf numarasıyla.
- **Tempo:** ortalama cümle ~9–12 kelime, uzunluklar çeşitli.

## Adım 2 — Türkçe öz-denetim (no-ai-slop + humanizer mantığı)
Önce yaz, sonra göstermeden denetle ve düzelt. Kalıbı ve süsü at, somutlaştır, anlatıcının sesini koru.
1. İkili karşıtlık ("Bu X değil, Y.") en fazla 2. 2. Şişirme ("derin bir dönüşüm", "bir yolculuk"). 3. Boş geçişler
("aslında", "gerçekten", "şunu belirtmek gerekir ki"). 4. Üçleme alışkanlığı. 5. Sahte içgörü girişleri ("Kimsenin sana
söylemediği…"). 6. İki nokta ile dramatik açıklama. 7. Kesik dram zinciri (3+ çok kısa cümle) en fazla bir kez.
8. Kendi sorusunu cevaplama en fazla 2. 9. Aforizma formülü (final dışında). 10. Genel kapanış ve özet tekrarı.
11. Eş anlamlı döndürme. 12. Belirsiz otorite ("uzmanlar diyor ki"). 13. Tekdüze ritim. 14. Uzun tire ve süslü noktalama.
15. Taşınabilirlik testi: cümle başka videoya değişmeden taşınabiliyorsa dolgudur. 16. Kanal kalıp sayacı (02_Defter F).
Korunacaklar: sıcaklık, gerçek konuşma gibi diyaloglar, tek kısa vurgu cümleleri, somut detaylar, final aforizması, imza.
Yeni bilgi ya da iddia eklenmez.

## Adım 3 — Metot kontrolü (yazdıktan sonra, göstermeden)
Outline ve kartla karşılaştır: metodun her adımı (01_Anayasa §4) yerinde mi · tek ana metafor ve 3 görünüşü · orta-video
açık döngüsü · CTA videonun duygusuna uygun mu · önceki videolarla (02_Defter D/F) aynı sonuç ya da kalıp tekrar ediyor mu
· güvenlik bağlamı. Düzeltmeler sessizce uygulanır.

## Çıktı
1. `{{KOD_ONEKI}}-0X_3_senaryo_tr.md`: yalnız etiketli tam metin; sonunda yalnız `Kelime: NNNN`.
2. Sohbet cevabı: en fazla 5 satır özet · kontrol satırları (`Kelime NNNN ✓ · Paragraf NN · İlk 30 sn N · Kapak anı ilk
   8 sn ✓ · Kal cümlesi ¶4 ✓ · Metafor 3 görünüş ✓ · Bilgi kazancı N ✓ · Öz-denetim: N kalıp düzeltildi`) · durum kartı
   `Bekleyen: ONAY 3 | Sonraki: ceviri`.

## Düzeltme turu
Yalnızca değişen paragraflar ("¶12 yeni: …"); kelime sayısı yeniden verilir.
