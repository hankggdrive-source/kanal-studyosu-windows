---
name: "kanal-studyosu-flow"
description: "Kanal Stüdyosu'nun hazırladığı flow_istek klasörünü okuyup Google Flow'da sahne görsellerini beşerli partilerle üretir, indirip flow_cikti klasörüne koyar ve BITTI.json yazar. Kanal, karakter, görsel oranı ve model istek.json'dan gelir. Kullanıcı 'kanal-studyosu-flow' ve bir klasör yolu verince kullan."
---

# kanal-studyosu-flow — yalnız Flow görsel üretimi (bütün kanallar)

Görevin tek: verilen klasördeki isteğe göre Flow'da görsel üretmek. Konu, senaryo, prompt ya da proje dosyası işi YOK. Promptları değiştirme, yeniden yazma, çevirme.

Kanala göre değişen her şey `istek.json`'dadır; bu becerideki `<…>` yerlerini oradan doldur:
- `<KARAKTER>` = `istek.json` → `karakter` (ör. `@Mila`). **Boşsa** karakter ekleme adımını atla; promptlarda karakter yoktur.
- `<ORAN>` = `ayarlar.oran` (`16:9` yatay ya da `9:16` dikey) · `<MODEL>` = `ayarlar.model` (tam adıyla) · `<KOD>` = `kod`.

