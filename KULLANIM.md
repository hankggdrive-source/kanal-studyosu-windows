# Kanal Stüdyosu · Kullanım

## İlk açılış
1. `1 - Ilk kurulum.cmd` (bir kez), sonra masaüstündeki `Kanal Stüdyosu` kısayolu (ya da klasördeki `Kanal Stüdyosu.vbs`).
2. **Ayarlar:** yazım servisi, AI84 (seslendirme) anahtarı, CapCut taslak klasörü.
   - **Claude Code (abonelik, varsayılan):** bütün yazım işleri bu bilgisayardaki Claude Code ile Pro/Max aboneliğinden
     yapılır, anahtar gerekmez. Claude Code kurulu olmalı ve PowerShell'de `claude` yazıp `/login` ile aboneliğinle
     giriş yapmış olmalısın; "Claude Code'u kontrol et" düğmesi bunu dener. Kullanım sınırı dolarsa adım durur, sınır
     açılınca **Tekrar dene**. Ücret abonelikten; ekranda "abonelik" ve API karşılığı tahmini yalnız bilgi olarak görünür.
   - **OpenRouter:** ücret OpenRouter kredisinden; anahtar ve aylık bütçe gerekir.
   - Görseller (Flow) iki durumda da Claude uygulamasında `kanal-studyosu-flow` becerisiyle yapılır.
3. **+ Kanal ekle:** iki yol var.
   - **Dosyayla ekle (önerilen):** "Şablonu kopyala" de (aynı şablon kurulum klasöründe `Yeni_Kanal_Sablonu.md`),
     bir yapay zekaya (Claude, ChatGPT…) yapıştır ve kanalını birkaç cümleyle anlat. Doldurduğu metni yapıştır ya da
     dosyayı seç, **Oku ve devam et**. Kanal bilgileri ayarlara, anayasa `01_Anayasa.md`'ye yazılır (okuma kodla
     yapılır, ücret yok). Eksik ya da hatalı alanlar kırmızıyla gösterilir. Ses, maskot, müzik ve onaylar o ekranda seçilir.
   - **Elle doldur:** 9 adımlı form. Az kullanılan ayarlar her adımda katlanmış **Gelişmiş** kutusundadır.
   - **Kelime sayısını sormaz:** süre × dilin konuşma hızıyla uygulama hesaplar (ör. 12 dk İtalyanca ~1900–2100).
     Her videodan sonra gerçek ses süresi ölçülür, kanalın hızı buna göre düzelir. Elle ayarlamak için Gelişmiş'te
     "uygulama hesaplasın" işaretini kaldır. Bu sürümden önce açılmış kanalların sayıları değişmez (elle ayarlı kalır).

## Kanal kartı
- **Üretime hazırlık:** eksikler listelenir (ör. ses seçilmedi, dosyalarda doldurulmamış yer var).
- **Kanal dosyaları:** 4 proje dosyası ve 6 beceri. `⟦DOLDUR: …⟧` işaretli yerleri kanalına göre yazıp işareti sil.
  Kaydedince önceki hâl `.yedek\`'e konur.
- **Kanal ayarları:** sihirbazdaki bütün alanlar. Video kodu öneki ve hedef dil ilk videodan sonra değişmez.
- **Klasörü aç:** kanal klasörü Dosya Gezgini'nde açılır. Müzik `Varliklar/Muzik` (montajda buradan rastgele ve farklı parçalar
  videoyu dolduracak kadar seçilir; klasör boşsa video müziksiz yapılır), maskotlar `Varliklar/Maskot`,
  karakter referans görseli `Varliklar/Karakter`.
- **Kanalı sil:** kanal adını yazınca kanal klasörü ve Kanal Stüdyosu'nun o kanal için oluşturduğu CapCut taslakları
  Geri Dönüşüm Kutusu'na taşınır. Başka yerde oluşmuş taslaklara dokunulmaz.

## Birden çok kanal
Üst çubuktaki seçiciyle kanal değiştirilir. Her kanal kendi klasöründe, kendi ayarlarıyla çalışır.

## Kapatma ve yeniden açma
Tarayıcı sekmesini kapatmak uygulamayı kapatmaz. Tamamen kapatmak için sağ üstteki **Kapat**. Uygulama açıkken simgesine
yeniden tıklarsan ikinci kopya başlamaz, açık olan ekran gelir.

## Üretim
Her şey seçili kanalın klasöründe ve ayarlarıyla olur.
1. **Sıradaki üretim** kartında iki yol var. Kanalın zorunlu eksikleri (ör. ses seçilmedi) varsa düğme kapalıdır.
   - **Konudan başla:** istersen konu isteğini yaz, **Üretime başla**.
   - **Hazır metinle başla:** metnin hazırsa dilini seç (Türkçe ya da kanalın dili) ve yapıştır. Tek adımda konu kartı
     çıkarılır, Kanal Defteri'ne göre çakışma kontrol edilir, metin sahne paragraflarına bölünüp etiketlenir. Metnin
     kelimelerine dokunulmaz; uygulama kelime kelime denetler. Türkçe metinde sonra 4. aşama yazılır; kanalın dilindeki
     metinde doğrudan 5. aşamaya geçilir. Atlanan aşamalar adım çubuğunda "atlandı" görünür.
   - **Bu üretimde onay iste:** ONAY 2, 4 ve 5'i bu üretim için açıp kapatabilirsin; varsayılanlar Kanal ayarları ›
     Onaylar'dan gelir. ONAY 1 ve 3 her zaman istenir. Onayı kapalı aşama, kod kontrolleri temizse beklemeden geçer.
2. Yazım aşamaları: 1 Konu → 2 Araştırma → 3 Türkçe senaryo → 4 Hedef dil (hedef dil Türkçe ise yok) → 5 Sahne paketi
   → 6 Paketleme. Onaylı aşamalarda dosyaları oku; gerekirse **Metni burada düzenle** (ücretsiz, model çağrılmaz),
   **Düzeltme iste** ya da **ONAY ver**.
3. **Görseller (Flow):** Claude masaüstünde yeni sohbet aç, ekrandaki komutu yapıştır. Bunun için paketteki
   `kanal-studyosu-flow.zip` becerisini Claude'a bir kez yükle (Ayarlar › Beceriler). Ajan bitirince uygulama kendisi
   devam eder: ses, sahne videoları, CapCut taslağı (CapCut kapalı olmalı), bölümler, son kontrol, rapor.
4. Bitince CapCut'ta `<ÖNEK>-0X` taslağını aç, kontrol et, dışa aktar. Silme adayları için "Taşı" ya da "Kalsın".
   **Üretimi kapat** ile ana ekrana dön.
- **Durdur:** çalışan adımı durdurur; **Tekrar dene** kaldığı yerden sürer.
- **Üretimi iptal et:** hiçbir şey silinmez; dosyalar kanalın `Arsiv/<kod>_iptal_<tarih>/` klasörüne gider, aynı kod
  yeniden kullanılır.
- **Müziği yeniden yap** (bitti ekranında): müziği beğenmezsen yeni rastgele parçalarla yeniden yapar. CapCut kapalı
  olmalı; eski müzik arşive kopyalanır, silinmez.
- **Videolar** listesinde biten videonun **Rapor** düğmesi üretim raporunu ve maliyet dökümünü gösterir.
- Üretim sürerken kanal değiştirilemez.

## İlk kurulum boş gelir
Uygulama hiç kanal olmadan açılır. "+ Kanal ekle" ile ilk kanalını oluştur.
