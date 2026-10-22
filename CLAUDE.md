# Kanal Stüdyosu (Windows) · Claude Code için rehber

Bu klasör çalışan bir Kanal Stüdyosu kurulumudur: her YouTube kanalı için fikirden CapCut taslağına video üreten yerel
bir uygulama (Python sunucu + tarayıcı arayüzü). Kullanıcı yazılımcı değil; onunla **sade Türkçe**, teknik terimsiz
konuş. Bu dosyayı okuduktan sonra işe göre aşağıdaki haritadan ilgili dosyalara bak. Bütün ayrıntılı tarif ve kodun
tamamı `SPECS.md`'de (≈560 KB); hepsini okuma, ilgili bölümü ara (ör. `## 10.9`, `### 10.14`, dosya adı).

## Çalışma kuralları
1. **Önce plan, sonra kod.** Kullanıcıya ne değişeceğini kısa bir listeyle anlat, onay al, sonra yap.
2. **Her değişiklikten sonra testleri çalıştır** (aşağıda). Kırmızı test varken "bitti" deme; testi silme ya da atlatma.
3. **Kullanıcının verisine dokunma:** `Kanallar\` (kanalların ayarları, metinleri, videoları) ve `Sistem\` (ayarlar,
   maliyet, kayıt) kullanıcının verisidir. Kod değişikliği `app\` ve `tests\` içinde yapılır. Kanal dosyalarını
   (beceriler, anayasa) değiştirmek gerekiyorsa önce sor; uygulama zaten önceki hâli `.yedek\`'e alır.
4. **Hiçbir şeyi kalıcı silme.** Uygulama silinecekleri `Silinecekler\` klasörüne ya da Geri Dönüşüm Kutusu'na taşır
   (`cop.py`, `dosya_duzeni.py`); bu kuralı koru.
5. **API anahtarı, şifre, token** hiçbir dosyaya yazılmaz. Anahtarlar Windows Kimlik Bilgisi Yöneticisi'nde (`keyring`,
   servis `studio.kanal`). Kullanıcıdan anahtar isteme; uygulamanın Ayarlar ekranına girmesini söyle.
6. **CapCut taslaklarına yalnız CapCut kapalıyken** dokunulur (`capcut_zinciri.py` bunu denetler). Kanal Stüdyosu'nun
   oluşturmadığı CapCut taslaklarına hiçbir durumda dokunma.
7. Windows'a özgü kuralları koru: süreç denetimi `os.kill(pid, 0)` ile yapılmaz (Windows'ta süreci öldürür;
   `sistem_win.surec_yasiyor`), ImageMagick `magick` ile çağrılır (Windows'un `convert.exe`'si başka bir programdır),
   alt süreçler konsol penceresi açmaz (`sistem_win.gizli`), dosyalar UTF-8 okunur/yazılır.
8. Değişiklikten sonra uygulamayı yeniden başlatmak gerekir: arayüzde sağ üstteki **Kapat**, sonra masaüstündeki
   kısayol (ya da `Kanal Stüdyosu.vbs`).

## Testler
Uygulamanın kendi Python ortamı ilk açılışta `Sistem\.venv`'e kurulur. Kurulum klasöründe (bu dosyanın olduğu yer):

```powershell
.\Sistem\.venv\Scripts\python.exe -m unittest discover -s tests
```

Testler kendi geçici klasörlerinde çalışır, kullanıcının kanallarına dokunmaz. FFmpeg gerektirenler FFmpeg yoksa
atlanır. `tests\veri\` içindeki kanal ve defter dosyaları **uydurma örnek veridir** (adları eski bir test kanalından
kalma). Yeni bir özellik eklediğinde ona da test yaz (ör. `tests\test_kanal_sablonu.py` örnek alınabilir).

## Değişiklikleri takip (önerilir)
Klasörde `.git` yoksa, ilk değişiklikten önce kullanıcıya sor ve `git init` + ilk kayıt yap (`.gitignore` hazır:
`Sistem\` ve `Kanallar\` takip edilmez). Böylece her değişiklik geri alınabilir. Her anlamlı değişiklikten sonra
kısa, Türkçe bir mesajla kaydet.

## Klasör haritası
- `Kanal Stüdyosu.vbs` → `app\windows\baslat.ps1`: Python ortamını kurar/onarır, sunucuyu `pythonw` ile başlatır.
- `1 - Ilk kurulum.cmd` → `app\windows\ilk_kurulum.ps1`: winget ile Python, FFmpeg, ImageMagick; masaüstü kısayolu.
- `app\kanal_studyosu\` (uygulama):
  - `__main__.py` başlatma · `sunucu.py` yerel HTTP sunucu ve bütün `/api/...` uç noktaları · `tek_kopya.py`
  - `ayarlar.py` genel ayarlar, sürüm (`SURUM`), anahtarlar · `yollar.py` klasörler · `kayit.py` kayıt
  - `kanallar.py` kanal ekleme/doğrulama/silme, kelime aralığı hesabı · `kanal.py` seçili kanal katmanı
    (modele giden KANAL AYARLARI bloğu: `ayarlar_blogu`) · `kanal_sablonu.py` tek dosyayla kanal ekleme
  - `uretim.py` üretim akışı (adımlar, onaylar, otomatik düzeltme, durum kaydı) · `asamalar.py` aşama tanımları ve
    modele giden mesajlar · `kontroller.py` modelsiz kod kontrolleri · `cikti.py` model cevabını dosyalara ayırma ·
    `metin.py` paragraf/kelime/yama
  - `llm.py` model katmanı → `claude_code.py` (abonelik, varsayılan) ya da `openrouter.py` · `maliyet.py`
  - `flow.py` görsel adımı (Claude masaüstündeki `kanal-studyosu-flow` becerisiyle klasör üzerinden)
  - `studio_baglanti.py` ses (AI84 → ElevenLabs, `ai84.py`) ve sahne videoları (ffmpeg) · `ses_kenar.py`
  - `capcut_zinciri.py` + `araclar.py` montaj betiklerini çağırır · `son_kontrol.py` rapor · `defter.py` Kanal Defteri
  - `onkontrol.py` açılış kontrolü · `cop.py`, `dosya_duzeni.py` silme politikası · `sistem_win.py` Windows işleri
  - `web\index.html`, `web\app.js`, `web\stil.css` arayüz (çerçevesiz, düz JavaScript)
- `app\araclar\` montaj betikleri (CapCut taslağı, müzik, maskot, altyazı, kontroller); `ortak.py` ortak yardımcı.
- `app\config\varsayilan.json` genel varsayılanlar (modeller, fiyatlar) · `kanal_varsayilan.json` yeni kanal varsayılanları.
- `app\sablonlar\kanal\` yeni kanala kopyalanan beceriler (`Beceriler\<aşama>\SKILL.md`) ve proje dosyaları.
- `app\skills\kanal-studyosu-flow\` Claude masaüstü uygulamasına yüklenen Flow becerisi (zip'i pakette).
- `Kanallar\<kısaltma>\` (kullanıcı verisi): `kanal.json`, `Beceriler\`, `Proje_dosyalari\` (00 Yönetici,
  01 Anayasa, 02 Defter, 03 Aktif video), `Varliklar\` (Muzik, Maskot, Karakter), `Uretim\`, `Videolar\`, `Arsiv\`.

## Üretim hattı (kısaca)
Hazır metin (isteğe bağlı) → 1 Konu → 2 Araştırma → 3 Türkçe senaryo → 4 Hedef dil (kanal Türkçe ise yok) →
5 Sahne paketi → 6 Paketleme → Görseller (Flow, kullanıcı Claude uygulamasında beceriyi çalıştırır) → Ses ve sahne
videoları → CapCut taslağı → Bölümler → Son kontrol → Kapanış (defter yenilenir). ONAY 1 ve 3 her zaman istenir;
2, 4, 5 kanal ayarından ve üretimin başında seçilir. Ayrıntı: `SPECS.md` bölüm 10.

## Sık özelleştirmeler: nereye bakılır
- **Bir kanalın yazım tarzı / kuralları:** o kanalın `Kanallar\<k>\Beceriler\<aşama>\SKILL.md` ve
  `Proje_dosyalari\01_Anayasa.md` (kod değişikliği gerekmez; uygulamadaki "Kanal dosyaları" ekranından da düzenlenir).
- **Yeni kanallara gelecek varsayılan beceriler:** `app\sablonlar\kanal\`.
- **Kanal ayarlarına yeni alan:** `app\config\kanal_varsayilan.json` + `kanallar.dogrula` + arayüzde `app.js`
  içindeki `bolumler()` + modele gidecekse `kanal.ayarlar_blogu` + gerekiyorsa `kanal_sablonu.ALANLAR`.
- **Model / efor / fiyat:** `app\config\varsayilan.json` ve kanal ayarlarındaki "Modeller ve bütçe".
- **Bir kontrolün kuralı:** `kontroller.py` (kodla yapılan) ya da `son_kontrol.py`.
- **Montaj (altyazı, müzik, maskot, CapCut):** `app\araclar\` ve `capcut_zinciri.py`.
- **Ekran metinleri ve düzen:** `web\app.js`, `web\stil.css`.

Sürüm değiştirirsen `ayarlar.py` içindeki `SURUM`'u da artır (ör. `1.2.3-windows` → `1.2.4-windows`).