## 0. Hazırlık — bütün izinler en başta, tek seferde
- Bilgisayar araçları (komut/dosya) ve Claude tarayıcısı gerekli. Yoksa tek mesajla dur: "Bu sohbette bilgisayar/tarayıcı araçları yok; bilgisayarın seçili olduğu yeni bir sohbet aç."
- Önce `anthropic-skills:built-in-browser` becerisini oku.
- İlk mesajın tek satır olsun: "Şimdi gereken izinleri bir kerede isteyeceğim (klasörler ve Flow sitesi). Her birinde 'bu sohbet boyunca / her zaman izin ver' seçeneğini seçersen üretim bitene kadar tekrar sormam."
- Sonra gereken bütün erişimleri hemen, arka arkaya aç (izin istekleri ilk dakikada toplansın, üretimin ortasına dağılmasın):
  1. Verilen istek klasörünü listele ve oku: `TALIMAT_AJAN.md`, `istek.json`, `promptlar.txt` (`eksikler.json` varsa yalnız oradaki sahneleri üret).
  2. İstek klasörünün yanındaki `flow_cikti/` klasörüne yazabildiğini dene (yoksa oluştur; boş `.yazma_testi` dosyası yaz, sonra sil).
  3. İndirilenler klasörünü (`~/Downloads`) listele (proje zip'i oraya iner).
  4. Tarayıcıda Flow'u aç (https://labs.google/fx/tools/flow).
  Bunlar bitince "İzinler tamam, üretime başlıyorum." yaz ve bir daha izin isteme gerektirmeyen adımlarla devam et.
- Kalıcı izin seçeneğini kullanıcı seçer; sen izin pencerelerine tıklama, izin seçme.
- Şifre girme. Flow oturumu kullanıcının tarayıcısında açık; düşerse dur ve giriş iste.

## 1. Flow projesi ve karakter
1. Flow → pencere 1440x900. `/New project|Yeni proje/` düğmesi `.click()`.
2. Ad: `input[aria-label="Düzenlenebilir metin"]` setter + Enter keydown → `istek.json` → `proje_adi`.
3. Karakter (yalnız `<KARAKTER>` doluysa): `pc(button[aria-label="İçerik öğelerini istem kutusuna ekle"])` → `pc(mat-select[role=combobox] div)` → adı `<KARAKTER>`'in `@` olmadan hâli olan `mat-option` (büyük/küçük harf fark etmez) → `pc(/İsteme ekle/)`. Kutunun üstünde karakter resmi görünmeli. Listede yoksa dur ve kullanıcıya söyle: "Flow'da <KARAKTER> karakteri yok; önce Flow'a ekle."
- `eksikler.json` turunda yeni proje AÇMA; aynı projede devam et.

## 2. Ayarlar ve ajan talimatı
1. `pc(button[aria-label="Ayarlar"])` → "Hiçbir zaman", resim x1, model tam "<MODEL>" (benzer adlı başka sürüm değil), oran <ORAN>, Kaydet; radio'larla doğrula.
2. `pc("Ajan talimatları")` → "Talimat ekle" → başlık `Üretim kuralları`, metin = `istek.json` → `flow_ajan_talimati`; `[role=switch]` aria-checked="true" → "Bitti".

## 3. Beşerli partiler (ASLA hepsi tek mesajda değil)
- Her parti `istek.json` → `partiler[k]`. Mesaj: "Sıradaki promptları sırayla üret (her biri <ORAN>, x1, <MODEL>) ve üretilen görselleri sırayla <sahneler> olarak adlandır. Hata olursa bir promptu en fazla 3 kez dene. Onay bekleme.\n\n" + promptlar (aralarında boş satır).
- Yazma (ProseMirror): DataTransfer + `ClipboardEvent('paste')`; `pm.innerText.length === MESAJ.length` kontrolü.
- Gönderme = Enter: imleci sona al (`pm.focus(); const s=getSelection(); s.selectAllChildren(pm); s.collapseToEnd();`) → `key Return` → 4 sn sonra `button[aria-label="Durdur"]` var mı.
- Flow'da tıklamalar pointer olaylarıyla: `const pc=el=>['pointerdown','mousedown','pointerup','mouseup','click'].forEach(t=>el.dispatchEvent(new (t.startsWith('pointer')?PointerEvent:MouseEvent)(t,{bubbles:true})));`
- Parti başına ~2,5 dk bekle (`sleep` ≤175 sn), `Durdur` kaybolunca sonraki parti.
- İlk ve ikinci partiden sonra ekran görüntüsü: görseller <ORAN> yönünde mi (16:9 yatay, 9:16 dikey) ve karakter (varsa) tutarlı mı? Kare çıkarsa dur, ajan talimatını kontrol et.
- "Tekrar dene"ye BASMA (çift üretim). Eksik kalanları yeni mesajla gönder.

## 4. İndirme ve teslim
1. `pc(button[aria-label="Diğer seçenekler"])` → `pc(/Projeyi indir/)`.
2. İndirilen zip'i (boyutu sabitlenince) `flow_cikti/` klasörüne kopyala (istek klasörünün yanında). Zip açılamıyorsa görselleri tek tek de koyabilirsin; adları `sahneNNNN_*.jpg` olmalı.
3. Son iş: `flow_cikti/BITTI.json` yaz: `{"kod": "<KOD>", "uretilen": <sayı>, "notlar": "<varsa kısa not>"}`.
4. Pencereyi `resize_window {preset:"desktop"}` ile geri al. Kullanıcıya tek satır: "Flow bitti: N görsel flow_cikti'de."

## 5. Sorun olursa
- Bir sahne Flow politikasına takılırsa ya da 3 denemede çıkmazsa promptu KENDİN DEĞİŞTİRME. `flow_cikti/SORUN.md` yaz: sahne numarası + Flow'un mesajı (aynen). Sonra diğer sahnelerle devam et ve sonunda `BITTI.json` yaz. Uygulama promptu Aşama 5'e düzelttirir.
- Hesap uyarısı (otomasyon/kullanım) gelirse hemen dur, `SORUN.md`'ye yaz ve kullanıcıya söyle; uygulamada yarı elle yol var.

## Bilinen sorunlar
| Sorun | Çözüm |
|---|---|
| Tüm promptlar tek mesajda → kare görseller, proje kilitlendi | Beşerli partiler. |
| Karakter referansıyla 1:1 kare | Ajan talimatı + her mesajda "<ORAN>"; ilk partiden sonra kontrol. |
| Tıklama tutmuyor / gönder basılmıyor | `pc()` pointer olayları; gönderme Enter. |
| Karakter çipi ilk gönderimden sonra kalkıyor | Sorun değil; ajan referansı hatırlıyor. |
| "Tekrar dene" çift üretim | Basma; eksikleri yeni mesajla gönder. |
| Kaydet penceresi (Claude uygulaması) | İndirme hemen `~/Downloads/.Q6L2SF6YDW.com.anthropic.claudefordesktop.*` olarak düşer; en yenisini kopyala. Kullanıcıya: "Açık kalan Kaydet pencerelerini İptal ile kapatabilirsin." |
