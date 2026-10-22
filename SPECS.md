# Kanal Stüdyosu (Windows) · Teknik şartname (SPECS)


Mac sürümünden uyarlanmış (son aktarım Mac **1.2.3**), kendi başına duran kopya (`app/`). Mac sürümü (`../kanal_studyosu`)
bundan etkilenmez; Mac'teki değişiklikler buraya **kendiliğinden gelmez**. Bir değişikliğin Windows'a taşınması
istendiğinde ayrıca yapılır ve aşağıdaki tabloya yazılır.

| Windows sürümü | Mac tabanı | Not |
|---|---|---|
| 1.2.2-windows | 1.2.2 | İlk uyarlama (22 Eki 2026) |
| 1.2.3-windows | 1.2.3 | Tek dosyayla kanal ekleme (şablon + anayasa), kelime sayısı süreden ve gerçek sesten, katlanan Gelişmiş ayarlar (22 Eki 2026) |

## Geliştirme paketi
Zip'te `CLAUDE.md` (Claude Code'un klasörde açılınca okuduğu rehber), `Gelistirme.txt` (kullanıcıya adımlar),
`.gitignore` (Sistem\ ve Kanallar\ takip edilmez) ve `tests\` vardır. `tests\` gerçek bir kanalın
metinlerine ihtiyaç duymayan test dosyalarıdır (`build_paket.PAKET_TESTLERI`); örnek kanal ve defter
`tests/ornek_veri/`'deki uydurma veridir. Kaynakları `gelistirme/`; CI paketin testlerini paketin kendi Python
ortamıyla da çalıştırır.

## Mac'ten farklar
- Başlatıcı: `Kanal Stüdyosu.vbs` → `app/windows/baslat.ps1` (gizli PowerShell; Python ortamını `Sistem\.venv`'e
  kurar, bozuksa `--clear` ile onarır; sunucu `pythonw` ile konsolsuz). İlk kurulum: `1 - Ilk kurulum.cmd` →
  `app/windows/ilk_kurulum.ps1` (winget: Python 3.12, FFmpeg, ImageMagick; Claude Code isteğe bağlı; masaüstü kısayolu).
- `kanal_studyosu/sistem_win.py`: süreç denetimi (Windows'ta `os.kill(pid, 0)` süreci sonlandırır), Dosya Gezgini,
  `tasklist` ile CapCut, Windows Kimlik Bilgisi Yöneticisi (`keyring`), CapCut yolları, alt süreçlerde konsol gizleme.
- Geri Dönüşüm Kutusu (`send2trash`); anahtarlar `keyring`; Pillow uygulamanın ortamında (`requirements.txt`).
- `odak_izgara.sh`, `maskot_seffaf.sh` → Python (`magick`; yoksa `convert`/`montage`).
- CapCut taslağı: `draft_info.json` ve `draft_content.json` birlikte (kök + Timelines, `.bak`) yazılır, okurken hangisi
  varsa; taslak kökü `C:/Users/...` biçiminde; şablondaki Mac CapCut önbellek yolları (efekt, yazı tipi)
  `%LOCALAPPDATA%\CapCut\User Data`'ya çevrilir. CapCut taslak klasörü varsayılanı
  `%LOCALAPPDATA%/CapCut/User Data/Projects/com.lveditor.draft`.
- Claude Code: `claude.exe` ya da npm `claude.cmd` (cmd /c ile) bulunur.
- Bütün betikler `PYTHONUTF8=1` ile çalışır (Türkçe/Çince karakterler).

## Geliştirme
Testler: `python -m unittest discover -s windows/tests` (Linux'ta da çalışır; Windows'ta GitHub Actions
`windows.yml`). Paket: `python windows/build_paket.py` → `windows/dist/Kanal Stüdyosu (Windows).zip`.


---

> Aşağıdaki ortak tarif Mac sürümü 1.2.3'ün şartnamesidir; Windows farkları yukarıdadır.


Bu belge Kanal Stüdyosu'nun güncel hâlinin tam tarifidir: ne yaptığı, klasör düzeni, kanal ayarları, ekranlar, arayüz
uç noktaları ve **bütün kaynak kodu** (Ek A). Ek A depodaki koddan otomatik üretilir:
`python3 scripts/specs_olustur.py` → `SPECS.md` (paket oluşturulurken kendiliğinden çalışır).
Tasarım ve yol haritası: `PLAN.md`.

**Sürüm durumu:** tam sürüm. Aşama 1–5 tamam: kurulum klasörü ve kanal işlemleri; tek kanallı ilk sürümün üretim hattının
tamamı (6 yazım aşaması, Flow devri, ses ve video, CapCut taslağı, bölümler, son kontrol, kapanış) kanal ayarlarıyla
çalışır; hazır metinle başlama; üretim başına onay seçimi; denge testleri; paket. Kurulum boş gelir (hiç kanal yok).

---

## 1. Amaç ve sınırlar
- Her YouTube kanalı için tek kanallı ilk sürümdeki üretim hattını (6 yazım aşaması → Flow → ses ve video → CapCut →
  bölümler → son kontrol → kapanış) çalıştıran macOS uygulaması. Python 3 standart kütüphanesi + yerel HTTP sunucusu +
  tarayıcıda Türkçe arayüz. Yazım servisi: Claude Code (abonelik, varsayılan) ya da OpenRouter; Python kütüphanesi
  `anthropic` yalnız OpenRouter için gerekir.
- Dil akışı her kanalda aynı: konu, araştırma, senaryo **Türkçe** → senaryo **hedef dilde** yeniden yazılır → hedef
  dilde seslendirilir. Hedef dil Türkçe ise 4. aşama atlanır.

## 2. Klasör düzeni
Kurulum klasörü = `.app`'in bulunduğu klasör (başlatıcı `KANAL_STUDYOSU_KOK` ortam değişkeniyle verir; geliştirmede
depo içindeki `calisma/`). İlk açılışta `Sistem/` ve `Kanallar/` kurulur; var olan hiçbir şeye dokunulmaz.
```
<Kurulum>/  Kanal Stüdyosu.app · SPECS.md · KULLANIM.md · 1 - Ilk kurulum.command
  Sistem/   ayarlar.json · maliyet.jsonl · aktif.json · kayit.log · .venv/
  Kanallar/<kisaltma>/
    kanal.json · taslaklar.json · .yedek/
    Proje_dosyalari/ 00_Yonetici.md 01_Anayasa.md 02_Defter.md 03_Aktif_Video.md
    Beceriler/ konu arastirma senaryo ceviri sahne paketleme  (her birinde SKILL.md)
    Varliklar/ Muzik Maskot Karakter son_ekran
    Videolar/ Arsiv/ Uretim/ Silinecekler/ Defter_arsivi/
```
Anahtarlar: macOS Anahtar Zinciri, servis `studio.kanal` (openrouter-api-key, ai84-api-key). Claude Code anahtar istemez.

## 3. Kanal ayarları (`kanal.json`)
Varsayılanlar `config/kanal_varsayilan.json`; okumada derin birleştirme. Alanlar:
`ad, kisaltma (değişmez), kod_oneki, kod_hane, dil{calisma:"tr", hedef}, uzunluk{hedef_dk, kelime_otomatik,
calisma_kelime[2], hedef_kelime[2], kart_karakter, hook_esigi, hiz_olcum{<dil>: [{kod, hiz, kelime, sure_sn, tarih}]}}, ses{voice_id, voice_name, model_id, language_code, output_format,
stability, similarity_boost, style, speed, use_speaker_boost}, gorsel{karakter, kurallar, ifade_notu, yasakli[],
izinli_olumsuz[], flow_model, oran}, etiketler{senaryo{karakter, metafor, sema, ilk30}, ses[], ses_sinir{}, tag_orani},
montaj{muzik, muzik_lufs, son_ekran_sn, maskot{dosyalar[], sira[]}, altyazi{yazi_tipi, yazi, kutu, kutu_opaklik, boyut},
video{…, kenar{…}}}, hassas_kelimeler[], onaylar{konu, arastirma, senaryo, ceviri, paketleme}, isler{<iş>: {model,
efor, max_token, web_arama}}, butce{video_usd}, kimlik (uuid), olusturma, test`.

### 3.1 Doğrulama (`kanallar.dogrula`)
Ad 1–60 · kısaltma `^[a-z0-9][a-z0-9-]{1,30}$` ve benzersiz · önek büyük harf/rakam/tire ≤12 ve (büyük/küçük harf
duyarsız) benzersiz · hedef dil listede · sayısal aralıklar · kelime alt < üst (yalnız kelime_otomatik kapalıyken) · ses ayar aralıkları · karakter `@ad`
ya da boş · senaryo etiketleri 4 farklı kısa ad · ses tag'leri küçük harf · maskot sırası M1…Mn · renkler #RRGGBB ·
modeller genel ayarlarda tanımlı. Uyarılar: voice_id yok, ses dil kodu hedef dilden farklı.
İlk video üretildikten sonra önek ve hedef dil değiştirilemez. Listeler güncellemede birleştirilmez, değiştirilir.

## 4. Kanal işlemleri (`kanallar.py`)
- **Ekle:** doğrula → geçici `.kisaltma.kuruluyor/` klasöründe alt klasörler, şablonlar (`sablonlar/kanal/`; yer
  tutucular `{{KANAL_ADI}} {{KOD_ONEKI}} {{HEDEF_DIL}} {{HEDEF_DIL_KODU}}`), `kanal.json`, boş `taslaklar.json`;
  "klasörden içe aktar" seçildiyse kopyalama; sonra tek hamlede yerine taşınır (yarım kanal kalmaz). İlk kanal
  kendiliğinden seçilir.
- **İçe aktar:** SKILL.md klasör adına göre eşlenir (konu, arastirma, senaryo, ceviri/italyanca/hedef/translat, sahne,
  paketleme); proje dosyaları `[ÖNEK_]0N_` adına göre; `Muzik` ve `Maskot` klasörlerindeki medya. Arsiv, Videolar,
  Silinecekler, Defter_arsivi, .yedek, Skill_eski* altındakiler atlanır; aynı hedefe birden çok aday varsa adında
  CURRENT geçen, sonra en üst klasördeki seçilir. Kaynak klasör değiştirilmez.
- **Güncelle:** kısaltma/kimlik değişmez; doğrulama; hedef dil değişirse dosya uyarısı.
- **Sil:** kanal adı aynen yazılmalı; süren üretim varken silinmez. Kanal klasörü ve **yalnız** iki izi taşıyan CapCut
  taslakları (kanalın `taslaklar.json` kaydında var VE taslak klasöründe `.kanal_studyosu.json` içinde bu kanalın
  kimliği var) Çöp Kutusu'na taşınır (`cop.py`: macOS'ta Finder ile, "Geri koy" çalışır). Diğer taslaklara
  dokunulmaz.
- **Seç:** `Sistem/aktif.json`; süren üretim varken başka kanala geçilmez.
- **Kanal dosyaları:** yalnız 4 proje dosyası ve 6 SKILL.md okunup yazılabilir; kayıtta önceki hâl `.yedek/`'e.
  `⟦DOLDUR` işaretleri sayılır.
- **Eksikler:** voice_id (zorunlu), doldurulmamış dosya, boş müzik klasörü, eksik maskot dosyası (zorunlu), karakter
  referans görseli.

## 5. Beceri şablonları (`sablonlar/kanal/`)
İlk sürümün becerilerinden türetildi; kanala özgü içerik `01_Anayasa.md`'deki `⟦DOLDUR⟧` alanlarına taşındı. Sayısal
sınırlar, etiket adları, yasaklı kelimeler, ses tag'leri ve maskot kuralı becerilere yazılmaz: uygulama her aşamada
modele güncel **KANAL AYARLARI** bloğunu verir (§10.2). Çıktı dosya adları: `<ÖNEK>-0X_1_konu_karti.md`,
`_1_defter_degisiklikleri.md`, `_2_arastirma_outline.md`, `_3_senaryo_tr.md`, `_4_senaryo_<dil>.md`,
`_5A_elevenlabs.txt`, `_5B_gorsel_promptlari.txt`, `_5C_veo3.md`, `_5D_montaj_plani.tsv`, `_6_paket.md`,
`_6_aciklama_final.md`.

## 6. Arayüz
Üst çubuk: kalan bakiye (OpenRouter, AI84; tıkla → yenile), maliyet (Claude Code'da "abonelik" + API karşılığı tahmini; OpenRouter'da bu video / bu ay), kanal seçici (üretim sürerken
kilitli), + Kanal ekle, Ayarlar, Kayıt, Kapat.

Ana ekran (üretim yokken): başlangıç kontrolü; kanal yoksa "Kanal ekle"; varsa kanal kartı (bilgiler, üretime
hazırlık, Kanal ayarları, Klasörü aç, Kanalı sil), kanal dosyaları (tıkla → düzenle), **Sıradaki üretim** kartı
(sekmeler: **Konudan başla** [isteğe bağlı konu isteği] / **Hazır metinle başla** [metnin dili: Türkçe ya da kanalın
dili, metin]; **Bu üretimde onay iste**: ONAY 2/4/5, varsayılanı kanal ayarından; Üretime başla — ön kontrol ya da
kanalın zorunlu eksikleri varsa kapalı), **Videolar** listesi (biten videolarda Rapor düğmesi: rapor + maliyet dökümü).

Üretim ekranı (ilk sürümdekiyle aynı): adım çubuğu (kanalın aşama sırası; Türkçe kanalda 4. aşama yok; biten
yazım aşamalarına tıklayınca salt okunur görünüm), çalışıyor paneli (ilerleme, Durdur), onay paneli (kontrol notları,
açık noktalar, özet, dosya sekmeleri, "Metni burada düzenle" → Kaydet ve kontrol et / Modelin yazdığı hâle dön, ONAY ver
+ not, Düzeltme iste), Flow paneli (ajan komutu + Kopyala, bekleme sayacı, Görselleri şimdi kontrol et, yarı elle yol
partileri; ajan sorun bildirirse Aşama 5'e düzeltme), ses kenarı / senkron kontrol notları (Yine de devam et / Tekrar
kontrol et), bütçe sorusu, hata paneli (Ayrıntı, Hatayı kopyala, Tekrar dene), bitti paneli (rapor özeti, silme adayları
→ Silinecekler'e taşı / Kalsın, Üretimi kapat), Üretimi iptal et. Metin kutularında Kopyala ve Büyüt.

Kanal ekle: önce yol seçimi (Dosyayla ekle · Elle doldur; bkz. 10.14). Elle: 9 adımlı sihirbaz (Kimlik, Dil ve uzunluk,
Ses, Görsel, Etiketler, Montaj [kapanış imzası ve kalıp sayaçları dahil], Onaylar, Modeller ve bütçe, Beceriler ve
dosyalar). Kanal ayarları: aynı alanlar tek sayfada. Her bölümde az kullanılan alanlar (`gelismis: true`) katlanmış
"Gelişmiş" kutusundadır (DOM'da kalır, kaydedilir). Dil ve uzunlukta kelime sayısı yerine hesaplanan aralık gösterilir.

## 7. Uç noktalar (yalnız 127.0.0.1; Host + belirteç denetimi)
GET `/api/durum`, `/api/kayit`, `/api/kanal/sablon` (şablon metni), `/api/kanal/dosya?kanal=&ad=`, `/api/kanal/silinecekler?kanal=`, `/api/dosya?ad=`
(süren üretimin dosyası), `/api/rapor[?kod=]`, `/api/flow/istek`
POST `/api/onkontrol`, `/api/bakiye`, `/api/uretim/baslat` (`konu_istegi`, `onaylar`; hazır metinde `hazir`, `hazir_metin`, `hazir_dil`), `/api/asama/<eylem>` (onay, duzeltme, elle, elle-geri,
tekrar, devam, flow-kontrol, flow-sorun-devam, flow-a5-duzeltme, muzik-yenile, silme, kapat, durdur, iptal),
`/api/kanal/dosya-oku` (`metin`), `/api/kanal/dogrula`, `/api/kanal/ekle` (+`anayasa`), `/api/kanal/guncelle`, `/api/kanal/sec`,
`/api/kanal/sil`, `/api/kanal/dosya`, `/api/kanal/klasor-ac`, `/api/ayarlar`, `/api/anahtar`, `/api/anahtar-test`,
`/api/kayit/ac`, `/api/kapat`.

## 7b. Tek kopya
Açık kopya adresini `Sistem/calisan.json`'a yazar (0600); yeni açılış önce ona bakar, cevap veren kopya varsa yeni sunucu
başlatmaz, tarayıcıda açık olanı gösterir. Başlatıcı sunucuyu arka planda başlatıp çıkar (macOS'ta "The application is
not open anymore" hatası çıkmaz). Kapat düğmesi kaydı siler.

## 8. Genel ayarlar (`config/varsayilan.json` + `Sistem/ayarlar.json`)
`yollar.capcut_taslak, butce.aylik_usd, onbellek_suresi, saglayici (claude_code|openrouter; eski kayıtta başka değer varsa claude_code sayılır), openrouter.modeller,
duzeltme_tur_siniri, modeller (fiyatlar), web_arama_1000_usd`.

## 9. Paket ve test
`build-app.sh` → `Kanal Stüdyosu.app` (program, config, şablonlar, araclar, skills) · `build-paket.sh` →
`dist/Kanal Stüdyosu.zip` (uygulama, ilk kurulum, KURULUM.txt, KULLANIM.md, SPECS.md, `kanal-studyosu-flow.zip`).
Testler: `python3 -m unittest discover -s tests`:
- `test_kanallar.py`: kanal ekle/doğrula/içe aktar/güncelle/sil, iki izli taslak silme, tek kopya.
- `test_parite*.py`: ilk sürümün test takımı, örnek bir kanalda aynen çalışır;
  uçtan uca testte gerçek montaj betikleri (srt, odak, CapCut taslağı, senk, yayın, maskot gömme) çalışır.
- `test_genel_kanal.py`: İngilizce kanal (kod, KANAL AYARLARI bloğu, kontrollerin kanal ayarından okunması, maskotsuz
  plan kontrolü, boş hassas kelime listesi), Türkçe kanal (4. aşama atlanır, Türkçe senaryo final), onayı kapalı aşama,
  sunucu durumunun kanala göre olması.

## 10. Üretim hattı
### 10.1 Seçili kanal katmanı (`kanal.py`)
Üretim modülleri yolları ve sınırları `kanal.py`'den alır: `kok()` = `Kanallar/<kisaltma>/`, `proje_klasoru()`,
`video_klasoru(kod)`, `arsiv_klasoru(kod)`, `uygulama_klasoru(kod)` (= `Arsiv/<kod>/_uygulama`), `uretim_klasoru()`
(= `Uretim/`), `altyazi_adi(kod)` (= `<kod>_altyazi_<dil>.srt`), `KOD` (önek deseni), `siradaki_kod()` (Videolar +
Defter A tablosu + üretim listesi), `uretim_listesi()` (`uretim_listesi.json`), `rit03_yenile()` (03_Aktif_Video.md'nin
eski hâli `Arsiv/<kod>/03_Aktif_Video_oncesi_*.md`'ye kopyalanır). Üretim sürerken kanal değiştirilemediği için seçili
kanal üretimin kanalıdır; süren üretim `Sistem/aktif.json` → `uretim: {kanal, kod}`.

`ayarlar.ayarlar()` genel ayarları kanalın `isler` (konu→A1 … paketleme→A6, bolumler→A6_2, defter, uyum, rapor, odak),
`ses`, `montaj.video` ve `butce.video_usd` değerleriyle birleştirir; üretim kodu bunları görür.

### 10.2 Aşamalar (`asamalar.py`)
Sıra: A1 Konu → A2 Araştırma → A3 Senaryo TR → A4 Hedef dil (hedef dil Türkçe ise yok) → A5 Sahne paketi → A6 Paketleme
→ FLOW → STUDIO (ses ve video) → CAPCUT → A6_2 Bölümler → SON (son kontrol) → KAPANIŞ. Her yazım aşamasının sistem
istemi: kanalın 4 proje dosyası + aşama becerisi + **KANAL AYARLARI** bloğu (`kanal.ayarlar_blogu()`: önek, diller,
kelime aralıkları, kart sınırı, hook eşiği, senaryo etiketleri, ses tag'leri ve sınırları, tag oranı, karakter,
görsel oranı, yasaklı kelimeler, izinli olumsuzlamalar, maskot, görsel kurallar). A5'e kanalın yüz ifadesi notu eklenir.
Onay: ONAY 1 ve ONAY 3 her zaman; ONAY 2/4/5 kanalın `onaylar` ayarı (arastirma, ceviri, paketleme; varsayılan) ya da
üretimin başında yapılan seçim (`durum.json → onaylar`, `asamalar.onay_gerekli`). Onayı kapalı aşama kontroller
temizse beklemeden geçer, sorun varsa durur. 1. aşamaya Studio verisi gitmez ("Studio verisi yok."). Final metin: hedef dil
senaryosu (`_4_senaryo_<dil>.md`) ya da Türkçe kanalda `_3_senaryo_tr.md`; 03_Aktif_Video'ya
"## ONAYLI FİNAL METİN · <dil>" başlığıyla eklenir.

### 10.3 Kontroller (`kontroller.py`)
İlk sürümdeki kontrollerin aynısı; sayılar ve listeler kanal ayarından: kart karakter sınırı, Türkçe ve hedef
dil kelime aralıkları, hook eşiği, senaryo etiketleri, izinli ses tag'leri ve sınırları, tag oranı, Flow yasaklı
kelimeler ve izinli olumsuzlamalar, karakter etiketi promptun başında mı (karakter boşsa çalışmaz), paket etiketinde
kanal adı (#KanalAdı). Teslim satırları genel: `Words: NNNN` ya da `Kelime: NNNN`.

### 10.4 Montaj araçları (`araclar/`, `kanal_studyosu/araclar.py`)
İlk sürümün Araclar betikleri uygulamanın içine taşındı; iş mantıkları aynı. Kanala özgü her şeyi ortam
değişkenlerinden alırlar: `KS_KANAL` (kanal klasörü), `KS_AYAR` (kanal.json), `KS_ONEK`, `KS_URETIM`, `KS_CAPCUT`,
`KS_ARACLAR`, `KS_PYTHON` (`araclar/ortak.py`). Betikler: `srt_uret.py`, `odak_izgara.sh`, `capcut_taslak.py`
(altyazı stili ve FPS kanaldan; taslak oluşunca iki iz bırakılır), `plan_kontrol.py` (maskot sırası kanaldan; maskot
yoksa bütün satırlar `-`), `senk_kontrol.py`, `hassas_kelime_kontrol.py` (liste kanaldan; boşsa temiz),
`acilis_kapanis_defteri.py` (kalıp sayaçları ve imza kanaldan), `muzik_otomatik.py` (LUFS kanaldan; bkz. 10.13),
`muzik_yatagi.py`, `yayin_hazirla.py`, `maskot_gom.py`, `maskot_seffaf.sh`, `capcut_iskelet/`.

### 10.5 Flow (`flow.py`, `skills/kanal-studyosu-flow`)
FLOW adımında `Videolar/<kod>/flow_istek/` hazırlanır: `istek.json` (kod, proje adı, beşerli partiler, kanal,
karakter, oran, model, ajan talimatı, beklenen boyut 1376x768 ya da 9:16'da 768x1376), `promptlar.txt`,
`TALIMAT_AJAN.md`. Kullanıcı Claude masaüstünde `kanal-studyosu-flow` becerisiyle ajanı başlatır; ajan görselleri
`flow_cikti/`'ye koyup `BITTI.json` yazınca uygulama boyut/eksik kontrolü yapıp devam eder. Sorun olursa `SORUN.md` →
Aşama 5'e düzeltme. Yarı elle yol: partiler ekranda kopyalanır.

### 10.6 Ses ve video (`studio_baglanti.py`, `ses_kenar.py`)
Seslendirme AI84 üzerinden ElevenLabs ile, kanalın `ses` ayarıyla (voice_id ve model zorunlu). Ses kayıpsız WAV'a
çevrilip kenarları yumuşatılır; kenar kontrolü kesik bulursa adım onay bekler. Apostrof normalizasyonu ve istek kaydı
(`Uretim/<slug>-<id8>/logs/tts_istekleri.jsonl`). Sahne videoları `Uretim/<slug>-<id8>/` altında.

### 10.7 CapCut, son kontrol, kapanış
`capcut_zinciri.py`: srt → odak → taslak → senk kontrolü (notlar varsa onay bekler) → yayın hazırlığı (müzik, maskot,
son ekran). CapCut adımları yalnız CapCut kapalıyken çalışır. SON: sahne–görsel uyum kontrolü (kanalın görsel
kurallarıyla), hassas kelime kontrolü, rapor. KAPANIŞ: Kanal Defteri yenilenir (`02_Defter_*`, eski hâl
`Defter_arsivi/`), Açılış–Kapanış Defteri, silme adayları (`Silinecekler/<kod>/`'e taşınabilir; uygulama hiçbir şey
silmez), maliyet dökümü `Arsiv/<kod>/MALIYET.md`.

### 10.8 İptal
Hiçbir dosya silinmez: `Videolar/<kod>` ve `Arsiv/<kod>` → `Arsiv/<kod>_iptal_<zaman>/`; 03_Aktif_Video üretim öncesi
hâline döner; kod yeniden kullanılır; CapCut taslağı yerinde bırakılır.

### 10.9 Hazır metinle başlama
Kullanıcı metni yapıştırır ve dilini seçer (Türkçe ya da kanalın hedef dili; hedef dil Türkçe ise tek seçenek). Metin
aynen `Arsiv/<kod>/<kod>_0_hazir_metin.txt`'ye yazılır. 1. aşamanın yerine tek model çağrısı (iş `hazir`: Sonnet,
düşük efor; sistem istemi: proje dosyaları + `konu` ve `senaryo` becerileri yalnız biçim/kural referansı + görev +
KANAL AYARLARI): konu kartı, Kanal Defteri çakışma kontrolü ("Çakışma kontrolü: …"), sahne paragraflarına bölme,
paragraf etiketleri. Sıra (`durum.json → sira`, ekranda `gorunum`): Türkçe metin `HT → A4 → A5 …` (A2, A3 `atlandi`;
hedef dili Türkçe kanalda `HT → A5`), hedef dilde metin `HI → A5 …` (A2, A3, A4 `atlandi`). Onayda 03_Aktif_Video'ya
konu kartı ve final metinse final yazılır. Kod kontrolü `kontroller.hazir_metin`: etiketler ve teslim satırları
çıkarılınca kelime dizisi kullanıcınınkiyle aynı olmalı (kıvrık/düz tırnak ve üç nokta farkı sayılmaz) → değilse hata
ve otomatik düzeltme; kelime aralığı, etiketsiz paragraf, 90 kelimeden uzun paragraf ve geçersiz etiket uyarıdır.
Teslim satırını kod yazar (`Kelime: N`, İtalyancada `Parole: N · Paragrafi: M`, diğer dillerde
`Words: N · Paragraphs: M`). Rapor, hazır metinle başlandığını ve kapalı onayları yazar.

### 10.11 Yazım servisi: Claude Code (abonelik) · `claude_code.py`
Varsayılan servis. Bütün model işleri (6 aşama, bölümler, Defter yenileme, uyum, odak, rapor) bu Mac'teki `claude`
komutuyla, kullanıcının Pro/Max aboneliğinden yapılır. Görseller (Flow) bu servisin dışındadır: kullanıcı Claude
uygulamasında `kanal-studyosu-flow` becerisini çalıştırır.
- Komut: `claude -p --input-format stream-json --output-format stream-json --verbose --include-partial-messages
  --model <iş modeli> --system-prompt-file <geçici dosya> --safe-mode --strict-mcp-config --max-turns N
  [--effort <iş eforu>] (--tools "" | --tools WebSearch --allowedTools WebSearch) [--resume <oturum>]`.
  Sistem metni bizimkidir (Claude Code'un kod asistanı talimatı kullanılmaz). Mesaj stream-json ile verilir; görseller
  (uyum, odak) base64 blok olarak gider, araç gerekmez. Web araması yalnız `web_arama` ayarlı işlerde (1–2. aşama).
- Çalışma klasörü `Sistem/claude_code/` (boş). Kullanıcının Claude Code ayarları, becerileri, eklentileri ve MCP
  sunucuları yüklenmez. `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL` gibi değişkenler alt
  sürecin ortamından çıkarılır (istek API'ye değil aboneliğe gitsin). `CLAUDE_CODE_MAX_OUTPUT_TOKENS` = iş `max_token`.
- Düzeltme turu: asistan bloğunda saklanan oturum kimliğiyle `--resume`; yalnız yeni kullanıcı mesajı gönderilir.
  Oturum yoksa (servis üretim ortasında değiştiyse) önceki turlar metin olarak tek mesajda aktarılır.
- Çıktı: `assistant` olaylarındaki metinler (ana ajan), `result` olayından oturum, kullanım ve `total_cost_usd`.
  İlerleme `stream_event` metin parçalarından. Durdur alt süreci sonlandırır. Zaman aşımı 45 dk.
- Hatalar: kullanım sınırı (açılış saatiyle), giriş yok (/login), kurulu değil, tur sınırı, yoğunluk → Türkçe mesaj.
  Eski sürüm bir bayrağı tanımazsa (`unknown option`) o bayrak çıkarılıp yeniden denenir.
- Maliyet: satır `usd: 0`, `abonelik: true`, `tahmini_usd` (bilgi); bütçe sınırı uygulanmaz. Rapor ve döküm bunu
  yazar. Ön kontrol `claude --version` ve `claude auth status` (authMethod `claude.ai` = abonelik).
- OpenRouter seçiliyse eski yol aynen çalışır (Anthropic Messages biçimi, bütçe sınırı). Doğrudan Anthropic API
  seçeneği kaldırıldı (22 Eki 2026).

### 10.12 Başlatıcı onarımı (`macos/ortam.sh`)
Açılışta ortamın Python'u gerçekten açılıyor mu ve `anthropic` yükleniyor mu denenir. Bozuksa (ör. Homebrew Python'u
güncelledi, ortamdaki bağlantı eski Python'u gösteriyor) `python3 -m venv --clear` ile yeniden kurulur. Ortam hiç
kurulamazsa uyarı penceresi kayıttaki son hatayı gösterir; yalnız kütüphane kurulamazsa uygulama yine açılır
(Claude Code ile çalışır) ve sonraki açılışta yeniden denenir.

### 10.13 Müzik yatağı (22 Eki 2026)
- `muzik_otomatik.py`: `Varliklar/Muzik`'ten rastgele ve birbirinden farklı parçalar, videonun tamamını (son ekran
  dahil) dolduracak kadar seçilir; parçalar kendi uzunluklarınca arka arkaya çalar (baştaki ve son 15 sn'deki
  sessizlik atlanır, `ortak.muzik_olc`). Aynı parça ancak klasör bitince ve art arda gelmeyecek biçimde tekrar eder;
  10 sn'den kısa parçalar dolgu olarak kullanılmaz. Çıktı satırı: `secilen: 1) a.mp3 (0:00-2:31) · 2) …`.
- `muzik_yatagi.py`: parçalar arka arkaya `acrossfade` zinciriyle (en fazla 3 sn geçiş) birleşir, `apad` ile video
  süresine tamamlanır; seviye kanalın `muzik_lufs`'una göre, son ekranda yükseltme. Parça aralığından kısaysa döngü aynı
  dosyanın ayrı girdileriyle kurulur (eski asplit döngüsü kısa ses üretiyordu). 1.2.3: eski `adelay` + `amix`
  birleştirmesi FFmpeg 9.x'te ikinci parçadan sonrasını sessiz bırakıyordu (Windows testinde görüldü); Mac de zincire geçti.
- Kanalın müziği açık ama klasör boşsa montaj müziksiz yapılır (`--muziksiz`), kayda ve sonuçlara yazılır.
- **Müziği yeniden yap** (bitti ekranı; `POST /api/asama/muzik-yenile`, `Uretim.muzik_yenile`): CapCut taslağı
  oluştuktan sonra, CapCut kapalıyken `muzik_otomatik.py <kod> --ekle`. Taslaktaki müzik kanalı yenisiyle değişir;
  eski müzik `Arsiv/<kod>/eski_muzik_<kod>.m4a`, eski taslak `draft_info_muzik_oncesi.json` olarak kopyalanır.
- Maskotsuz kanal: plan kontrolünün boş maskot satırı alt satırı okumaz; `yayin_hazirla`'ya yalnız
  `--maskot S:M:SÜRE` çiftleri gider.

### 10.14 Yeni kanal dosyası ve kelime aralığı (1.2.3)
- **Şablon** (`kanal_sablonu.py`): `Yeni_Kanal_Sablonu.md` açılışta kurulum klasörüne konur (varsa dokunulmaz);
  `GET /api/kanal/sablon` aynı metni verir. Baş kısım kullanıcıya ve yapay zekaya talimat; `=== A · KANAL BİLGİLERİ ===`
  bölümünde `Alan: değer` satırları (`ALANLAR`: kanal adı, video dili, süre zorunlu; oran, karakter etiketi, karakter
  sahnesi etiketi, ifade notu, görsel kurallar, ek yasaklı kelimeler, hassas kelimeler, ses tag'leri, imza, altyazı
  yazı tipi ve renkleri, isteğe bağlı kısaltma/önek); `=== B · KANAL ANAYASASI ===` bölümü `01_Anayasa.md` şablonunun
  `## 1.`'den sonrası.
- **Okuma** (`kanal_sablonu.oku`, `POST /api/kanal/dosya-oku`), yapay zekasız: kod bloğu çitleri atılır; başlıklar
  biçim farkına dayanıklı (kalın, madde işaretli, BÜYÜK HARF; ı/i farkı yok); etiketsiz satırlar önceki alana eklenir;
  boş / "yok" / ⟦…⟧ boş sayılır. Dil adı ya da kodu tanınır; sayı metinden; oran "9:16/dikey"; karakter `@Ad` ("yok" →
  boş); renk #RRGGBB; ek yasaklı kelimeler genel listeye eklenir. Zorunlu alan boş ya da değer çevrilemezse `eksik`
  ({yol, etiket, neden}). Kısaltma ve önek boşsa addan, var olanlarla çakışmadan önerilir. Sonuç doğrulanır (eksikte
  zaten görünenler ve ses uyarısı hariç). Anayasada kalan ⟦DOLDUR⟧ sayısı uyarıdır.
- **Ekleme:** `kanallar.ekle(..., anayasa=)` → `anayasa_metni`: şablonun baş kısmı (doldurma notu olmadan) + B bölümü,
  `{{…}}` yer tutucuları doldurulur. Arayüz: yol seçimi → yapıştır/dosya seç → tek sayfa (Eksik ya da hatalı · Kanal ·
  Uygulamada seçilenler [ses, müzik, maskot, ONAY 2/4/5] · katlanmış "Dosyadan gelen diğer ayarlar").
- **Kelime aralığı** (`kanallar.kelime_hesapla`, `oku` her okumada): `uzunluk.kelime_otomatik` açıksa
  `calisma_kelime` (tr) ve `hedef_kelime` = hedef_dk × konuşma hızı × ses hızı (speed) ± %5, onluğa yuvarlanır.
  Hız: kanalın o dildeki son 5 ölçümünün ortancası, yoksa `KONUSMA_HIZI` (tr 142, it 167 — gerçek bir kanalın değerlerinden;
  en 155, de 135, es 165, fr 160, pt 160, nl 145, pl 130, ru 130, ar 120, ja 150). Arayüzdeki gösterim aynı hesap.
- **Ölçüm** (`Uretim._hiz_olc` → `studio_baglanti.ses_olcumu` + `kanallar.hiz_kaydet`): sesler bitince kelime (ses
  tag'leri hariç) / (sahne sesleri + sahne başına `pause_seconds`) → hız 1,0'a göre kelime/dk; 60–260 dışı ya da çok kısa
  ölçüm kaydedilmez, aynı video yeniden ölçülünce eskisinin yerine geçer. Ölçüm hatası üretimi durdurmaz.
- **Eski kanallar:** dosyasında `kelime_otomatik` yoksa okumada `false` sayılır; elle girilmiş aralıklar aynen kalır.

### 10.10 Denge testi verisi
`tests/veri/ornek_kanal.json`: uydurma bir örnek kanal tanımı; yalnız testlerde kullanılır.
Uygulamada belirli bir kanala özel bir şey yoktur.

---

## Ek A · Kaynak kodu (Windows)

Üretildi: 22.10.2026 16:18 · kod sürümü: 44350eb 2026-10-22

- `app/kanal_studyosu/__init__.py`
- `app/kanal_studyosu/__main__.py`
- `app/kanal_studyosu/ai84.py`
- `app/kanal_studyosu/araclar.py`
- `app/kanal_studyosu/asamalar.py`
- `app/kanal_studyosu/ayarlar.py`
- `app/kanal_studyosu/capcut_zinciri.py`
- `app/kanal_studyosu/cikti.py`
- `app/kanal_studyosu/claude_code.py`
- `app/kanal_studyosu/cop.py`
- `app/kanal_studyosu/defter.py`
- `app/kanal_studyosu/dosya_duzeni.py`
- `app/kanal_studyosu/flow.py`
- `app/kanal_studyosu/kanal.py`
- `app/kanal_studyosu/kanal_sablonu.py`
- `app/kanal_studyosu/kanallar.py`
- `app/kanal_studyosu/kayit.py`
- `app/kanal_studyosu/kontroller.py`
- `app/kanal_studyosu/llm.py`
- `app/kanal_studyosu/maliyet.py`
- `app/kanal_studyosu/metin.py`
- `app/kanal_studyosu/onkontrol.py`
- `app/kanal_studyosu/openrouter.py`
- `app/kanal_studyosu/ses_kenar.py`
- `app/kanal_studyosu/sistem_win.py`
- `app/kanal_studyosu/son_kontrol.py`
- `app/kanal_studyosu/studio_baglanti.py`
- `app/kanal_studyosu/sunucu.py`
- `app/kanal_studyosu/tek_kopya.py`
- `app/kanal_studyosu/uretim.py`
- `app/kanal_studyosu/yollar.py`
- `app/kanal_studyosu/web/index.html`
- `app/kanal_studyosu/web/app.js`
- `app/kanal_studyosu/web/stil.css`
- `app/config/kanal_varsayilan.json`
- `app/config/varsayilan.json`
- `app/sablonlar/kanal/Beceriler/arastirma/SKILL.md`
- `app/sablonlar/kanal/Beceriler/ceviri/SKILL.md`
- `app/sablonlar/kanal/Beceriler/konu/SKILL.md`
- `app/sablonlar/kanal/Beceriler/paketleme/SKILL.md`
- `app/sablonlar/kanal/Beceriler/sahne/SKILL.md`
- `app/sablonlar/kanal/Beceriler/senaryo/SKILL.md`
- `app/sablonlar/kanal/Proje_dosyalari/00_Yonetici.md`
- `app/sablonlar/kanal/Proje_dosyalari/01_Anayasa.md`
- `app/sablonlar/kanal/Proje_dosyalari/02_Defter.md`
- `app/sablonlar/kanal/Proje_dosyalari/03_Aktif_Video.md`
- `app/araclar/acilis_kapanis_defteri.py`
- `app/araclar/capcut_efekt_verisi.json`
- `app/araclar/capcut_taslak.py`
- `app/araclar/hassas_kelime_kontrol.py`
- `app/araclar/maskot_gom.py`
- `app/araclar/maskot_seffaf.py`
- `app/araclar/muzik_otomatik.py`
- `app/araclar/muzik_yatagi.py`
- `app/araclar/odak_izgara.py`
- `app/araclar/ortak.py`
- `app/araclar/plan_kontrol.py`
- `app/araclar/sablon_altyazi.json`
- `app/araclar/senk_kontrol.py`
- `app/araclar/srt_uret.py`
- `app/araclar/yayin_hazirla.py`
- `app/skills/kanal-studyosu-flow/SKILL.md`
- `app/requirements.txt`
- `app/windows/baslat.ps1`
- `app/windows/ilk_kurulum.ps1`
- `paket/1 - Ilk kurulum.cmd`
- `paket/KURULUM.txt`
- `paket/Kanal Stüdyosu.vbs`
- `build_paket.py`

### `app/kanal_studyosu/__init__.py`

```python
"""Kanal Stüdyosu: her YouTube kanalı için fikirden CapCut taslağına video üretim uygulaması."""
```

### `app/kanal_studyosu/__main__.py`

```python
"""Başlatma: python3 -m kanal_studyosu [--no-browser] [--port N]"""
from __future__ import annotations

import argparse
import atexit
import threading
import webbrowser

from . import ayarlar as A
from . import kanal_sablonu
from . import kayit
from . import sunucu
from . import tek_kopya
from . import yollar


def main() -> None:
    from .sistem_win import alt_surecleri_gizle
    alt_surecleri_gizle()
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--port", type=int, default=0)
    z = ap.parse_args()
    for k in yollar.kur():
        kayit.yaz(f"Klasör oluşturuldu: {k}")
    try:
        kanal_sablonu.sablon_dosyasi_yaz()
    except OSError as e:
        kayit.yaz(f"Yeni kanal şablonu yazılamadı: {e}", "uyari")
    acik = tek_kopya.calisan(yollar.calisan_dosyasi())
    if acik:  # uygulama zaten açık: ikinci kopya başlamaz, açık olan gösterilir
        kayit.yaz(f"{A.UYGULAMA} zaten açık; tarayıcıda o gösteriliyor")
        if not z.no_browser:
            webbrowser.open(acik)
        return
    s = sunucu.baslat(z.port)
    adres = f"http://127.0.0.1:{sunucu.PORT[0]}/?token={sunucu.TOKEN}"
    tek_kopya.kaydet(yollar.calisan_dosyasi(), sunucu.PORT[0], sunucu.TOKEN)
    atexit.register(tek_kopya.sil, yollar.calisan_dosyasi())
    kayit.yaz(f"{A.UYGULAMA} {A.SURUM} açıldı: {adres} · kurulum klasörü {yollar.kok()}")
    sunucu.onkontrol_baslat()
    if not z.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(adres)).start()
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
```

### `app/kanal_studyosu/ai84.py`

```python
"""AI84.pro API istemcisi (yalnız standart kütüphane). Belge: https://api.ai84.pro (kullanıcının verdiği entegrasyon notu).

Kurallar (belgeden):
- Kimlik: `xi-api-key` başlığı. Gövdeli her POST'ta `Content-Type: application/json`.
- Üretim asenkron: POST → job_id; GET ile durum sorgulanır; 'done' olunca audioUrl hemen indirilir.
- İş durumları KAPALI küme: queued, processing, done, failed. Tanınmayan durum bitmemiş sayılır.
- Sorgu 5xx dönerse iş hâlâ sürüyordur: aynı aralıkla sorgulamaya devam edilir.
- POST'ta 429: Retry-After kadar beklenir (dakikada 60 sınırı).
- HTTP 200 işin başarılı olduğu anlamına gelmez; job.status'a bakılır.
- Başarısız iş: errorMessage (gösterilebilir), errorCategory 1 = girdi hatası (tekrar etme),
  2 = geçici (sonra tekrar), errorMessageKey (dala ayırmak için). Başarısız işten ücret alınmaz.
- Ses URL'leri süreli imzalıdır; saklanmaz, hemen indirilir.

Bağlantı, eski Creator Pipeline Studio'da çalıştığı bilinen yolla Mac'in curl programıyla kurulur (belge
örnekleri de curl). Python'un varsayılan kimliği (Python-urllib) sunucu önündeki koruma katmanınca 403 ile
reddedilebiliyor. curl yoksa urllib tarayıcı benzeri bir User-Agent ile kullanılır.
Anahtar komut satırına yazılmaz (ps'te görünmesin): başlıklar 0600 izinli geçici dosyadan okunur.
"""
from __future__ import annotations

import json
import os
import shutil
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TABAN = "https://api.ai84.pro"
KIMLIK = "KanalStudyosu/0.1 (macOS; curl uyumlu)"


def _curl() -> str | None:
    return "/usr/bin/curl" if Path("/usr/bin/curl").exists() else shutil.which("curl")


def _son_basliklar(ham: str) -> dict:
    """curl -D çıktısında (-L ile birden çok yanıt olabilir) son yanıtın başlıkları."""
    bloklar = [b for b in ham.replace("\r\n", "\n").split("\n\n") if b.strip().startswith("HTTP/")]
    bas = {}
    for satir in (bloklar[-1].splitlines()[1:] if bloklar else []):
        if ":" in satir:
            k, v = satir.split(":", 1)
            bas[k.strip()] = v.strip()
    return bas
BITMIS = {"done", "failed"}


class AI84Hatasi(Exception):
    """kategori: 1 = istek hatası (aynen tekrar etme), 2 = geçici, None = bilinmiyor/ağ."""

    def __init__(self, mesaj: str, kategori: int | None = None, anahtar: str = "", http: int | None = None):
        super().__init__(mesaj)
        self.kategori, self.anahtar, self.http = kategori, anahtar, http


def _ssl_baglami():
    try:  # python.org Python'unda sistem sertifikaları olmayabilir; certifi (anthropic ile gelir) varsa kullan
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _json(ham: bytes) -> dict:
    try:
        j = json.loads(ham or b"{}")
        return j if isinstance(j, dict) else {"data": j}
    except ValueError:
        return {}


class AI84:
    def __init__(self, anahtar: str, taban: str = TABAN, bekle=time.sleep):
        self.anahtar, self.taban, self._bekle = anahtar.strip(), taban.rstrip("/"), bekle
        self._ssl = _ssl_baglami() if taban.startswith("https") else None

    # --- HTTP ---
    def _istek(self, yontem: str, yol: str, govde=None, zaman_asimi: int = 60) -> tuple[int, dict, dict]:
        if not self.anahtar:
            raise AI84Hatasi("AI84 anahtarı kayıtlı değil. Ayarlar'dan ekle.", 1)
        veri = json.dumps(govde, ensure_ascii=False).encode() if govde is not None else None
        basliklar = {"xi-api-key": self.anahtar, "Accept": "application/json",
                     **({"Content-Type": "application/json"} if veri is not None else {})}
        if _curl():
            return self._curl_istek(yontem, self.taban + yol, basliklar, veri, zaman_asimi)
        r = urllib.request.Request(self.taban + yol, data=veri, method=yontem, headers={**basliklar, "User-Agent": KIMLIK})
        try:
            with urllib.request.urlopen(r, timeout=zaman_asimi, context=self._ssl) as c:
                return c.status, _json(c.read()), dict(c.headers)
        except urllib.error.HTTPError as e:
            return e.code, _json(e.read()), dict(e.headers or {})
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise AI84Hatasi(f"AI84'e ulaşılamadı ({getattr(e, 'reason', e)}).", 2)

    @staticmethod
    def _curl_istek(yontem, url, basliklar, veri, zaman_asimi) -> tuple[int, dict, dict]:
        with tempfile.TemporaryDirectory() as td:
            hp, cikti, bd = Path(td) / "h", Path(td) / "o", Path(td) / "d"
            hp.write_text("\n".join(f"{k}: {v}" for k, v in basliklar.items()))
            os.chmod(hp, 0o600)
            komut = [_curl(), "-sS", "-L", "--max-time", str(zaman_asimi), "-X", yontem, "-H", "@" + str(hp),
                     "-D", str(bd), "-o", str(cikti), "-w", "%{http_code}", url]
            if veri is not None:
                komut += ["--data-binary", "@-"]
            try:
                q = subprocess.run(komut, input=veri, capture_output=True, timeout=zaman_asimi + 15)
            except subprocess.TimeoutExpired:
                raise AI84Hatasi("AI84 yanıt vermedi (zaman aşımı).", 2)
            if q.returncode:
                raise AI84Hatasi(f"AI84'e ulaşılamadı ({q.stderr.decode(errors='replace').strip()[:200]}).", 2)
            ham = cikti.read_bytes() if cikti.exists() else b""
            bas = _son_basliklar(bd.read_text(errors="replace")) if bd.exists() else {}
            j = _json(ham)
            if not j and ham:
                j = {"_ham": ham[:300].decode(errors="replace")}
            return int(q.stdout or 0), j, bas

    @staticmethod
    def _hata(kod: int, j: dict) -> AI84Hatasi:
        """Sunucunun kendi mesajı her zaman gösterilir (tahmin yürütmeden)."""
        msg = str(j.get("message") or j.get("error") or j.get("detail") or "").strip()
        if not msg and j.get("_ham"):
            ham = j["_ham"].lower()
            msg = ("istek sunucunun güvenlik katmanınca engellendi (Cloudflare)" if "cloudflare" in ham or "<html" in ham
                   else j["_ham"][:120])
        ek = f" Sunucu: {msg}" if msg else ""
        if kod == 401:
            return AI84Hatasi(f"AI84 anahtarı geçersiz ya da süresi dolmuş (HTTP 401).{ek}", 1, http=kod)
        if kod == 403:
            return AI84Hatasi(f"AI84 isteği reddetti (HTTP 403).{ek} Belgeye göre seslendirme ücretli hesap ister; "
                              "anahtarın aktif olduğunu ai84.pro panelinden kontrol et.", 1, http=kod)
        if kod >= 500:
            return AI84Hatasi(f"AI84 geçici bir hata verdi (HTTP {kod}); biraz sonra tekrar dene.", 2, http=kod)
        if kod == 0:
            return AI84Hatasi("AI84'ten yanıt alınamadı.", 2)
        return AI84Hatasi(f"AI84 hatası (HTTP {kod}).{ek}", 1, http=kod)

    # --- uç noktalar ---
    def krediler(self) -> int:
        kod, j, _ = self._istek("GET", "/v1/credits", zaman_asimi=20)
        if kod != 200:
            raise self._hata(kod, j)
        return int(j.get("credits", 0))

    def tts_gonder(self, govde: dict, deneme: int = 4) -> dict:
        """POST /v2/text-to-speech/async → {'job_id', 'credit_cost', …}. 429'da Retry-After kadar bekler."""
        for i in range(deneme):
            kod, j, bas = self._istek("POST", "/v2/text-to-speech/async", govde)
            if kod in (200, 201):
                if not (j.get("job_id") or j.get("task_id")):
                    raise AI84Hatasi("AI84 iş numarası döndürmedi.", 2)
                return j
            if kod == 429 and i + 1 < deneme:
                self._bekle(float(bas.get("Retry-After") or bas.get("retry-after") or 10))
                continue
            raise self._hata(kod, j)
        raise AI84Hatasi("AI84 istek sınırı (429) aşıldı; biraz sonra tekrar dene.", 2, http=429)

    def tts_durum(self, job_id: str) -> dict | None:
        """GET /v2/text-to-speech/async/:id → job sözlüğü; 5xx ya da ağ hatasında None (iş sürüyor sayılır)."""
        try:
            kod, j, _ = self._istek("GET", "/v2/text-to-speech/async/" + urllib.parse.quote(str(job_id), safe=""),
                                    zaman_asimi=45)
        except AI84Hatasi:
            return None
        if kod >= 500:
            return None
        if kod != 200:
            raise self._hata(kod, j)
        return j.get("job", j)

    def tts_bekle(self, job_id: str, sure: int = 600, aralik: float = 3, durum_cb=None) -> dict:
        """Bitene kadar sorgular. done → job; failed → AI84Hatasi (kategori ile); süre dolarsa kategori None."""
        son = time.time() + sure
        while time.time() < son:
            job = self.tts_durum(job_id)
            st = (job or {}).get("status", "")
            if durum_cb and st:
                durum_cb(st)
            if st == "done":
                if not job.get("audioUrl"):
                    raise AI84Hatasi("İş bitti ama ses adresi yok.", 2)
                return job
            if st == "failed":
                raise AI84Hatasi(job.get("errorMessage") or "Seslendirme başarısız.", job.get("errorCategory"),
                                 job.get("errorMessageKey") or "")
            self._bekle(aralik)
        raise AI84Hatasi("10 dakikada tamamlanmadı; AI84 işi hâlâ sürüyor olabilir. Tekrar dene aynı işi "
                         "ücretsiz sorgular.", None)

    def indir(self, url: str, zaman_asimi: int = 120) -> bytes:
        """İmzalı ses adresi: anahtarsız indirilir."""
        if urllib.parse.urlparse(url).scheme not in ("http", "https"):
            raise AI84Hatasi("Geçersiz ses adresi.", 2)
        if _curl():
            try:
                q = subprocess.run([_curl(), "-sS", "-L", "--fail", "--max-time", str(zaman_asimi), url],
                                   capture_output=True, timeout=zaman_asimi + 15)
            except subprocess.TimeoutExpired:
                raise AI84Hatasi("Ses indirilemedi (zaman aşımı).", 2)
            if q.returncode:
                raise AI84Hatasi(f"Ses indirilemedi ({q.stderr.decode(errors='replace').strip()[:200]}).", 2)
            return q.stdout
        try:
            r = urllib.request.Request(url, headers={"User-Agent": KIMLIK})
            with urllib.request.urlopen(r, timeout=zaman_asimi, context=self._ssl if url.startswith("https") else None) as c:
                return c.read()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise AI84Hatasi(f"Ses indirilemedi ({getattr(e, 'reason', e)}).", 2)
```

### `app/kanal_studyosu/araclar.py`

```python
"""Montaj araçlarını (uygulamanın araclar/ klasöründeki betikler) çağırır.

Betikler ilk sürümün Araclar betiklerinden taşındı; iş mantıkları aynıdır. Kanala özgü her şeyi ortam
değişkenlerinden alırlar:
  KS_KANAL   kanal klasörü (Videolar/, Arsiv/, Varliklar/ burada)
  KS_AYAR    kanal.json (dil, altyazı stili, maskot, müzik, hassas kelimeler, kalıp sayaçları)
  KS_ONEK    video kodu öneki
  KS_URETIM  ses/görsel/sahne videosu klasörlerinin kökü (Kanallar/<kanal>/Uretim)
  KS_CAPCUT  CapCut taslak klasörü
  KS_ARACLAR betiklerin klasörü
Betikler sistemdeki python3 ile çalışır (Pillow gibi kütüphaneler orada).
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import ayarlar as A
from . import kanal
from . import kayit
from . import yollar

ARACLAR = ("srt_uret.py", "odak_izgara.py", "capcut_taslak.py", "plan_kontrol.py", "senk_kontrol.py",
           "hassas_kelime_kontrol.py", "acilis_kapanis_defteri.py", "muzik_otomatik.py", "muzik_yatagi.py",
           "yayin_hazirla.py", "maskot_gom.py", "ortak.py", "capcut_efekt_verisi.json", "sablon_altyazi.json",
           "capcut_iskelet")


class AracHatasi(Exception):
    """Betik çalıştırılamadı (model hatası değil): kullanıcıya gösterilir, modele gitmez.
    ayrinti: betiğin çıktısının sonu (hata ekranında 'Ayrıntı' olarak gösterilir, kopyalanabilir)."""

    def __init__(self, mesaj: str, ayrinti: str = ""):
        super().__init__(mesaj)
        self.ayrinti = ayrinti


@dataclass
class Sonuc:
    kod: int
    cikti: str


def araclar_klasoru() -> Path:
    return yollar.KAYNAK / "araclar"


def _python() -> str:
    """Betikler uygulamanın kendi Python ortamında çalışır (Pillow orada kurulu). Konsol penceresi açmayan
    pythonw yerine python.exe kullanılır (betik çıktısı okunur)."""
    import sys
    py = Path(sys.executable)
    if py.name.lower() == "pythonw.exe" and (py.parent / "python.exe").exists():
        return str(py.parent / "python.exe")
    return str(py)


def ortam() -> dict:
    from .onkontrol import program
    ekler = [str(Path(p).parent) for p in (program("ffmpeg"), program("magick")) if p]
    yol_ = os.pathsep.join(ekler + [os.environ.get("PATH", "")])
    return dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PATH=yol_, KS_KANAL=str(kanal.kok()),
                KS_AYAR=str(kanal.kok() / "kanal.json"), KS_ONEK=kanal.onek(), KS_URETIM=str(kanal.uretim_klasoru()),
                KS_CAPCUT=str(A.yol("capcut_taslak")), KS_ARACLAR=str(araclar_klasoru()), KS_PYTHON=_python())


def calistir(betik: str, *argumanlar: str, zaman_asimi: int = 1800) -> Sonuc:
    yol = araclar_klasoru() / betik
    if not yol.exists():
        raise AracHatasi(f"araclar/{betik} bulunamadı.")
    komut = [_python(), str(yol)] + list(argumanlar)
    kayit.yaz(f"Araç: {betik} {' '.join(argumanlar)}")
    try:
        from .sistem_win import gizli
        p = subprocess.run(komut, cwd=str(yol.parent), env=ortam(), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=zaman_asimi, **gizli())
    except subprocess.TimeoutExpired:
        raise AracHatasi(f"{betik} {zaman_asimi // 60} dakikada bitmedi.")
    cikti = (p.stdout or "") + (("\n" + p.stderr) if p.stderr.strip() else "")
    if p.returncode != 0:
        kayit.yaz(f"{betik} hata verdi:\n{cikti[-2000:]}", "hata")
        raise AracHatasi(f"{betik} hata verdi.", f"$ {betik} {' '.join(argumanlar)}\n{cikti[-4000:]}")
    return Sonuc(p.returncode, cikti)


# --- Belirli betiklerin çıktıları ------------------------------------------------

def plan_kontrol(tsv_yolu: str, sahne_sayisi: int) -> dict:
    """→ {'temiz': bool, 'hatalar': [...], 'maskot': '--maskot 10:1:2 …', 'kes': '70.3'}"""
    c = calistir("plan_kontrol.py", str(tsv_yolu), str(sahne_sayisi)).cikti
    son = next((s for s in reversed(c.splitlines()) if s.startswith(("TEMIZ", "HATA"))), "")
    hatalar = []
    if "[" in son:  # betik listeyi Python biçiminde yazar; tırnak içeren mesajlar da doğru ayrılsın
        try:
            hatalar = [str(h) for h in ast.literal_eval(son[son.find("["):].strip())]
        except (ValueError, SyntaxError):
            hatalar = re.findall(r"'([^']*)'", son[son.find("["):])
    # Maskotsuz kanalda satır boştur; yalnız kendi satırı okunur (alt satırdaki "TEMIZ []" karışmasın).
    m = re.search(r"yayin_hazirla maskot:[ \t]*([^\n]*)", c)
    k = re.search(r"KES %\s*([\d.]+)", c)
    return {"temiz": son.startswith("TEMIZ"), "hatalar": hatalar, "maskot": m.group(1).strip() if m else "",
            "kes": k.group(1) if k else ""}


def hassas_kelime(kod: str) -> dict:
    """→ {'temiz': bool, 'paketleme': [...], 'metin': [...]} (betik Videolar/<kod>/04 ve 02'yi okur)."""
    c = calistir("hassas_kelime_kontrol.py", kod).cikti
    satirlar = [s.strip() for s in c.splitlines() if s.strip()]
    return {"temiz": any("TEMIZ" in s for s in satirlar[:1]),
            "paketleme": [s for s in satirlar if s.startswith("paketleme satir")],
            "metin": [s for s in satirlar if s.startswith("metin ilk 30 sn")]}


def acilis_kapanis() -> str:
    """Kanal klasöründeki Acilis_Kapanis_Defteri.md'yi yeniden üretir ve içeriğini döndürür."""
    calistir("acilis_kapanis_defteri.py")
    return (kanal.kok() / "Acilis_Kapanis_Defteri.md").read_text(encoding="utf-8")
```

### `app/kanal_studyosu/asamalar.py`

```python
"""Aşama tanımları ve modele giden mesajların kurulması.

Sistem öneki (önbellekli, bir video boyunca sabit): proje dosyaları 00 + 01 + 02 → aşama becerisi (içerik
değiştirilmeden) → uygulama çerçevesi notu + KANAL AYARLARI (kanal.json'dan).
Kullanıcı mesajı (değişken): beceriyi tetikleyen kısa Türkçe mesaj + onaylı girdiler.
Hedef dil Türkçe olan kanalda 4. aşama yoktur; Türkçe senaryo finaldir.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from . import araclar
from . import ayarlar as A
from . import kanal
from . import kontroller as K

CERCEVE = """# UYGULAMA ÇERÇEVESİ (Kanal Stüdyosu)
Bu konuşma Kanal Stüdyosu uygulamasında, API üzerinden yürüyor. Yukarıdaki proje dosyaları (00–02) ve aşama becerisi aynen geçerlidir. Yalnızca şu teknik farklar vardır:
1. Ajan yok. Uygulama dosyaları otomatik kaydeder, kontrolleri kod yapar, onayları kullanıcı uygulama ekranında verir. Kullanıcı mesajlarını uygulama iletir.
2. Dosya aracı yok. Her çıktı dosyasını tam adıyla şu biçimde ver: <dosya ad="DOSYA_ADI">tam içerik</dosya>. İçeriği kod bloğuna sarma.
3. Sohbet cevabını (özet, kontrol satırları, durum kartı) <ozet>…</ozet> içinde ver. Dosya içeriğini özette tekrar etme.
4. Düzeltme turunda dosyayı baştan yazma; yalnız değişen kısımları yama olarak ver. Numaralar yamadan önceki dosyaya göredir:
   <yama dosya="AD" paragraf="12">paragrafın yeni hali, etiketleriyle</yama>
   <yama dosya="AD" paragraf="12" islem="sil"></yama>
   <yama dosya="AD" paragraf="12" islem="sonrasina_ekle">eklenecek paragraf(lar)</yama>
   <yama dosya="AD" satir="Başlık">satırın yeni tam hali (bu metinle başlayan ilk satırın yerine geçer; montaj planında satir="0023")</yama>
   <yama dosya="AD" bolum="§4">bölümün yeni tam hali</yama>
   <yama dosya="AD" kuyruk="1">teslim satırlarının yeni hali (kelime/paragraf satırları değiştiyse)</yama>
   Değişiklik çok kapsamlıysa dosyanın tamamını <dosya> ile yeniden verebilirsin.
5. Becerideki "Model: …" satırı bilgi içindir; modeli uygulama seçer.
6. Web arama aracı açıksa onu kullan; değilse bilgini kullan. Sayı uydurma. Doğrulanacak iddiaları ve hassas bölümleri metnin içinde işaretleme; sohbet cevabının sonunda düz yazı tek satır ver: "Açık noktalar: ¶N … " (paragraf numarasıyla; yoksa "Açık noktalar: yok").
7. Konuşma her aşamada yenidir. Önceki aşamaların onaylı çıktıları mesajda <belge ad="…"> olarak verilir; 03_Aktif_Video.md de güncel hâliyle mesajdadır. Becerilerde başka adlarla anılan proje dosyaları (ör. ORN_00, ORN_01, ORN_02, ORN_03) sırasıyla 00_Yonetici.md, 01_Anayasa.md, 02_Defter.md ve 03_Aktif_Video.md'dir; beceri adları (ör. ornek-arastirma) da bu uygulamadaki aşamalardır.
8. Metinde geçerli etiketler yalnız {senaryo}. Seslendirme metninde yalnız {ses}."""


def cerceve() -> str:
    e = kanal.ayar()["etiketler"]
    sinir = e.get("ses_sinir", {})
    ses = " ".join(f"[{t}]" for t in e["ses"] if t not in sinir)
    ses += "".join(f" ve en fazla {n} [{t}]" for t, n in sinir.items())
    return CERCEVE.format(senaryo=" ".join(f"[{x}]" for x in e["senaryo"].values()), ses=ses.strip()) \
        + "\n\n" + kanal.ayarlar_blogu()


def ifade_notu() -> str:
    return (kanal.ayar()["gorsel"].get("ifade_notu") or "").strip()


def belge(ad: str, icerik: str) -> str:
    return f'<belge ad="{ad}">\n{icerik.strip()}\n</belge>'


@dataclass(frozen=True)
class Asama:
    kimlik: str               # "A1"
    no: int                   # 1..6
    ad: str                   # ekranda görünen
    beceri: str               # Beceriler/<beceri>/SKILL.md
    onay: int | None          # ONAY numarası (yoksa None)
    cikti_sonekleri: tuple    # dosya adı sonekleri: "_1_konu_karti.md" … ({dil} = hedef dil kodu)

    def ciktilar(self, kod: str) -> list[str]:
        return [kod + s.replace("{dil}", kanal.hedef_dil()) for s in self.cikti_sonekleri]


ASAMALAR = {
    "A1": Asama("A1", 1, "Konu", "konu", 1, ("_1_konu_karti.md", "_1_defter_degisiklikleri.md")),
    "A2": Asama("A2", 2, "Araştırma", "arastirma", 2, ("_2_arastirma_outline.md",)),
    "A3": Asama("A3", 3, "Senaryo TR", "senaryo", 3, ("_3_senaryo_tr.md",)),
    "A4": Asama("A4", 4, "Hedef dil", "ceviri", 4, ("_4_senaryo_{dil}.md",)),
    # Aşama 5'te ONAY yok: kontroller temizse kendiliğinden Aşama 6'ya geçilir.
    "A5": Asama("A5", 5, "Sahne paketi", "sahne", None,
                ("_5A_elevenlabs.txt", "_5B_gorsel_promptlari.txt", "_5C_veo3.md", "_5D_montaj_plani.tsv")),
    "A6": Asama("A6", 6, "Paketleme", "paketleme", 5, ("_6_paket.md",)),
    # Montaj sonrası Mesaj 2: ONAY yok; kod zaman damgalarını doğrular.
    "A6_2": Asama("A6_2", 6, "Bölümler", "paketleme", None, ("_6_aciklama_final.md",)),
}
# Hazır metinle başlayan üretimin ilk aşaması (1. aşamanın yerine): konu kartı + Defter çakışma kontrolü +
# metni sahne paragraflarına bölme + paragraf etiketleri. Metnin kendisi değişmez (kod denetler).
# HT: metin Türkçe (3. aşamanın dosyası olur) · HI: metin hedef dilde (4. aşamanın dosyası olur, sonra 5).
ASAMALAR["HT"] = Asama("HT", 1, "Hazır metin", "konu", 1,
                       ("_1_konu_karti.md", "_1_defter_degisiklikleri.md", "_3_senaryo_tr.md"))
ASAMALAR["HI"] = Asama("HI", 1, "Hazır metin", "konu", 1,
                       ("_1_konu_karti.md", "_1_defter_degisiklikleri.md", "_4_senaryo_{dil}.md"))
HAZIR = ("HT", "HI")
HAZIR_ORIJINAL = "_0_hazir_metin.txt"  # kullanıcının verdiği metin, aynen (arşivde)

TUM_SIRA = ["A1", "A2", "A3", "A4", "A5", "A6", "FLOW", "STUDIO", "CAPCUT", "A6_2", "SON", "KAPANIS"]
SON_ADIM = "BITTI"
# Kanal ayarındaki onay anahtarı (Onaylar ekranı). Yalnız ONAY 2, 4 ve 5 kapatılabilir; ONAY 1 ve 3 her zaman.
ONAY_ANAHTARI = {"A1": "konu", "A2": "arastirma", "A3": "senaryo", "A4": "ceviri", "A6": "paketleme"}
ONAY_SECILEBILIR = ("A2", "A4", "A6")


def hazir_dil(kimlik: str) -> str:
    return "tr" if kimlik == "HT" else kanal.hedef_dil()


def hazir_diller() -> dict[str, str]:
    """Hazır metnin seçilebilecek dilleri: Türkçe ve kanalın hedef dili (hedef dil Türkçe ise tek seçenek)."""
    d = {"tr": "Türkçe"}
    d[kanal.hedef_dil()] = kanal.dil_adi()
    return d


def sira(d: dict | None = None) -> list[str]:
    """Üretimin adımları: hedef dil Türkçe ise A4 yoktur; hazır metinle başlayan üretimde durum.json → sira."""
    if d and d.get("sira"):
        return d["sira"]
    return [x for x in TUM_SIRA if x != "A4" or kanal.ceviri_var()]


def gorunum_sirasi(d: dict | None = None) -> list[str]:
    return (d or {}).get("gorunum") or sira(d)


def hazir_sira(dil: str) -> tuple[list[str], list[str], list[str]]:
    """Hazır metinli üretim → (çalışma sırası, ekrandaki sıra, atlanan aşamalar)."""
    normal = sira()
    if dil == "tr":
        ilk, atlanan = "HT", ["A2", "A3"]
    else:
        ilk, atlanan = "HI", ["A2", "A3", "A4"]
    atlanan = [k for k in atlanan if k in normal]
    kalan = [k for k in normal if k != "A1" and k not in atlanan]
    return [ilk] + kalan, [ilk] + atlanan + kalan, atlanan


def adim_adlari() -> dict[str, str]:
    return {"A1": "1 · Konu", "A2": "2 · Araştırma", "A3": "3 · Senaryo TR", "A4": f"4 · {kanal.dil_adi()}",
            "A5": "5 · Sahne paketi", "A6": "6 · Paketleme", "FLOW": "Görseller (Flow)", "STUDIO": "Ses ve video",
            "CAPCUT": "CapCut", "A6_2": "Bölümler", "SON": "Son kontrol", "KAPANIS": "Kapanış",
            "HT": "1 · Hazır metin (Türkçe)", "HI": f"1 · Hazır metin ({kanal.dil_adi()})"}


def onay_varsayilan() -> dict:
    o = kanal.ayar()["onaylar"]
    return {k: bool(o.get(ONAY_ANAHTARI[k], True)) for k in ONAY_SECILEBILIR}


def onay_gerekli(asama: Asama, d: dict | None = None) -> bool:
    """ONAY'lı aşama onay bekler mi: ONAY 2/4/5 için önce bu üretimin seçimi, yoksa kanal ayarı; diğerleri her zaman."""
    if asama.onay is None:
        return False
    if asama.kimlik in ONAY_SECILEBILIR:
        secim = (d or {}).get("onaylar") or {}
        if asama.kimlik in secim:
            return bool(secim[asama.kimlik])
        return onay_varsayilan()[asama.kimlik]
    return True


HAZIR_GOREV = """# AŞAMA: HAZIR METİN
Kullanıcı bu videonun metnini hazır verdi. Konu seçimi, araştırma ve senaryo yazımı (metin hedef dildeyse hedef dilde yeniden yazım da) yapılmıyor. Yukarıdaki iki beceri yalnız BİÇİM ve KURAL kaynağıdır: konu kartının biçimi ve Defter değişikliklerinin biçimi `konu` becerisinden, sahne paragrafları ve etiketlerin anlamı `senaryo` becerisinden. O becerilerdeki diğer adımları (Studio verisi, konu seçme, web araştırması, yazım, öz denetim, çeviri, hook güçlendirme) uygulama.

Görevin dört iş:
1. Konu kartı: beceri biçiminde, kanal ayarlarındaki karakter sınırını aşmadan, "KONU KARTI · <KOD> · …" başlığıyla ve Başlık satırıyla. İçeriği yalnız verilen metinden çıkar.
2. Kanal Defteri kontrolü: konu, başlık, açılış ve kapanış 02_Defter.md'deki önceki videolarla çakışıyor mu, aynı kalıp tekrar ediyor mu. Sonucu <ozet> içinde "Çakışma kontrolü: …" satırıyla yaz (çakışma yoksa "yok"). Defter değişikliklerini beceri biçiminde ayrı dosyaya yaz.
3. Sahne paragrafları: metni sahne büyüklüğünde paragraflara böl; paragraflar arasında bir boş satır. Yalnız cümle sonlarından böl. Metin zaten paragraflara bölünmüşse uygun olanları koru.
4. Etiketler: her paragrafın başına senaryo becerisindeki anlamlarına göre, kanal ayarlarındaki senaryo etiketlerinden uygun olanı koy. Metinde zaten etiket varsa koru.

METNE DOKUNMA: tek kelime ekleme, silme, değiştirme, çevirme ya da yerini değiştirme; noktalamayı ve yazımı da koru. Yalnız paragraf araları ve etiketler eklenir. Uygulama, etiketler çıkarılınca metnin kullanıcınınkiyle kelimesi kelimesine aynı olduğunu denetler.
Metnin sonuna teslim satırı (kelime/paragraf/hook) yazma; uygulama ekler. Üç dosyayı da tam adlarıyla <dosya> içinde ver."""


def final_dosya(kod: str) -> str:
    """Seslendirilecek onaylı final metin: hedef dil senaryosu (A4) ya da hedef dil Türkçe ise Türkçe senaryo."""
    return ASAMALAR["A4"].ciktilar(kod)[0] if kanal.ceviri_var() else kod + "_3_senaryo_tr.md"


def sistem(asama: Asama) -> list[str]:
    ortak = "\n\n".join(f"# PROJE DOSYASI: {ad}\n\n{kanal.rit(ad)}" for ad in kanal.PROJE_DOSYALARI[:3])
    if asama.kimlik in HAZIR:
        referans = "\n\n".join(f"# REFERANS BECERİ (yalnız biçim ve kurallar için): {b}\n\n{kanal.beceri(b)}"
                               for b in ("konu", "senaryo"))
        return [ortak, referans, HAZIR_GOREV + "\n\n" + cerceve()]
    return [ortak, f"# AŞAMA BECERİSİ: {asama.beceri}\n\n{kanal.beceri(asama.beceri)}", cerceve()]


def _not(onay_notu: str) -> str:
    return f" Notlar: {onay_notu.strip()}" if onay_notu and onay_notu.strip() else ""


def ilk_mesaj(asama: Asama, kod: str, oku: Callable[[str], str], girdi: dict) -> str:
    """oku(dosya_adı) → arşivdeki onaylı çıktı; girdi: studio_verisi, konu_istegi, onay_notlari."""
    notlar = girdi.get("onay_notlari", {})
    aktif = lambda: belge(kanal.AKTIF, kanal.rit(kanal.AKTIF))
    if asama.kimlik in HAZIR:
        kart, defter_, metin_ = asama.ciktilar(kod)
        parcalar = [f"{kod} için hazır metin. Metnin dili: {kanal.dil_adi(hazir_dil(asama.kimlik))}. "
                    f"Dosyalar: `{kart}` (konu kartı), `{defter_}` (Defter değişiklikleri), `{metin_}` (sahne "
                    "paragraflarına bölünmüş ve etiketlenmiş metin)."]
        if (girdi.get("konu_istegi") or "").strip():
            parcalar.append("Kullanıcının notu:\n" + girdi["konu_istegi"].strip())
        parcalar.append(belge("hazir_metin.txt", oku(kod + HAZIR_ORIJINAL)))
        return "\n\n".join(parcalar)
    if asama.kimlik == "A1":
        parcalar = [f"{kod} için Aşama 1. `konu` becerisini kullan."]
        veri = (girdi.get("studio_verisi") or "").strip()
        parcalar.append("Önceki yayınlanmış videonun Studio verisi:\n" + veri if veri else "Studio verisi yok.")
        if (girdi.get("konu_istegi") or "").strip():
            parcalar.append("Kullanıcının konu isteği:\n" + girdi["konu_istegi"].strip())
        return "\n\n".join(parcalar)
    if asama.kimlik == "A2":
        return "\n\n".join([f"ONAY 1.{_not(notlar.get('A1'))} Aşama 2: `arastirma`.", aktif()])
    if asama.kimlik == "A3":
        outline = kod + "_2_arastirma_outline.md"
        return "\n\n".join([f"ONAY 2.{_not(notlar.get('A2'))} Aşama 3: `senaryo`.", aktif(), belge(outline, oku(outline))])
    if asama.kimlik == "A4":
        tr = kod + "_3_senaryo_tr.md"
        return "\n\n".join([f"ONAY 3.{_not(notlar.get('A3'))} Aşama 4: `ceviri` ({kanal.dil_adi()}).", aktif(),
                            belge(tr, oku(tr))])
    if asama.kimlik == "A5":
        onceki = "A4" if kanal.ceviri_var() else "A3"
        no = 4 if kanal.ceviri_var() else 3
        parcalar = [f"ONAY {no}.{_not(notlar.get(onceki))} {kod} Aşama 5: `sahne`. Final metin 03_Aktif_Video.md'de."]
        if ifade_notu():
            parcalar.append("Görsel promptları için ek not: " + ifade_notu())
        return "\n\n".join(parcalar + [aktif()])
    if asama.kimlik == "A6":
        return "\n\n".join([f"{kod} Aşama 6: `paketleme` (Mesaj 1).", aktif()])
    if asama.kimlik == "A6_2":
        zamanlar = "\n".join(f"{b['zaman']} · {b['bolum']} · {b['ilk_cumle']}" for b in girdi.get("bolumler", []))
        paket = kod + "_6_paket.md"
        return "\n\n".join([
            f"Montaj bitti. {kod} Aşama 6 Mesaj 2: bölümler ve nihai açıklama. Zamanlar kesin:\n{zamanlar}",
            f"ONAY 5 verilen paket aşağıda.{_not(notlar.get('A6'))}", belge(paket, oku(paket)), aktif()])
    raise KeyError(asama.kimlik)


def kontrol(asama: Asama, kod: str, oku: Callable[[str], str]) -> K.Sonuc:
    sonuc = K.Sonuc()
    dosyalar = {}
    for ad in asama.ciktilar(kod):
        try:
            dosyalar[ad] = oku(ad)
        except FileNotFoundError:
            dosyalar[ad] = ""
    sonuc.hatalar += K.eksik_dosyalar(dosyalar, asama.ciktilar(kod))
    if sonuc.hatalar:
        return sonuc
    if asama.kimlik == "A1":
        ek = K.konu_karti(dosyalar[kod + "_1_konu_karti.md"])
    elif asama.kimlik in HAZIR:
        ek = K.konu_karti(dosyalar[kod + "_1_konu_karti.md"])
        hm = K.hazir_metin(oku(kod + HAZIR_ORIJINAL), dosyalar[asama.ciktilar(kod)[2]], hazir_dil(asama.kimlik))
        ek.hatalar += hm.hatalar
        ek.uyarilar += hm.uyarilar
        ek.bilgiler += hm.bilgiler
    elif asama.kimlik == "A3":
        ek = K.senaryo_tr(dosyalar[kod + "_3_senaryo_tr.md"])
    elif asama.kimlik == "A4":
        ek = K.senaryo_it(oku(kod + "_3_senaryo_tr.md"), dosyalar[final_dosya(kod)])
    elif asama.kimlik == "A5":
        a, b, c, d = (dosyalar[x] for x in asama.ciktilar(kod))
        ek = K.sahne_paketi(a, b, c, d, oku(final_dosya(kod)))
        if not ek.hatalar:  # plan_kontrol yalnızca sayılar tutarlıyken anlamlı
            pk = araclar.plan_kontrol(str(kanal.arsiv_klasoru(kod) / (kod + "_5D_montaj_plani.tsv")),
                                      len(K.bloklar(a)))
            ek.bilgiler.append(f"KES %{pk['kes']}" if pk["kes"] else "plan_kontrol çalıştı")
            if pk["temiz"]:
                ek.bilgiler.append("plan_kontrol: TEMIZ")
                ek.ek = {"maskot": pk["maskot"]}
            else:
                ek.hatalar += [f"Montaj planı (plan_kontrol): {h}" for h in pk["hatalar"]]
    elif asama.kimlik == "A6":
        ek = K.paket(dosyalar[kod + "_6_paket.md"])
        _hassas(kod, ek)
    elif asama.kimlik == "A6_2":
        ek = K.aciklama_final(dosyalar[kod + "_6_aciklama_final.md"], girdi_zamanlari(kod))
        _hassas(kod, ek)
    else:
        ek = K.Sonuc()
    sonuc.hatalar += ek.hatalar
    sonuc.uyarilar += ek.uyarilar
    sonuc.bilgiler += ek.bilgiler
    sonuc.ek = ek.ek
    return sonuc


def girdi_zamanlari(kod: str) -> list[str]:
    """CapCut adımında kaydedilen bölüm zamanları (durum.json)."""
    d = A.json_oku(kanal.uygulama_klasoru(kod) / "durum.json", {}) or {}
    return [b["zaman"] for b in d.get("bolumler", [])]


def _hassas(kod: str, ek: K.Sonuc) -> None:
    """hassas kelime kontrolü: DEFTER KAYDI (iç not) ve ilk 30 sn bulguları uyarı, diğerleri hata."""
    hk = araclar.hassas_kelime(kod)
    ic = _defter_kaydi_satirlari(kanal.video_klasoru(kod) / "04_Paketleme_ve_Veo3.md")
    for h in hk["paketleme"]:
        m = re.match(r"paketleme satir (\d+)", h)
        if m and int(m.group(1)) in ic:  # kanal içi not, yayında görünmez
            ek.uyarilar.append(f"Hassas kelime DEFTER KAYDI'nda (iç not, yayında görünmez): {h}")
        else:
            ek.hatalar.append(f"Hassas kelime ({h})")
    ek.uyarilar += [f"İlk 30 sn hassas kelime ({h}); metin onaylı olduğu için yalnızca bilgi." for h in hk["metin"]]
    if hk["temiz"]:
        ek.bilgiler.append("hassas_kelime_kontrol: TEMIZ")


def _defter_kaydi_satirlari(yol) -> set[int]:
    """04 dosyasında DEFTER KAYDI bölümünün satır numaraları (1'den başlar)."""
    satirlar = yol.read_text(encoding="utf-8").splitlines()
    bas = next((i for i, l in enumerate(satirlar) if l.startswith("#") and "DEFTER KAYDI" in l), None)
    if bas is None:
        return set()
    son = next((j for j in range(bas + 1, len(satirlar)) if satirlar[j].startswith("#")), len(satirlar))
    return set(range(bas + 1, son + 1))


def sonuc_dosyalari(asama: Asama, kod: str, oku: Callable[[str], str]) -> dict[str, str]:
    """Aşama çıktısından Videolar/<kod>/ sonuç dosyaları (SKILL D Adım 4.2 ve 4.5).
    İçerik değişmez; yalnızca sondaki boşluk ve TSV'deki boş satırlar temizlenir."""
    if asama.kimlik == "A5":
        tsv = "\n".join(K.tsv_satirlari(oku(kod + "_5D_montaj_plani.tsv"))) + "\n"
        return {"02_ElevenLabs_seslendirme_metni.txt": oku(kod + "_5A_elevenlabs.txt").rstrip() + "\n",
                "03_Gorsel_promptlari.txt": oku(kod + "_5B_gorsel_promptlari.txt").rstrip() + "\n",
                "05_Montaj_plani.tsv": tsv}
    paket = (f"# {kod} · Paketleme ve Veo3\n\n{oku(kod + '_6_paket.md').strip()}\n\n"
             f"## Veo3 hareket promptları\n\n{oku(kod + '_5C_veo3.md').strip()}\n") if asama.kimlik in ("A6", "A6_2") else ""
    if asama.kimlik == "A6":
        return {"04_Paketleme_ve_Veo3.md": paket}
    if asama.kimlik == "A6_2":
        # SKILL 10c: nihai açıklama 04'ün en üstüne "## 0 · YAYIN PAKETİ" olarak eklenir.
        return {"04_Paketleme_ve_Veo3.md":
                "## 0 · YAYIN PAKETİ (montaj sonrası nihai açıklama — YouTube'a bunu yapıştır)\n\n"
                f"{oku(kod + '_6_aciklama_final.md').strip()}\n\n"
                "Başlık, kapak A/B (test edilen hipotez) ve sabit yorum: aşağıdaki paketin 1., 2. ve 4. bölümleri.\n\n"
                f"---\n\n{paket}"}
    return {}


# Arşivdeki alışılmış adlar (SKILL D Adım 4): ham aşama dosyasının bir kopyası.
ARSIV_KOPYALARI = {"A5": {"_5C_veo3.md": "veo3.md"}, "A6": {"_6_paket.md": "proje3_paketleme.md"},
                   "A6_2": {"_6_aciklama_final.md": "proje3_paket_final.md"}}


def rit03_kart_ile(kod: str, kart: str, tarih: str) -> str:
    return (f"# 03 · AKTİF VİDEO\nDurum: {kod} aktif. ONAY 1 verildi ({tarih}).\n\n"
            f"## ONAYLI KONU KARTI\n{kart.strip()}\n")


def rit03_final_ekle(rit03: str, kod: str, final: str, tarih: str) -> str:
    govde = rit03.split("\n## ONAYLI FİNAL METİN", 1)[0].rstrip()
    no = 4 if kanal.ceviri_var() else 3
    govde = govde.replace("ONAY 1 verildi", f"ONAY 1 ve ONAY {no} verildi", 1)
    return (f"{govde}\n\n## ONAYLI FİNAL METİN · {kanal.dil_adi()} (etiketli, teslim satırlarıyla; ONAY {no}: {tarih})\n"
            f"{final.strip()}\n")
```

### `app/kanal_studyosu/ayarlar.py`

```python
"""Genel ayarlar (bütün kanallar için ortak), JSON yardımcıları ve API anahtarları.

Varsayılanlar config/varsayilan.json'dan gelir; kullanıcının değiştirdikleri kurulum klasöründeki
Sistem/ayarlar.json'da tutulur. Kanala özgü ayarlar kanalın kendi kanal.json dosyasındadır (kanallar.py).
"""
from __future__ import annotations

import copy
import json
import os
import platform
import re
import subprocess
import threading
from pathlib import Path

from . import yollar

UYGULAMA = "Kanal Stüdyosu"
SURUM = "1.2.3-windows"

ANAHTAR_SERVIS = "studio.kanal"
# Yazım servisleri: Claude Code (abonelik; anahtar gerekmez) ve OpenRouter. Doğrudan Anthropic API kaldırıldı.
SAGLAYICILAR = ("claude_code", "openrouter")
ANAHTARLAR = {"ai84": (ANAHTAR_SERVIS, "ai84-api-key", "AI84_API_KEY"),
              "openrouter": (ANAHTAR_SERVIS, "openrouter-api-key", "OPENROUTER_API_KEY")}

_KILIT = threading.RLock()


def atomik_yaz(yol: Path, metin: str) -> None:
    """Önce geçici dosyaya yazar, sonra yer değiştirir (yarım dosya kalmaz)."""
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = yol.with_name(yol.name + ".tmp")
    with _KILIT:
        with open(gecici, "w", encoding="utf-8") as f:
            f.write(metin)
            f.flush()
            os.fsync(f.fileno())
        os.replace(gecici, yol)


def json_yaz(yol: Path, veri) -> None:
    atomik_yaz(yol, json.dumps(veri, ensure_ascii=False, indent=2))


def json_oku(yol: Path, varsayilan=None):
    try:
        return json.loads(Path(yol).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return copy.deepcopy(varsayilan)


def birlestir(taban: dict, ust: dict) -> dict:
    sonuc = copy.deepcopy(taban)
    for k, v in ust.items():
        if isinstance(v, dict) and isinstance(sonuc.get(k), dict):
            sonuc[k] = birlestir(sonuc[k], v)
        else:
            sonuc[k] = copy.deepcopy(v)
    return sonuc


def varsayilan() -> dict:
    return json.loads((yollar.CONFIG / "varsayilan.json").read_text(encoding="utf-8"))


def genel() -> dict:
    """Yalnız genel ayarlar (bütün kanallar için ortak)."""
    a = birlestir(varsayilan(), json_oku(yollar.ayar_dosyasi(), {}) or {})
    if a.get("saglayici") not in SAGLAYICILAR:  # eski sürümde "anthropic" seçilmiş olabilir
        a["saglayici"] = "claude_code"
    return a


# Üretim kodundaki iş adları → kanal.json'daki iş adları
IS_ESLEME = {"A1": "konu", "A2": "arastirma", "A3": "senaryo", "A4": "ceviri", "A5": "sahne", "A6": "paketleme",
             "A6_2": "bolumler", "A6_2_yedek": "bolumler_yedek"}


def ayarlar() -> dict:
    """Genel ayarlar + seçili kanalın modelleri, sesi, video ayarları ve video bütçesi (üretim kodu buradan okur)."""
    from . import kanallar
    a = genel()
    akt = kanallar.aktif()
    k = kanallar.oku(akt) if akt else kanallar.varsayilan()
    a["isler"] = {ic: k["isler"][dis] for ic, dis in IS_ESLEME.items() if dis in k["isler"]}
    a["isler"].update({ad: v for ad, v in k["isler"].items() if ad not in IS_ESLEME.values()})
    a["ses"] = dict(k["ses"])
    a["video"] = dict(k["montaj"]["video"])
    a["butce"]["video_usd"] = k["butce"]["video_usd"]
    return a


IZINLI = {"yollar", "butce", "onbellek_suresi", "duzeltme_tur_siniri", "saglayici"}


def ayar_kaydet(degisiklik: dict) -> dict:
    """Yalnızca bilinen alanları kullanıcı dosyasına yazar."""
    kullanici = json_oku(yollar.ayar_dosyasi(), {}) or {}
    for k, v in degisiklik.items():
        if k not in IZINLI:
            raise ValueError(f"Bilinmeyen ayar: {k}")
        kullanici[k] = birlestir(kullanici[k], v) if isinstance(v, dict) and isinstance(kullanici.get(k), dict) else v
    yeni = birlestir(varsayilan(), kullanici)
    _dogrula(yeni)
    json_yaz(yollar.ayar_dosyasi(), kullanici)
    return yeni


def _dogrula(a: dict) -> None:
    if float(a["butce"]["aylik_usd"]) <= 0:
        raise ValueError("Aylık bütçe sıfırdan büyük olmalı")
    if a.get("saglayici", "claude_code") not in SAGLAYICILAR:
        raise ValueError("Yazım servisi Claude Code ya da OpenRouter olmalı")
    if a["onbellek_suresi"] not in ("5m", "1h"):
        raise ValueError("Önbellek süresi 5m ya da 1h olmalı")


def yol(ad: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(genel()["yollar"][ad])))


# --- Anahtarlar (Windows Kimlik Bilgisi Yöneticisi; keyring yoksa ortam değişkeni) ---

def anahtar(tur: str) -> str:
    from . import sistem_win
    servis, hesap, ortam = ANAHTARLAR[tur]
    return sistem_win.anahtar_oku(servis, hesap, ortam)


def anahtar_kaydet(tur: str, deger: str) -> None:
    servis, hesap, _ = ANAHTARLAR[tur]
    deger = str(deger).strip()
    if not re.fullmatch(r"[A-Za-z0-9_\-.:+/=]{8,512}", deger):
        raise ValueError("Anahtar beklenen biçimde değil")
    from . import sistem_win
    sistem_win.anahtar_yaz(servis, hesap, deger)


def anahtar_sil(tur: str) -> None:
    from . import sistem_win
    servis, hesap, _ = ANAHTARLAR[tur]
    sistem_win.anahtar_sil(servis, hesap)
```

### `app/kanal_studyosu/capcut_zinciri.py`

```python
"""CapCut zinciri: uygulamanın araçlar/ betiklerini sırayla çağırır (CapCut KAPALIYKEN).

srt_uret → odak (odak_izgara.py + görsel model) → capcut_taslak → senk_kontrol --metin
→ yayin_hazirla (müzik, 4 maskot, 8 sn son ekran) → senk_kontrol.
CapCut'ı açıp kontrol etmek ve dışa aktarmak kullanıcının işidir.
"""
from __future__ import annotations

import base64
import csv
import io
import json
import re
from pathlib import Path

from . import araclar
from . import ayarlar as A
from . import kanal
from . import kanallar
from . import kayit
from . import metin as M

ODAK_SORUSU = """Bu görsel bir kontak sayfası: her küçük resim bir video sahnesi, altında sarı sahne numarası var ve 3x3 ızgarayla bölünmüş.
Her sahne için yakınlaşmanın gideceği ODAK öğesinin, o sahnenin KENDİ küçük resmi içindeki merkezini ver.
Koordinatlar küçük resme göre 0–1 arasında: sol üst (0,0), sağ alt (1,1). Değerler 0,1–0,9 aralığında olsun.
Sahneler ve odak öğeleri:
{liste}
Yalnızca JSON ver, başka hiçbir şey yazma: {{"0001": [x, y], "0002": [x, y], ...}}"""


def taslak_klasoru(kod: str) -> Path:
    return A.yol("capcut_taslak") / kod


def srt(kod: str, video: Path) -> dict:
    d = kanal.video_klasoru(kod)
    c = araclar.calistir("srt_uret.py", str(video), str(d / "02_ElevenLabs_seslendirme_metni.txt"),
                         str(d / kanal.altyazi_adi(kod))).cikti
    m = re.search(r"cues (\d+) toplam ([\d:,]+)", c)
    return {"satir": int(m.group(1)) if m else None, "toplam": m.group(2) if m else ""}


def plan_satirlari(kod: str) -> list[dict]:
    yol = kanal.video_klasoru(kod) / "05_Montaj_plani.tsv"
    return [r for r in csv.DictReader(io.StringIO(yol.read_text(encoding="utf-8")), delimiter="\t") if r.get("sahne")]


def _json_al(metin: str) -> dict:
    m = re.search(r"\{.*\}", metin, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except ValueError:
        return {}


def _gecerli(n: str, deger) -> bool:
    return (isinstance(deger, list) and len(deger) == 2 and all(isinstance(v, (int, float)) for v in deger)
            and all(0.1 <= float(v) <= 0.9 for v in deger))


def odak(kod: str, video: Path, llm, ilerleme=lambda m: None) -> dict:
    """Kontak sayfalarına bakan görsel model (iş 'odak': Haiku; tutmazsa 'odak_yedek': Sonnet).
    Kod 0,1–0,9 aralığını ve eksik sahneyi denetler. → 06_Odak_noktalari.json"""
    hedef = kanal.arsiv_klasoru(kod) / "odak"
    araclar.calistir("odak_izgara.py", str(video), str(hedef))
    sayfalar = sorted(hedef.glob("sayfa*.jpg"), key=lambda p: int(re.search(r"\d+", p.stem).group(0)))
    plan = plan_satirlari(kod)
    sonuc: dict[str, list] = {}
    for i, sayfa in enumerate(sayfalar):
        sahneler = plan[i * 12:(i + 1) * 12]
        liste = "\n".join(f"{r['sahne']}: {r.get('odak') or 'ana öğe'}" for r in sahneler)
        resim = base64.standard_b64encode(sayfa.read_bytes()).decode()
        mesaj = [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": resim}},
            {"type": "text", "text": ODAK_SORUSU.format(liste=liste)}]}]
        for is_adi in ("odak", "odak_yedek"):
            ilerleme(f"Odak noktaları: sayfa {i + 1}/{len(sayfalar)}" + (" (yedek model)" if is_adi != "odak" else ""))
            j = _json_al(llm.istek(is_adi, kod, [], mesaj).metin)
            eksik = [r["sahne"] for r in sahneler if not _gecerli(r["sahne"], j.get(r["sahne"]))]
            if not eksik:
                break
            kayit.yaz(f"Odak sayfa {i + 1}: {len(eksik)} sahne geçersiz/eksik ({is_adi})", "uyari")
        for r in sahneler:
            sonuc[r["sahne"]] = [round(float(v), 3) for v in j[r["sahne"]]] if _gecerli(r["sahne"], j.get(r["sahne"])) \
                else [0.5, 0.45]  # iki model de veremezse güvenli varsayılan; raporda belirtilir
    varsayilan = [n for n, v in sonuc.items() if v == [0.5, 0.45]]
    A.json_yaz(kanal.video_klasoru(kod) / "06_Odak_noktalari.json", sonuc)
    return {"sahne": len(sonuc), "varsayilan": varsayilan}


def taslak(kod: str, video: Path) -> dict:
    if taslak_klasoru(kod).exists():
        raise araclar.AracHatasi(f"CapCut'ta '{kod}' adlı taslak zaten var. Uygulama mevcut taslağa dokunmaz; "
                                 "CapCut'ta adını değiştirip Tekrar dene.")
    d = kanal.video_klasoru(kod)
    c = araclar.calistir("capcut_taslak.py", "--video", str(video), "--plan", str(d / "05_Montaj_plani.tsv"),
                         "--odak", str(d / "06_Odak_noktalari.json"), "--srt", str(d / kanal.altyazi_adi(kod)),
                         "--ad", kod).cikti
    if taslak_klasoru(kod).is_dir():  # iki iz: kanal silinirken yalnız Kanal Stüdyosu'nun taslakları Çöp'e gider
        kanallar.taslak_kaydet(kanal.secili(), taslak_klasoru(kod))
    m = re.search(r"^ok .*?([\d.]+) sn sahne (\d+) altyazi (\d+)\s*\n(.*)", c, re.M)
    istatistik = _json_al(m.group(4)) if m else {}
    return {"sure": m.group(1) if m else "", "sahne": int(m.group(2)) if m else None,
            "altyazi": int(m.group(3)) if m else None, "istatistik": istatistik}


NORMAL_NOTLAR = ("konusma hizi farkli", "sessizlik")  # SKILL 10b-4: bunlar beklenen durumlar


def senk(kod: str, metin: bool = False) -> dict:
    c = araclar.calistir("senk_kontrol.py", kod, *(["--metin"] if metin else [])).cikti
    satirlar = c.splitlines()
    i = next((k for k, s in enumerate(satirlar) if s.startswith("SONUC:")), len(satirlar))
    notlar = [s for s in satirlar[i + 1:] if s.strip() and not re.match(r"^\d{4} ", s)] if i < len(satirlar) else []
    return {"temiz": i < len(satirlar) and "TEMIZ" in satirlar[i],
            "sorunlar": [s for s in notlar if not any(k in s for k in NORMAL_NOTLAR)],
            "normal": [s for s in notlar if any(k in s for k in NORMAL_NOTLAR)],
            "son_ekran": next((s for s in satirlar if s.startswith("son ekran var")), ""),
            "ozet": "\n".join(satirlar[:i + 1])[-1500:]}


def maskot_argumanlari(maskot: str) -> list[str]:
    """Yalnız '--maskot SAHNE:M:SÜRE' çiftleri (eski sürümün kaydına karışmış başka sözcükler atılır)."""
    p = (maskot or "").split()
    return [x for i in range(len(p) - 1) if p[i] == "--maskot" and re.fullmatch(r"\d+:\d+:\d+(?:\.\d+)?", p[i + 1])
            for x in (p[i], p[i + 1])]


MUZIK_UZANTI = (".mp3", ".m4a", ".wav", ".aac", ".flac")


def muzik_dosyalari() -> list[Path]:
    k = kanal.kok() / "Varliklar" / "Muzik"
    return sorted(f for f in k.glob("*") if f.suffix.lower() in MUZIK_UZANTI and not f.name.startswith(".")) \
        if k.is_dir() else []


def yayin_hazirla(kod: str, maskot: str) -> dict:
    arg = maskot_argumanlari(maskot)
    k = kanal.ayar()["montaj"]
    bos = k["muzik"] and not muzik_dosyalari()
    if bos:  # kanal kartındaki uyarının söylediği gibi: müziksiz devam
        kayit.yaz(f"{kod}: müzik açık ama Varliklar/Muzik klasörü boş; montaj müziksiz yapılıyor", "uyari")
    arg += ["--son-sn", str(k["son_ekran_sn"])] + ([] if k["muzik"] and not bos else ["--muziksiz"])
    try:
        c = araclar.calistir("yayin_hazirla.py", kod, *arg, zaman_asimi=3600).cikti
    except araclar.AracHatasi:
        # Uzun maskot üretiminde yarıda kalabilir; tekrar çalıştırılınca bitmiş maskotları atlar (BENI_OKU).
        kayit.yaz("yayin_hazirla bir kez daha deneniyor", "uyari")
        c = araclar.calistir("yayin_hazirla.py", kod, *arg, zaman_asimi=3600).cikti
    # muzik_otomatik.py de "tamam …" yazar; yayin_hazirla'nın satırı "| muzik:" içeren sonuncusudur.
    tamam = [s for s in re.findall(r"^tamam .*", c, re.M) if "| muzik:" in s]
    if not tamam:
        raise araclar.AracHatasi("yayin_hazirla.py beklenen 'tamam' satırını vermedi.", c[-4000:])
    secilen = re.search(r"secilen:.*", c)
    return {"satir": tamam[-1], "muzik": "muzik: var" in tamam[-1],
            "secilen": secilen.group(0) if secilen else
            ("yok: Varliklar/Muzik klasörü boş olduğu için müziksiz üretildi" if bos else "")}


def muzik_yenile(kod: str) -> str:
    """Bitmiş taslağın müziğini yeniden yapar (muzik_otomatik.py --ekle): yeni rastgele parçalar, eski müzik dosyası ve
    taslak arşive kopyalanır. CapCut kapalı olmalı. Döner: seçilen parçalar satırı."""
    if capcut_acik():
        raise araclar.AracHatasi("CapCut açık. Önce CapCut'ı kapat, sonra yeniden dene.")
    if not muzik_dosyalari():
        raise araclar.AracHatasi("Varliklar/Muzik klasöründe parça yok. Kanal kartında Klasörü aç ile müzik ekle.")
    son = str(kanal.ayar()["montaj"]["son_ekran_sn"])
    c = araclar.calistir("muzik_otomatik.py", kod, "--ekle", "--son-sn", son, zaman_asimi=1800).cikti
    secilen = re.search(r"secilen:.*", c)
    return secilen.group(0) if secilen else "yenilendi"


def capcut_acik() -> bool:
    from .onkontrol import capcut_acik as acik
    return acik()


def bolum_zamanlari(kod: str) -> list[dict]:
    """Taslaktaki her 'bolum' değişiminin başlangıcı (m:ss) ve o sahnenin ilk cümlesi (SKILL 10c)."""
    dr = json.loads((taslak_klasoru(kod) / "draft_info.json").read_text(encoding="utf-8"))
    segler = [t for t in dr["tracks"] if t["type"] == "video"][0]["segments"]
    plan = plan_satirlari(kod)
    paragraflar = [M.govde(p) for p in
                   (kanal.video_klasoru(kod) / "02_ElevenLabs_seslendirme_metni.txt").read_text(encoding="utf-8")
                   .strip().split("\n\n") if p.strip()]
    sonuc, onceki = [], None
    for i, r in enumerate(plan):
        if r["bolum"] != onceki and i < len(segler):
            bas = segler[i]["target_timerange"]["start"] / 1e6
            m, s = divmod(int(bas), 60)
            ilk = re.split(r"(?<=[.!?…»])\s+", paragraflar[i])[0] if i < len(paragraflar) else ""
            sonuc.append({"zaman": f"{m}:{s:02d}", "bolum": r["bolum"], "sahne": r["sahne"], "ilk_cumle": ilk})
        onceki = r["bolum"]
    return sonuc
```

### `app/kanal_studyosu/cikti.py`

````python
"""Model cevabını dosyalara, yamalara ve sohbet özetine ayırır.

Uygulama çerçevesi modele şu biçimi söyler:
  <dosya ad="ORN-VID-06_3_senaryo_tr.md"> … </dosya>
  <yama dosya="…" paragraf="12" [islem="sil|sonrasina_ekle"]> … </yama>
  <yama dosya="…" satir="Başlık"> … </yama>
  <yama dosya="…" bolum="§4"> … </yama>
  <yama dosya="…" kuyruk="1"> … </yama>
  <ozet> … </ozet>
  Açık noktalar: ¶12 … | yok   (sohbet cevabının son satırı; ayrı alana alınır)
Etiket yoksa ve beklenen dosya sayısı kadar kod bloğu varsa, bloklar sırayla
dosyalara eşlenir (becerilerdeki "dosya aracı yoksa kod bloğu" kuralı).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

DOSYA = re.compile(r'<dosya\s+ad="([^"]+)"\s*>(.*?)</dosya>', re.S)
YAMA = re.compile(r"<yama\s+([^>]*)>(.*?)</yama>", re.S)
OZET = re.compile(r"<ozet>(.*?)</ozet>", re.S)
OZNITELIK = re.compile(r'(\w+)="([^"]*)"')
KOD_BLOGU = re.compile(r"```[^\n]*\n(.*?)\n```", re.S)
# Sohbet cevabının sonundaki düz yazı satır: "Açık noktalar: ¶12 … " ya da "Açık noktalar: yok".
# Dosyalardan ayrı tutulur ve ekranda ayrı gösterilir; seslendirmeye ya da sahne akışına gitmez.
ACIK = re.compile(r"^[ \t>*_-]*Açık noktalar[ \t*_]*:[ \t*_]*(.*?)[ \t*_]*$", re.M | re.I)


@dataclass
class Ayrisma:
    dosyalar: dict[str, str] = field(default_factory=dict)
    yamalar: dict[str, list[dict]] = field(default_factory=dict)
    ozet: str = ""
    acik_noktalar: str = ""


def _cit_temizle(icerik: str) -> str:
    """Dosya içeriği bir kod bloğuna sarılmışsa çitleri kaldırır."""
    s = icerik.strip("\n")
    m = re.fullmatch(r"\s*```[^\n]*\n(.*?)\n```\s*", s, re.S)
    return (m.group(1) if m else s).strip("\n") + "\n"


def ayristir(metin: str, beklenen: list[str] | None = None) -> Ayrisma:
    a = Ayrisma()
    for ad, icerik in DOSYA.findall(metin):
        a.dosyalar[ad.strip()] = _cit_temizle(icerik)
    for oz, icerik in YAMA.findall(metin):
        o = dict(OZNITELIK.findall(oz))
        if "dosya" not in o:
            continue
        y: dict = {"icerik": icerik.strip("\n")}
        if "paragraf" in o:
            y["paragraf"] = int(o["paragraf"])
            y["islem"] = o.get("islem", "degistir")
        elif "satir" in o:
            y["satir"] = o["satir"]
        elif "bolum" in o:
            y["bolum"] = o["bolum"]
        elif o.get("kuyruk"):
            y["kuyruk"] = True
        else:
            continue
        a.yamalar.setdefault(o["dosya"].strip(), []).append(y)
    disari = YAMA.sub("", DOSYA.sub("", metin))  # dosya/yama içerikleri hariç sohbet metni
    acik = ACIK.findall(re.sub(r"</?ozet>", "\n", disari))
    if acik:
        a.acik_noktalar = acik[-1].strip().strip("«»\"'`").strip()  # «yok» → yok
    m = OZET.search(metin)
    if m:
        a.ozet = ACIK.sub("", m.group(1)).strip()
    if not a.dosyalar and not a.yamalar and beklenen:
        bloklar = KOD_BLOGU.findall(metin)
        if len(bloklar) == len(beklenen):
            a.dosyalar = {ad: b.strip("\n") + "\n" for ad, b in zip(beklenen, bloklar)}
    if not a.ozet:
        kalan = ACIK.sub("", OZET.sub("", disari)).strip()
        a.ozet = kalan[:3000]
    return a
````

### `app/kanal_studyosu/claude_code.py`

```python
"""Claude Code (abonelik) üzerinden yazım.

Uygulama `claude` komutunu ekransız (-p) çalıştırır; Claude Code kullanıcının Pro/Max aboneliğiyle giriş yapmış
olmalıdır. Her istekte:
- sistem metni bizimkidir (proje dosyaları + beceri + çerçeve + KANAL AYARLARI): `--system-prompt-file`;
  Claude Code'un kod asistanı talimatları kullanılmaz,
- mesaj `--input-format stream-json` ile verilir (görseller de aynı biçimde gider; araç gerekmez),
- araçlar kapalıdır (`--tools ""`); yalnız web araması olan işlerde (1–2. aşama) `WebSearch` açılır,
- kullanıcının Claude Code ayarları, becerileri, eklentileri ve MCP sunucuları yüklenmez (`--safe-mode`,
  `--strict-mcp-config`); çalışma klasörü boş bir klasördür (Sistem/claude_code), dosyalara dokunamaz,
- ANTHROPIC_API_KEY gibi değişkenler ortamdan çıkarılır: istek API'ye değil aboneliğe gider,
- düzeltme turunda aynı Claude Code oturumu `--resume` ile sürdürülür (model önceki yazdığını hatırlar).
Eski bir Claude Code sürümü bir bayrağı tanımazsa o bayrak çıkarılıp yeniden denenir ve kayda yazılır.
Ücret token başına değil aboneliktir; Claude Code'un verdiği tahmini tutar yalnız bilgi olarak kaydedilir.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

from . import ayarlar as A
from . import kayit
from . import yollar
from .sistem_win import gizli

ZAMAN_ASIMI = 45 * 60          # bir çağrı en fazla (sn)
EN_FAZLA_TUR = 40               # web aramalı işlerde ajan turları
_TEMIZLENECEK_ORTAM = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_USE_BEDROCK",
                       "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY", "ANTHROPIC_MODEL")
_ATILAN_BAYRAKLAR: set[str] = set()  # bu Claude Code sürümünün tanımadığı bayraklar (oturum boyunca)


class ClaudeCodeHatasi(Exception):
    """Kullanıcıya gösterilecek kısa Türkçe mesaj."""


def komut_yolu() -> str | None:
    """`claude` programının yolu (PATH'te yoksa Windows'taki bilinen kurulum yerlerine de bakılır)."""
    ozel = os.environ.get("KANAL_STUDYOSU_CLAUDE")
    if ozel:
        return ozel
    bulunan = shutil.which("claude")
    if bulunan:
        return bulunan
    ev = Path.home()
    appdata = Path(os.environ.get("APPDATA", str(ev / "AppData/Roaming")))
    yerel = Path(os.environ.get("LOCALAPPDATA", str(ev / "AppData/Local")))
    for aday in (ev / ".local/bin/claude.exe", ev / ".claude/local/claude.exe", appdata / "npm/claude.cmd",
                 yerel / "Programs/claude/claude.exe", ev / ".local/bin/claude"):
        if aday.exists():
            return str(aday)
    return None


def _komut(yol: str) -> list[str]:
    """npm kurulumundaki claude.cmd doğrudan çalıştırılamaz; cmd /c ile çağrılır."""
    return ["cmd", "/c", yol] if yol.lower().endswith((".cmd", ".bat")) else [yol]


def calisma_klasoru() -> Path:
    k = yollar.sistem() / "claude_code"
    k.mkdir(parents=True, exist_ok=True)
    return k


def _ortam() -> dict:
    ev = Path.home()
    yol = os.pathsep.join([str(ev / ".local" / "bin"), str(Path(os.environ.get("APPDATA", str(ev / "AppData/Roaming"))) / "npm"),
                           os.environ.get("PATH", "")])
    o = {k: v for k, v in os.environ.items() if k.upper() not in _TEMIZLENECEK_ORTAM}
    o.update(PATH=yol, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1", PYTHONUTF8="1")
    return o


def durum() -> tuple[bool, str]:
    """Kurulu mu, abonelikle giriş yapılmış mı (ücretsiz; model çağrılmaz)."""
    yol = komut_yolu()
    if not yol:
        return False, "Claude Code bulunamadı. Kurmak için: https://claude.com/claude-code (PowerShell'de `claude --version` çalışmalı)."
    try:
        surum = subprocess.run(_komut(yol) + ["--version"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=30, env=_ortam(), **gizli()).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, f"Claude Code çalıştırılamadı ({e})."
    try:
        p = subprocess.run(_komut(yol) + ["auth", "status"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30, env=_ortam(), **gizli())
        j = json.loads(p.stdout or "{}")
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return True, f"Claude Code kurulu ({surum}). Giriş durumu okunamadı; ilk yazımda denenecek."
    yontem = j.get("authMethod", "")
    if p.returncode != 0 or yontem in ("", "none"):
        return False, f"Claude Code kurulu ({surum}) ama giriş yapılmamış. PowerShell'de `claude` yazıp /login ile aboneliğinle giriş yap."
    if yontem != "claude.ai":
        return True, (f"Claude Code kurulu ({surum}); giriş yöntemi '{yontem}'. Abonelik (claude.ai) değilse ücret API "
                      "hesabından düşer.")
    return True, f"Claude Code kurulu ({surum}), abonelikle giriş yapılmış."


# --- mesajlar ----------------------------------------------------------------------

def _icerik_listesi(icerik) -> list[dict]:
    if isinstance(icerik, str):
        return [{"type": "text", "text": icerik}]
    return [b for b in icerik if b.get("type") in ("text", "image")]


def _metin(icerik) -> str:
    return "\n\n".join(b.get("text", "") for b in _icerik_listesi(icerik) if b.get("type") == "text")


def oturum_kimligi(mesaj: dict) -> str:
    if mesaj.get("role") != "assistant" or not isinstance(mesaj.get("content"), list):
        return ""
    return next((b.get("oturum", "") for b in mesaj["content"] if b.get("oturum")), "")


def plan(mesajlar: list[dict]) -> tuple[str, list[dict]]:
    """→ (sürdürülecek oturum kimliği ya da '', gönderilecek kullanıcı içeriği).
    Son asistan turunda Claude Code oturumu varsa yalnız ondan sonraki kullanıcı mesajları gönderilir; yoksa (ilk tur
    ya da yazım servisi sonradan değiştiyse) konuşmanın tamamı tek mesajda verilir."""
    son = max((i for i, m in enumerate(mesajlar) if oturum_kimligi(m)), default=-1)
    if son >= 0 and all(m.get("role") == "user" for m in mesajlar[son + 1:]) and mesajlar[son + 1:]:
        icerik: list[dict] = []
        for m in mesajlar[son + 1:]:
            icerik += _icerik_listesi(m["content"])
        return oturum_kimligi(mesajlar[son]), icerik
    if len(mesajlar) == 1:
        return "", _icerik_listesi(mesajlar[0]["content"])
    # Önceki turlar başka bir servisle yazıldı: konuşma metin olarak aktarılır, son kullanıcı mesajı aynen eklenir.
    gecmis = []
    for m in mesajlar[:-1]:
        kim = "KULLANICI" if m.get("role") == "user" else "SEN (önceki cevabın)"
        gecmis.append(f"<tur kim=\"{kim}\">\n{_metin(m['content'])}\n</tur>")
    on = {"type": "text", "text": "Bu konuşmanın önceki turları aşağıda. Onların devamı olarak cevap ver.\n\n"
          + "\n\n".join(gecmis)}
    return "", [on] + _icerik_listesi(mesajlar[-1]["content"])


# --- çağrı -----------------------------------------------------------------------

def _bayraklar(model: str, efor: str | None, web: bool, oturum: str, sistem_dosyasi: Path) -> list[str]:
    b = ["-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
         "--include-partial-messages", "--model", model, "--system-prompt-file", str(sistem_dosyasi),
         "--safe-mode", "--strict-mcp-config", "--max-turns", str(EN_FAZLA_TUR if web else 3)]
    if web:
        b += ["--tools", "WebSearch", "--allowedTools", "WebSearch"]
    else:
        b += ["--tools", ""]
    if efor:
        b += ["--effort", efor]
    if oturum:
        b += ["--resume", oturum]
    sonuc, i = [], 0
    while i < len(b):  # tanınmayan bayraklar (ve değerleri) çıkarılır
        tek = b[i] in ("-p", "--verbose", "--include-partial-messages", "--safe-mode", "--strict-mcp-config")
        if b[i] in _ATILAN_BAYRAKLAR:
            i += 1 if tek else 2
            continue
        sonuc += [b[i]] if tek else b[i:i + 2]
        i += 1 if tek else 2
    return sonuc


def _hata_mesaji(metin: str) -> str:
    m = metin.lower()
    if re.search(r"usage limit|rate limit|limit reached|limit will reset|resets|5-hour|weekly limit|out of extra usage", m):
        saat = re.search(r"reset[s]?\s*(?:at)?\s*([0-9:apm\s]+(?:\([^)]*\))?)", metin, re.I)
        return ("Claude Code kullanım sınırına ulaşıldı" + (f" (açılış: {saat.group(1).strip()})" if saat else "") +
                ". Sınır açılınca Tekrar dene; adım kaldığı yerden sürer.")
    if re.search(r"not logged in|please run /login|invalid api key|authentication|oauth token|log in", m):
        return "Claude Code'da giriş yapılmamış ya da oturum süresi dolmuş. PowerShell'de `claude` yazıp /login ile aboneliğinle giriş yap, sonra Tekrar dene."
    if re.search(r"credit balance|billing", m):
        return "Claude Code hesabı ücret/kredi hatası verdi. Abonelikle giriş yaptığından emin ol (claude /login)."
    if re.search(r"overloaded|529|internal server error|api error: 5\d\d|connection", m):
        return "Claude şu an yoğun ya da ulaşılamıyor. Biraz sonra Tekrar dene."
    return "Claude Code bir hata verdi. Ayrıntı kayıt panelinde."


def istek(is_adi: str, sistem: list[str], mesajlar: list[dict], ilerleme=None, iptal=None) -> dict:
    """Claude Code'u çalıştırır. Döner: {'metin', 'oturum', 'kullanim', 'model', 'tahmini_usd', 'sunulan'}."""
    yol = komut_yolu()
    if not yol:
        raise ClaudeCodeHatasi("Claude Code bulunamadı. Kurup PowerShell'de `claude` ile aboneliğinle giriş yap.")
    ayar = A.ayarlar()
    isa = ayar["isler"][is_adi]
    model = isa["model"]
    efor = isa.get("efor") if ayar["modeller"].get(model, {}).get("efor") else None
    web = bool(isa.get("web_arama"))
    oturum, icerik = plan(mesajlar)
    kl = calisma_klasoru()
    sistem_dosyasi = kl / f"sistem_{os.getpid()}_{threading.get_ident()}.md"
    sistem_dosyasi.write_text("\n\n".join(t for t in sistem if t) or "Türkçe, kısa ve doğru cevap ver.", encoding="utf-8")
    ortam = _ortam()
    ortam["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(int(isa.get("max_token", 32000)))
    girdi = json.dumps({"type": "user", "message": {"role": "user", "content": icerik}}, ensure_ascii=False) + "\n"
    try:
        for _deneme in range(6):
            komut = _komut(yol) + _bayraklar(model, efor, web, oturum, sistem_dosyasi)
            sonuc = _calistir(komut, girdi, ortam, kl, ilerleme, iptal)
            tanimsiz = re.search(r"unknown option '?(--[\w-]+)", sonuc["stderr"], re.I)
            if sonuc["kod"] != 0 and tanimsiz and tanimsiz.group(1) not in _ATILAN_BAYRAKLAR:
                _ATILAN_BAYRAKLAR.add(tanimsiz.group(1))
                kayit.yaz(f"Claude Code bu sürümde {tanimsiz.group(1)} bayrağını tanımıyor; onsuz deneniyor", "uyari")
                continue
            break
    finally:
        sistem_dosyasi.unlink(missing_ok=True)
    son = sonuc["sonuc"]
    if son is None or son.get("is_error") or son.get("subtype") not in (None, "success"):
        metin = json.dumps(son, ensure_ascii=False)[:1500] if son else ""
        ayrinti = (metin + "\n" + sonuc["stderr"][-1500:]).strip()
        kayit.yaz(f"Claude Code hatası ({is_adi}, çıkış {sonuc['kod']}): {ayrinti}", "hata")
        if son and son.get("subtype") == "error_max_turns":
            raise ClaudeCodeHatasi("Claude Code tur sınırına ulaştı (web araması çok uzadı). Tekrar dene.")
        raise ClaudeCodeHatasi(_hata_mesaji(ayrinti))
    metin = "\n\n".join(t for t in sonuc["metinler"] if t.strip()) or son.get("result", "")
    u = son.get("usage") or {}
    stu = u.get("server_tool_use") or {}
    kullanim = {k: int(u.get(k) or 0) for k in
                ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
    kullanim["web_search_requests"] = int(stu.get("web_search_requests") or 0)
    sunulan = next(iter(son.get("modelUsage") or {}), "") or model
    return {"metin": metin, "oturum": son.get("session_id", ""), "kullanim": kullanim, "model": model,
            "tahmini_usd": float(son.get("total_cost_usd") or 0), "sunulan": sunulan}


def _calistir(komut: list[str], girdi: str, ortam: dict, kl: Path, ilerleme, iptal) -> dict:
    from .llm import Durduruldu
    try:
        p = subprocess.Popen(komut, cwd=str(kl), env=ortam, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", bufsize=1, **gizli())
    except OSError as e:
        raise ClaudeCodeHatasi(f"Claude Code başlatılamadı ({e}).")
    hata_parcalari: list[str] = []
    threading.Thread(target=lambda: hata_parcalari.append(p.stderr.read()), daemon=True).start()
    p.stdin.write(girdi)
    p.stdin.close()
    metinler: list[str] = []
    sonuc = None
    yazilan = 0
    baslangic = time.time()
    satirlar: list[str] = []
    okuyucu_bitti = threading.Event()

    def oku():
        for s in p.stdout:
            satirlar.append(s)
        okuyucu_bitti.set()
    threading.Thread(target=oku, daemon=True).start()
    islenen = 0
    while True:
        bitti = okuyucu_bitti.wait(0.3)
        while islenen < len(satirlar):
            s = satirlar[islenen].strip()
            islenen += 1
            if not s.startswith("{"):
                continue
            try:
                o = json.loads(s)
            except ValueError:
                continue
            tur = o.get("type")
            if tur == "stream_event":
                ol = o.get("event") or {}
                if ol.get("type") == "content_block_delta" and (ol.get("delta") or {}).get("type") == "text_delta":
                    yazilan += len(ol["delta"].get("text", ""))
                    if ilerleme:
                        ilerleme(yazilan)
            elif tur == "assistant" and not o.get("parent_tool_use_id"):
                metin = "".join(b.get("text", "") for b in (o.get("message") or {}).get("content", [])
                                if b.get("type") == "text")
                if metin:
                    metinler.append(metin)
            elif tur == "result":
                sonuc = o
        if bitti:
            break
        if iptal and iptal():
            p.terminate()
            raise Durduruldu("Durduruldu. Tekrar dene ile bu adım baştan yazılır.")
        if time.time() - baslangic > ZAMAN_ASIMI:
            p.terminate()
            raise ClaudeCodeHatasi(f"Claude Code {ZAMAN_ASIMI // 60} dakikada bitmedi. Tekrar dene.")
    try:
        kod = p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        kod = -9
    time.sleep(0.05)
    return {"kod": kod, "sonuc": sonuc, "metinler": metinler, "stderr": "".join(hata_parcalari)}
```

### `app/kanal_studyosu/cop.py`

```python
"""Geri Dönüşüm Kutusu'na taşıma (kalıcı silme yok; Geri Dönüşüm Kutusu boşaltılana kadar geri alınabilir).

Windows'ta send2trash kütüphanesiyle taşınır ("Geri yükle" çalışır). KANAL_STUDYOSU_COP ortam değişkeni verilirse
(testler) oraya taşınır.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def _benzersiz(hedef: Path) -> Path:
    if not hedef.exists():
        return hedef
    return hedef.with_name(f"{hedef.name} {datetime.now().strftime('%Y%m%d-%H%M%S')}")


def tasi(yol: Path) -> Path | None:
    """yol'u Çöp'e taşır; taşınan yeri (biliniyorsa) döndürür. Yol yoksa None."""
    yol = Path(yol)
    if not yol.exists():
        return None
    ozel = os.environ.get("KANAL_STUDYOSU_COP")
    if not ozel and platform.system() == "Windows":
        from send2trash import send2trash
        send2trash(str(yol))
        if not yol.exists():
            return None
    cop = Path(ozel) if ozel else Path.home() / ".local/share/Trash/files"
    cop.mkdir(parents=True, exist_ok=True)
    hedef = _benzersiz(cop / yol.name)
    shutil.move(str(yol), str(hedef))
    return hedef
```

### `app/kanal_studyosu/defter.py`

````python
"""Kanal Defteri (02_Defter.md) yenileme.

1) Yeni defteri model (iş: "defter", Sonnet) yazar: 1. aşamanın defter değişiklikleri +
   6. aşamanın DEFTER KAYDI + açılış–kapanış defteri çıktısı + süre/sahne.
2) Kod yapıyı denetler: A tablosunda her video kodu tek satır, sıralı, eksik yok; bölümler duruyor.
   Sorun varsa en fazla 2 düzeltme turu.
3) Eski defter Arsiv/<KOD>/'a, yenisinin tarihli kopyası Defter_arsivi/'ne yazılır.
4) 02_Defter.md yenisiyle değiştirilir. Hiçbir şey silinmez.
"""
from __future__ import annotations

import re
from datetime import datetime

from . import ayarlar as A
from . import cikti
from . import kanal
from . import kayit
from .kontroller import Sonuc

DEFTER = kanal.DEFTER

GOREV = """# GÖREV: KANAL DEFTERİNİ YENİLE (Kanal Stüdyosu)
Bu konuşma Kanal Stüdyosu uygulamasında, API üzerinden yürüyor. Sana mevcut 02_Defter.md ve bu videonun kayıtları <belge> olarak veriliyor. 00_Yonetici.md'deki düzenle defterin YENİ TAM HÂLİNİ yaz:
- 1. aşamanın defter değişikliklerini uygula.
- 6. aşamanın DEFTER KAYDI bloğunu ilgili bölümlere işle (A satırı, D, E, F, mekanik etiketler).
- F bölümündeki açılış–kapanış tablosunu ve kalıp sayılarını verilen Açılış–Kapanış Defteri çıktısıyla güncelle.
- Videonun süre/sahne bilgisini A tablosuna yaz.
- Başka satırlara dokunma; hiçbir videoyu silme. A tablosunda her video kodu tek satırdır ve kodlar sıralıdır.
- Başlıktaki sürüm satırını bugünün tarihiyle güncelle.
Çıktı biçimi: <dosya ad="02_Defter.md">yeni defterin tamamı</dosya> ve <ozet>en fazla 5 satır: neler değişti</ozet>."""


def _bolumler(metin: str) -> list[str]:
    return re.findall(r"^## ([A-Z])\.", metin, re.M)


def yapi_kontrol(eski: str, yeni: str, kod: str) -> Sonuc:
    s = Sonuc()
    eski_kodlar = [r["Kod"] for r in kanal.defter_tablosu(eski)]
    yeni_kodlar = [r["Kod"] for r in kanal.defter_tablosu(yeni)]
    beklenen = sorted(set(eski_kodlar) | {kod}, key=lambda k: int(k.rsplit("-", 1)[1]))
    s.bilgiler.append(f"A tablosu: {len(yeni_kodlar)} video")
    ciftler = sorted({k for k in yeni_kodlar if yeni_kodlar.count(k) > 1})
    if ciftler:
        s.hatalar.append(f"A tablosunda birden fazla satırı olan kod: {', '.join(ciftler)}")
    eksik = [k for k in beklenen if k not in yeni_kodlar]
    if eksik:
        s.hatalar.append(f"A tablosunda eksik kod: {', '.join(eksik)}")
    fazla = [k for k in yeni_kodlar if k not in beklenen]
    if fazla:
        s.hatalar.append(f"A tablosunda beklenmeyen kod: {', '.join(fazla)}")
    if not ciftler and yeni_kodlar != sorted(yeni_kodlar, key=lambda k: int(k.rsplit("-", 1)[1])):
        s.hatalar.append("A tablosunda kodlar sıralı değil.")
    kayip = [b for b in _bolumler(eski) if b not in _bolumler(yeni)]
    if kayip:
        s.hatalar.append(f"Bölüm(ler) kaybolmuş: {', '.join(kayip)}")
    if len(yeni) < 0.8 * len(eski):
        s.hatalar.append(f"Yeni defter eskisinden çok kısa ({len(yeni)} / {len(eski)} karakter); içerik silinmiş olabilir.")
    return s


def defter_kaydi(paket_md: str) -> str:
    """6. aşama paketinden DEFTER KAYDI bloğu (bulunamazsa paketin tamamı)."""
    satirlar = paket_md.splitlines()
    bas = next((i for i, l in enumerate(satirlar) if "DEFTER KAYDI ·" in l), None)
    if bas is None:
        return paket_md
    son = next((j for j in range(bas + 1, len(satirlar))
                if satirlar[j].startswith("```") or satirlar[j].startswith("## ")), len(satirlar))
    return "\n".join(satirlar[bas:son]).strip()


def yenile(llm, kod: str, sure_sahne: str, acilis_kapanis: str, ilerleme=None, butce_onayli=False) -> dict:
    from .asamalar import belge
    arsiv = kanal.arsiv_klasoru(kod)
    eski = kanal.rit(DEFTER)
    degisiklik = (arsiv / f"{kod}_1_defter_degisiklikleri.md").read_text(encoding="utf-8")
    paket = (arsiv / f"{kod}_6_paket.md").read_text(encoding="utf-8")
    sistem = ["\n\n".join(f"# PROJE DOSYASI: {ad}\n\n{kanal.rit(ad)}" for ad in kanal.PROJE_DOSYALARI[:2]), GOREV]
    mesajlar = [{"role": "user", "content": "\n\n".join([
        f"{kod} üretimi bitti. Kanal Defteri'ni yenile. Bugün: {datetime.now().strftime('%d.%m.%Y')}. "
        f"{kod} süre / sahne: {sure_sahne}.",
        belge(DEFTER, eski), belge(f"{kod}_1_defter_degisiklikleri.md", degisiklik),
        belge(f"{kod} DEFTER KAYDI", defter_kaydi(paket)),
        belge("Acilis_Kapanis_Defteri.md", acilis_kapanis)])}]
    sinir = int(A.ayarlar()["duzeltme_tur_siniri"])
    for tur in range(sinir + 1):
        cevap = llm.istek("defter", kod, sistem, mesajlar, ilerleme=ilerleme, butce_onayli=butce_onayli and tur == 0,
                          tur=f"oto_duzeltme_{tur}" if tur else "ilk")
        mesajlar += cevap.ek_mesajlar + [{"role": "assistant", "content": cevap.icerik}]
        a = cikti.ayristir(cevap.metin, [DEFTER])
        yeni = a.dosyalar.get(DEFTER, "")
        sonuc = yapi_kontrol(eski, yeni, kod) if yeni else Sonuc(hatalar=["Yeni defter dosyası verilmedi."])
        if sonuc.temiz:
            break
        if tur < sinir:
            kayit.yaz(f"Defter: yapı kontrolü {len(sonuc.hatalar)} sorun buldu, düzeltme {tur + 1}/{sinir}")
            mesajlar.append({"role": "user", "content": "Düzeltme (uygulamanın yapı kontrolü):\n" +
                             "\n".join(f"- {h}" for h in sonuc.hatalar) +
                             "\nDefterin tamamını <dosya> ile yeniden ver."})
    A.json_yaz(kanal.uygulama_klasoru(kod) / "konusma_defter.json", {"sistem": sistem, "mesajlar": mesajlar})
    if not sonuc.temiz:
        # Defter değiştirilmez; aday arşive yazılır, kullanıcıya gösterilir.
        if yeni:
            A.atomik_yaz(arsiv / "02_Defter_yeni_aday_KONTROLDEN_GECMEDI.md", yeni)
        return {"tamam": False, "kontrol": sonuc.sozluk(), "ozet": a.ozet}
    damga = datetime.now()
    A.atomik_yaz(arsiv / f"02_Defter_oncesi_{damga.strftime('%Y%m%d_%H%M%S')}.md", eski)
    tarihli = kanal.kok() / "Defter_arsivi" / f"{damga.strftime('%Y-%m-%d')}_02_Defter.md"
    if tarihli.exists():
        tarihli = tarihli.with_name(f"{damga.strftime('%Y-%m-%d_%H%M%S')}_02_Defter.md")
    A.atomik_yaz(tarihli, yeni)
    A.atomik_yaz(kanal.proje_klasoru() / DEFTER, yeni)
    kayit.yaz(f"{kod}: Kanal Defteri yenilendi (tarihli kopya: {tarihli.name})")
    return {"tamam": True, "kontrol": sonuc.sozluk(), "ozet": a.ozet, "tarihli": str(tarihli)}
````

### `app/kanal_studyosu/dosya_duzeni.py`

```python
"""Dosya düzeni ve silme politikası.

- Bu modül hiçbir dosyayı SİLMEZ; yalnızca taşır.
- Videolar/<KOD> içinde yalnızca sonuç dosyaları kalır; fazlası Arsiv/<KOD>'a taşınır.
- Üretim bitince silme adayları listelenir; kullanıcı cevap vermezse Silinecekler/<KOD>'a
  (klasör yapısı korunarak) taşınır. Kullanıcı kendisi siler.
"""
from __future__ import annotations

import fnmatch
import shutil
from datetime import datetime
from pathlib import Path

from . import kanal

SONUC_DOSYALARI = ("01_OKU_BENI.md", "02_ElevenLabs_seslendirme_metni.txt", "03_Gorsel_promptlari.txt",
                   "04_Paketleme_ve_Veo3.md", "05_Montaj_plani.tsv", "06_Odak_noktalari.json",
                   "{kod}_altyazi_{dil}.srt", "flow_indirilen")
# Flow devri sürerken geçici olarak izinli (içe almadan sonra arşive taşınır).
GECICI = ("flow_istek", "flow_cikti")
# Asla silme kapsamına girmez.
KORUNAN = ("*.mp4", "tam_yedek_*", "draft_info_*_oncesi.json", "Skill_eski_*", "eski_muzik_*")


def izinli(kod: str) -> set[str]:
    return {s.format(kod=kod, dil=kanal.hedef_dil()) for s in SONUC_DOSYALARI} | set(GECICI)


def fazlalar(kod: str) -> list[Path]:
    v = kanal.video_klasoru(kod)
    if not v.is_dir():
        return []
    return sorted(p for p in v.iterdir() if p.name not in izinli(kod) and p.name != ".DS_Store")


def _bos_ad(hedef: Path) -> Path:
    if not hedef.exists():
        return hedef
    damga = datetime.now().strftime("%Y%m%d_%H%M%S")
    return hedef.with_name(f"{hedef.stem}_{damga}{hedef.suffix}")


def fazlalari_arsive_tasi(kod: str) -> list[str]:
    tasinan = []
    for p in fazlalar(kod):
        hedef = _bos_ad(kanal.arsiv_klasoru(kod) / p.name)
        hedef.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(hedef))
        tasinan.append(p.name)
    return tasinan


def korunuyor_mu(yol: Path) -> bool:
    if kanal.kok() / "Videolar" in yol.parents or yol == kanal.kok() / "Videolar":
        return True
    return any(fnmatch.fnmatch(yol.name, k) for k in KORUNAN)


def silme_adaylari(kod: str) -> list[Path]:
    """Arsiv/<KOD> içindeki büyük ara dosyalar: Flow zip'leri, kontak/odak sayfaları, ara yedekler."""
    a = kanal.arsiv_klasoru(kod)
    if not a.is_dir():
        return []
    desen = ("*.zip", "kontak*.jpg", "odak", "flow_v*", "draft_info_yayin_oncesi.json")
    adaylar = [p for p in a.iterdir() if any(fnmatch.fnmatch(p.name, d) for d in desen)]
    return sorted((p for p in adaylar if not korunuyor_mu(p)), key=lambda p: p.name)


def silineceklere_tasi(kod: str, yollar: list[Path]) -> list[str]:
    hedef_kok = kanal.kok() / "Silinecekler" / kod
    tasinan = []
    for p in yollar:
        p = Path(p)
        if korunuyor_mu(p) or kanal.kok() not in p.parents:
            continue
        hedef = _bos_ad(hedef_kok / p.relative_to(kanal.arsiv_klasoru(kod) if kanal.arsiv_klasoru(kod) in p.parents
                                                  else kanal.kok()))
        hedef.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(hedef))
        tasinan.append(hedef.relative_to(kanal.kok()).as_posix())
    return tasinan
```

### `app/kanal_studyosu/flow.py`

```python
"""Flow adımı: klasör tabanlı devir (uygulama ↔ Claude masaüstü ajanı). Playwright yok.

Adaptör arayüzü: istek_hazirla → durum (bekle) → dogrula → ice_al.
- Uygulama Flow'a hiç bağlanmaz; görselleri kullanıcının Claude masaüstü sohbetindeki ajan üretir.
- Ajan görselleri/zip'i flow_cikti/'ye koyar ve BITTI.json yazar; sorun olursa SORUN.md.
- Yarı elle yedek yol: partiler ekranda "Kopyala" ile verilir, kullanıcı zip'i flow_cikti/'ye bırakır.
Hiçbir dosya silinmez; işlenen sinyal dosyaları ve klasörler arşive taşınır.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

from . import ayarlar as A
from . import kanal
from . import kontroller as K



def boyut() -> tuple[int, int]:
    """Flow'un indirdiği görsel ölçüsü: 16:9 → 1376x768, 9:16 → 768x1376."""
    return (768, 1376) if kanal.ayar()["gorsel"].get("oran") == "9:16" else (1376, 768)


PARTI = 5
AD = re.compile(r"^sahne(\d{4})(?:[_\-. ].*)?\.(jpe?g|png)$", re.I)

def ajan_talimati_flow() -> str:
    g = kanal.ayar()["gorsel"]
    oran, model = g.get("oran", "16:9"), g.get("flow_model", "Nano Banana 2")
    yon = "9:16 portrait aspect ratio (tall vertical, e.g. 1080x1920), never 1:1 square and never landscape" \
        if oran == "9:16" else "16:9 landscape aspect ratio (wide horizontal, e.g. 1920x1080), never 1:1 square and never portrait"
    kar = f", even when the {g['karakter']} character reference image is attached" if g.get("karakter") else ""
    return (f"Always generate every image in {yon}{kar}: always set the aspect ratio parameter to {oran} explicitly. "
            f"Generate exactly one image (x1) per prompt, using the {model} model. " + _AJAN_DEVAM)


_AJAN_DEVAM = (
    "Work "
    "through the whole prompt list in order, 5 at a time, without stopping to ask for confirmation between batches. "
    "If a generation fails, retry that same prompt at most 2 times, then skip it and continue; never send the same "
    "prompt more than 3 times in total. Name each image right after it is created: first prompt = sahne0001, second = "
    "sahne0002, and so on. Do not generate a prompt again if it already has a successful image. Keep your chat replies "
    "very short.")


def istek_klasoru(kod: str) -> Path:
    return kanal.video_klasoru(kod) / "flow_istek"


def cikti_klasoru(kod: str) -> Path:
    return kanal.video_klasoru(kod) / "flow_cikti"


def promptlar(kod: str) -> list[str]:
    return K.bloklar((kanal.video_klasoru(kod) / "03_Gorsel_promptlari.txt").read_text(encoding="utf-8"))


def talimat_metni(kod: str, proje_adi: str, klasor: Path, sadece: list[int] | None) -> str:
    kapsam = (f"Yalnız şu sahneleri üret: {', '.join(f'sahne{n:04d}' for n in sadece)} (eksikler.json). "
              "Aynı Flow projesinde devam et; var olan görsellere dokunma.") if sadece else \
        f"Flow'da yeni proje aç: adı `{proje_adi}`."
    g = kanal.ayar()["gorsel"]
    kar = g.get("karakter", "")
    kanal_adi, model, oran = kanal.ayar()["ad"], g.get("flow_model", "Nano Banana 2"), g.get("oran", "16:9")
    karakter_adimi = f"{kar} karakterini ekle (Flow'daki karakter), " if kar else ""
    karakter_kontrol = f" ve {kar} karakterinin tutarlı olduğunu" if kar else ""
    yon = "dikey" if oran == "9:16" else "yatay"
    return f"""# Flow üretimi · {kod}

Bu klasörü Kanal Stüdyosu hazırladı ({kanal_adi}). Görevin yalnızca Flow'da görsel üretmek. Başka hiçbir iş yapma; proje dosyalarını okuma.

**Klasör:** `{klasor}`

1. `istek.json` ve `promptlar.txt` dosyalarını oku. Promptlar sırayla, her biri tek paragraf; 1. prompt = sahne0001.
2. {kapsam}
3. {karakter_adimi}ayarları yap: "Hiçbir zaman", x1, model tam "{model}", {oran}. Ajan talimatı `istek.json` → `flow_ajan_talimati`.
4. Promptları **beşerli partiler** hâlinde gönder (`istek.json` → `partiler`). Asla hepsini tek mesajda verme. Her partiden sonra bitmesini bekle; ilk iki partiden sonra görsellerin {yon} olduğunu{karakter_kontrol} kontrol et. "Tekrar dene"ye basma.
5. Bitince projeyi indir ve zip'i (ya da `sahneNNNN_*.jpg` görselleri) şu klasöre koy: `{klasor.parent / 'flow_cikti'}`
6. Son olarak aynı klasöre `BITTI.json` yaz: `{{"kod": "{kod}", "uretilen": <sayı>, "notlar": "<varsa kısa not>"}}`
7. Bir sahne Flow politikasına takılır ya da çıkmazsa promptu kendin değiştirme. Sahne numarasını ve Flow'un mesajını `flow_cikti/SORUN.md` dosyasına yaz, sonra `BITTI.json` yaz.

Şifre girme. Oturum düşerse dur ve kullanıcıdan giriş iste.
"""


def istek_hazirla(kod: str, kisa_konu: str, sadece: list[int] | None = None) -> dict:
    P = promptlar(kod)
    numaralar = sadece or list(range(1, len(P) + 1))
    partiler = [{"sahneler": [f"sahne{n:04d}" for n in numaralar[i:i + PARTI]],
                 "promptlar": [P[n - 1] for n in numaralar[i:i + PARTI]]}
                for i in range(0, len(numaralar), PARTI)]
    proje = f"{kod} {kisa_konu}".strip()
    k = istek_klasoru(kod)
    istek = {"kod": kod, "proje_adi": proje, "toplam_sahne": len(P), "uretilecek": len(numaralar),
             "sadece_eksikler": bool(sadece), "partiler": partiler,
             "kanal": kanal.ayar()["ad"], "karakter": kanal.ayar()["gorsel"].get("karakter", ""),
             "ayarlar": {"oran": kanal.ayar()["gorsel"].get("oran", "16:9"), "adet": "x1",
                         "model": kanal.ayar()["gorsel"].get("flow_model", "Nano Banana 2"), "onay": "Hiçbir zaman"},
             "flow_ajan_talimati": ajan_talimati_flow(),
             "beklenen_cikti": {"bicim": "zip ya da jpg", "boyut": "{}x{}".format(*boyut()), "ad": "sahneNNNN_*.jpg"},
             "hazirlanma": datetime.now().isoformat(timespec="seconds")}
    A.json_yaz(k / "istek.json", istek)
    A.atomik_yaz(k / "promptlar.txt", "\n\n".join(P) + "\n")
    A.atomik_yaz(k / "TALIMAT_AJAN.md", talimat_metni(kod, proje, k, sadece))
    if sadece:
        A.json_yaz(k / "eksikler.json", {"sahneler": [f"sahne{n:04d}" for n in sadece]})
    cikti_klasoru(kod).mkdir(parents=True, exist_ok=True)
    return istek


def ajan_komutu(kod: str) -> str:
    return f"`kanal-studyosu-flow` becerisini kullan. Klasör: {istek_klasoru(kod)}"


def _gorseller(klasor: Path) -> dict[int, list[Path]]:
    by: dict[int, list[Path]] = {}
    for f in klasor.rglob("*"):
        m = AD.match(f.name)
        if f.is_file() and m and "__MACOSX" not in f.parts:
            by.setdefault(int(m.group(1)), []).append(f)
    return by


def durum(kod: str) -> dict:
    c = cikti_klasoru(kod)
    if not c.is_dir():
        return {"var": False}
    sorun = c / "SORUN.md"
    return {"var": True, "gorsel": len(_gorseller(c)), "zip": len(list(c.glob("*.zip"))),
            "bitti": (c / "BITTI.json").exists(),
            "sorun": sorun.read_text(encoding="utf-8")[:4000] if sorun.exists() else ""}


def _boyut(f: Path) -> tuple[int, int] | None:
    from .onkontrol import _program
    q = subprocess.run([_program("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0:s=x", str(f)], capture_output=True, text=True)
    m = re.match(r"(\d+)x(\d+)", q.stdout.strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def _ziplari_ac(kod: str) -> None:
    for z in cikti_klasoru(kod).glob("*.zip"):
        hedef = cikti_klasoru(kod) / f"_acilan_{z.stem}"
        if hedef.exists():
            continue
        try:
            with zipfile.ZipFile(z) as zf:
                if zf.testzip() is not None:
                    raise zipfile.BadZipFile("bozuk dosya")
                zf.extractall(hedef)
        except zipfile.BadZipFile:
            raise ValueError(f"{z.name} açılamadı (indirme yarım kalmış olabilir).")


def dogrula(kod: str) -> dict:
    """→ {'tamam': bool, 'eksik': [n], 'boyut': [..], 'cift': [..], 'secilen': {n: yol}}"""
    _ziplari_ac(kod)
    toplam = len(promptlar(kod))
    by = _gorseller(cikti_klasoru(kod))
    # Daha önce içe alınmış görseller (yalnız eksikler turu) de sayılır.
    onceki = _gorseller(kanal.video_klasoru(kod) / "flow_indirilen") if \
        (kanal.video_klasoru(kod) / "flow_indirilen").is_dir() else {}
    secilen, hatali, cift, beklenen = {}, [], [], boyut()
    for n in range(1, toplam + 1):
        adaylar = by.get(n) or onceki.get(n) or []
        if not adaylar:
            continue
        if len(adaylar) > 1:
            cift.append(f"sahne{n:04d}: {len(adaylar)} görsel var, en yenisi alındı")
        f = max(adaylar, key=lambda p: p.stat().st_mtime)
        b = _boyut(f)
        if b != beklenen:
            hatali.append(f"sahne{n:04d}: {b[0]}x{b[1]}" if b else f"sahne{n:04d}: okunamadı")
            continue
        secilen[n] = f
    eksik = [n for n in range(1, toplam + 1) if n not in secilen]
    return {"tamam": not eksik, "toplam": toplam, "eksik": eksik, "boyut": hatali, "cift": cift,
            "secilen": {n: str(p) for n, p in secilen.items()}}


def ice_al(kod: str, secilen: dict) -> Path:
    """Görselleri Videolar/<kod>/flow_indirilen/'e kopyalar; istek/çıktı klasörlerini arşive taşır."""
    hedef = kanal.video_klasoru(kod) / "flow_indirilen"
    hedef.mkdir(exist_ok=True)
    for n, yol in secilen.items():
        yol = Path(yol)
        if hedef in yol.parents:
            continue
        shutil.copy2(yol, hedef / yol.name)
    sinyal_arsivle(kod, tumu=True)
    return hedef


def sinyal_arsivle(kod: str, tumu: bool = False) -> None:
    """BITTI.json/SORUN.md (ya da tumu=True ise flow_istek ve flow_cikti) arşive taşınır; silinmez."""
    damga = datetime.now().strftime("%Y%m%d_%H%M%S")
    a = kanal.arsiv_klasoru(kod) / f"flow_devri_{damga}"
    if tumu:
        for k in (istek_klasoru(kod), cikti_klasoru(kod)):
            if k.exists():
                a.mkdir(parents=True, exist_ok=True)
                shutil.move(str(k), str(a / k.name))
        return
    for ad in ("BITTI.json", "SORUN.md"):
        f = cikti_klasoru(kod) / ad
        if f.exists():
            a.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(a / ad))


def secilenler_klasorden(kod: str) -> dict[int, Path]:
    """İçe alınmış görseller: sahne no → dosya (Studio'ya verilecek)."""
    by = _gorseller(kanal.video_klasoru(kod) / "flow_indirilen")
    return {n: max(v, key=lambda p: p.stat().st_mtime) for n, v in by.items()}
```

### `app/kanal_studyosu/kanal.py`

```python
"""Seçili kanalın klasörü ve ayarları (üretim modüllerinin kullandığı katman).

İlk (tek kanallı) sürümdeki kanal.py ile aynı arayüz; yollar sabit bir kanal klasörü yerine seçili kanalın klasöründen
(Kanallar/<kisaltma>/) gelir. Üretim sürerken kanal değiştirilemediği için "seçili kanal" üretimin kanalıdır.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from . import ayarlar as A
from . import kanallar

YONETICI, ANAYASA, DEFTER, AKTIF = kanallar.PROJE_DOSYALARI
PROJE_DOSYALARI = kanallar.PROJE_DOSYALARI
BECERILER = tuple(a for a, _ in kanallar.ASAMALAR)


def secili() -> str:
    k = kanallar.aktif()
    if not k:
        raise ValueError("Seçili kanal yok. Önce bir kanal ekle.")
    return k


def ayar() -> dict:
    return kanallar.oku(secili())


def kok() -> Path:
    return kanallar.klasor(secili())


def proje_klasoru() -> Path:
    return kok() / "Proje_dosyalari"


def rit(ad: str) -> str:
    """Proje dosyası (00_Yonetici.md … 03_Aktif_Video.md)."""
    return (proje_klasoru() / ad).read_text(encoding="utf-8")


def beceri(ad: str) -> str:
    return (kok() / "Beceriler" / ad / "SKILL.md").read_text(encoding="utf-8")


def onek() -> str:
    return ayar()["kod_oneki"]


def hedef_dil() -> str:
    return ayar()["dil"]["hedef"]


def dil_adi(kod: str | None = None) -> str:
    kod = kod or hedef_dil()
    return kanallar.DILLER.get(kod, kod)


def ceviri_var() -> bool:
    """Hedef dil Türkçe ise 4. aşama (hedef dilde yeniden yazım) atlanır."""
    return hedef_dil() != "tr"


def kod_deseni() -> re.Pattern:
    return re.compile(rf"^{re.escape(onek())}-(\d{{2,3}})$")


class _Kod:
    """Eski KOD sabitinin yerine: kanal.KOD.match(...) seçili kanalın önekine göre çalışır."""

    def match(self, s: str):
        return kod_deseni().match(s or "")


KOD = _Kod()


def kod_yap(n: int) -> str:
    return f"{onek()}-{n:0{int(ayar().get('kod_hane', 2))}d}"


def video_klasoru(kod: str) -> Path:
    return kok() / "Videolar" / kod


def arsiv_klasoru(kod: str) -> Path:
    return kok() / "Arsiv" / kod


def uygulama_klasoru(kod: str) -> Path:
    """Uygulamanın durum ve konuşma kayıtları (Videolar temiz kalsın diye arşivde)."""
    return arsiv_klasoru(kod) / "_uygulama"


def uretim_klasoru() -> Path:
    """Ses, görsel ve sahne videolarının üretildiği yer (ilk sürümdeki Creator Projects'in karşılığı)."""
    return kok() / "Uretim"


def altyazi_adi(kod: str) -> str:
    return f"{kod}_altyazi_{hedef_dil()}.srt"


def mevcut_kodlar() -> list[str]:
    v = kok() / "Videolar"
    if not v.is_dir():
        return []
    d = kod_deseni()
    return sorted((p.name for p in v.iterdir() if p.is_dir() and d.match(p.name)), key=lambda k: int(d.match(k).group(1)))


def defter_tablosu(defter: str | None = None) -> list[dict]:
    """Kanal Defteri A tablosundaki video satırları."""
    if defter is None:
        try:
            defter = rit(DEFTER)
        except FileNotFoundError:
            return []
    d = kod_deseni()
    satirlar, basliklar = [], None
    for s in defter.splitlines():
        if not s.startswith("|"):
            if basliklar and satirlar:
                break
            continue
        hucre = [h.strip() for h in s.strip().strip("|").split("|")]
        if hucre and hucre[0] == "Kod":
            basliklar = hucre
            continue
        if basliklar and hucre and d.match(hucre[0]):
            satirlar.append(dict(zip(basliklar, hucre)))
    return satirlar


def siradaki_kod() -> str:
    d = kod_deseni()
    numaralar = [int(d.match(k).group(1)) for k in mevcut_kodlar()]
    numaralar += [int(d.match(s["Kod"]).group(1)) for s in defter_tablosu()]
    numaralar += [int(d.match(k).group(1)) for k in (A.json_oku(uretim_listesi_yolu(), {}) or {}).get("videolar", {})
                  if d.match(k)]
    return kod_yap((max(numaralar) if numaralar else 0) + 1)


def uretim_listesi_yolu() -> Path:
    return kok() / "uretim_listesi.json"


def uretim_listesi() -> dict:
    """İlk açılışta Videolar + Kanal Defteri'nden oluşturulur; sonra yalnızca güncellenir."""
    yol = uretim_listesi_yolu()
    liste = A.json_oku(yol, None)
    if liste is None:
        liste = {"olusturma": datetime.now().isoformat(timespec="seconds"), "videolar": {}}
    defter = {s["Kod"]: s for s in defter_tablosu()}
    d = kod_deseni()
    degisti = False
    for kod in sorted(set(mevcut_kodlar()) | set(defter), key=lambda k: int(d.match(k).group(1))):
        if kod in liste["videolar"]:
            continue
        s = defter.get(kod, {})
        m = re.match(r"\s*([\d:]+)\s*/\s*(\d+)", s.get("Süre / sahne", ""))
        liste["videolar"][kod] = {"kod": kod, "baslik": s.get("Nihai başlık", ""), "durum": s.get("Durum", ""),
                                  "sure": m.group(1) if m else "", "sahne": int(m.group(2)) if m else None,
                                  "klasor": str(video_klasoru(kod)), "salt_okunur": True}
        degisti = True
    if degisti:
        A.json_yaz(yol, liste)
    return liste


def liste_guncelle(kod: str, **alanlar) -> None:
    liste = uretim_listesi()
    v = liste["videolar"].setdefault(kod, {"kod": kod, "klasor": str(video_klasoru(kod)), "salt_okunur": False})
    v.update(alanlar)
    A.json_yaz(uretim_listesi_yolu(), liste)


def rit03_yenile(kod: str, yeni_metin: str) -> Path:
    """03_Aktif_Video.md'yi yeniler; eski hâli silinmez, video arşivine kopyalanır."""
    yol = proje_klasoru() / AKTIF
    if yol.exists():
        eski = yol.read_text(encoding="utf-8")
        if eski != yeni_metin:
            A.atomik_yaz(arsiv_klasoru(kod) / f"03_Aktif_Video_oncesi_{datetime.now():%Y%m%d_%H%M%S}.md", eski)
    A.atomik_yaz(yol, yeni_metin)
    return yol


# --- modele giden KANAL AYARLARI bloğu --------------------------------------------

def ayarlar_blogu() -> str:
    k = ayar()
    u, e, g, m = k["uzunluk"], k["etiketler"], k["gorsel"], k["montaj"]
    sen = e["senaryo"]
    sinir = ", ".join(f"[{t}] en fazla {n}" for t, n in e.get("ses_sinir", {}).items()) or "yok"
    maskot = (f"{len(m['maskot']['sira'])} sahnede sırasıyla {', '.join(m['maskot']['sira'])} "
              f"(dosyalar: {', '.join(m['maskot']['dosyalar'])})") if m["maskot"]["sira"] else "maskot yok (bütün satırlar '-')"
    satirlar = [
        "# KANAL AYARLARI (uygulamadan; becerideki sayılarla çelişirse bunlar geçerlidir)",
        f"- Kanal: {k['ad']} · video kodu {k['kod_oneki']}-0X",
        f"- Diller: çalışma metinleri Türkçe; video dili {dil_adi()} ({k['dil']['hedef']})"
        + ("" if ceviri_var() else " — hedef dil Türkçe olduğu için 4. aşama yoktur, Türkçe senaryo finaldir"),
        f"- Hedef süre ~{u['hedef_dk']} dk · Türkçe senaryo {u['calisma_kelime'][0]}–{u['calisma_kelime'][1]} kelime · "
        f"{dil_adi()} senaryo {u['hedef_kelime'][0]}–{u['hedef_kelime'][1]} kelime (etiketler hariç)",
        f"- Konu kartı en fazla {u['kart_karakter']} karakter · hook puanı eşiği {u['hook_esigi']}/10",
        f"- Senaryo etiketleri: karakter sahnesi [{sen['karakter']}] · metafor [{sen['metafor']}] · şema [{sen['sema']}] · "
        f"ilk 30 sn [{sen['ilk30']}]",
        f"- Seslendirme tag'leri (yalnız bunlar): {' '.join('[' + t + ']' for t in e['ses'])} · sınırlar: {sinir} · "
        f"tag'li paragraf oranı en fazla %{e['tag_orani']}",
        f"- Flow karakteri: {g['karakter'] or 'yok (karakter etiketi kullanılmaz)'} · görsel oranı {g['oran']}",
        f"- Flow yasaklı kelimeler (hiçbir biçimde): {', '.join(g['yasakli']) or 'yok'}",
        f"- İzinli teknik olumsuzlamalar: {', '.join('no ' + x for x in g['izinli_olumsuz'])}",
        f"- Maskot: {maskot}",
    ]
    if g.get("kurallar"):
        satirlar.append(f"- Görsel kurallar: {g['kurallar']}")
    return "\n".join(satirlar)
```

### `app/kanal_studyosu/kanal_sablonu.py`

````python
"""Yeni kanal dosyası: kanal bilgileri + kanal anayasası tek metinde.

Kullanıcı şablonu (Yeni_Kanal_Sablonu.md) herhangi bir yapay zekaya verip kanalına göre doldurtur, sonra uygulamaya
yapıştırır. Okuma kodla yapılır (yapay zeka kullanılmaz). A bölümü `Alan: değer` satırlarıdır ve kanal ayarlarına
çevrilir; B bölümü olduğu gibi kanalın 01_Anayasa.md dosyası olur. Eksik ya da hatalı alanlar formda işaretlenir.
Ses, maskot, müzik ve onaylar dosyada yoktur, uygulamada seçilir.
"""
from __future__ import annotations

import re

from . import ayarlar as A
from . import kanallar
from . import yollar

DOSYA_ADI = "Yeni_Kanal_Sablonu.md"
A_BASLIK = "=== A · KANAL BİLGİLERİ ==="
B_BASLIK = "=== B · KANAL ANAYASASI ==="
_A_DESEN = re.compile(r"\bA\s*[·.:\-–]\s*KANAL\s+B[İI]LG[İI]LER[İI]", re.I)
_B_DESEN = re.compile(r"\bB\s*[·.:\-–]\s*KANAL\s+ANAYASASI", re.I)

# (etiket, yol, tür, açıklama, zorunlu)
ALANLAR = (
    ("Kanal adı", "ad", "metin", "YouTube'daki kanal adı.", True),
    ("Video dili", "dil.hedef", "dil", "Videoların seslendirileceği dil: " + ", ".join(kanallar.DILLER.values()) + ".",
     True),
    ("Video süresi (dakika)", "uzunluk.hedef_dk", "sayi", "Bir videonun hedef uzunluğu, ör. 12. Kelime sayısını "
     "uygulama bundan hesaplar.", True),
    ("Görsel oranı", "gorsel.oran", "oran", "16:9 (yatay) ya da 9:16 (dikey). Boşsa 16:9.", False),
    ("Flow karakter etiketi", "gorsel.karakter", "karakter", "Sahnelerde tekrar eden bir karakter varsa @ ile adı "
     "(ör. @Mira); yoksa boş bırak.", False),
    ("Karakter sahnesi etiketi", "etiketler.senaryo.karakter", "etiket", "Senaryoda karakterli paragrafların başına "
     "yazılan kısa ad, büyük harf ve boşluksuz (ör. MIRA). Boşsa KARAKTER.", False),
    ("Karakterin yüz ifadesi notu", "gorsel.ifade_notu", "metin", "İsteğe bağlı: karakterin yüz ifadeleri nasıl "
     "olmalı.", False),
    ("Görsel kurallar", "gorsel.kurallar", "metin", "Kanalın görsellerinde neye dikkat edilir (ör. yazı ve logo yok, "
     "çocuk figürü yok). Boşsa genel kurallar kullanılır.", False),
    ("Ek yasaklı görsel kelimeler", "gorsel.yasakli", "liste_ek", "İngilizce, virgülle. Görsel promptlarında asla "
     "geçmeyecek kelimeler; genel güvenlik listesine eklenir.", False),
    ("Hassas kelimeler", "hassas_kelimeler", "liste", "Video dilinde, virgülle. Başlık, açıklama ve ilk 30 saniyede "
     "kullanılmayacak kelimeler (kök yazılabilir).", False),
    ("Seslendirme tonu tag'leri", "etiketler.ses", "liste", "İngilizce, küçük harf, virgülle (ör. calm, softly, warm). "
     "Boşsa varsayılan liste.", False),
    ("Kapanış imzası", "imza", "metin", "Her videonun sonunda aynen tekrar eden tek satır, video dilinde. Yoksa boş.",
     False),
    ("Altyazı yazı tipi", "montaj.altyazi.yazi_tipi", "metin", "Bilgisayarda kurulu bir yazı tipi (ör. Nunito).", False),
    ("Altyazı yazı rengi", "montaj.altyazi.yazi", "renk", "#RRGGBB biçiminde.", False),
    ("Altyazı kutu rengi", "montaj.altyazi.kutu", "renk", "#RRGGBB biçiminde.", False),
    ("Kısaltma", "kisaltma", "metin", "İsteğe bağlı: kanal klasörünün adı (küçük harf, rakam, tire). Boşsa addan "
     "önerilir.", False),
    ("Video kodu öneki", "kod_oneki", "metin", "İsteğe bağlı: videolar ÖNEK-01, ÖNEK-02 diye adlanır (ör. BK). Boşsa "
     "addan önerilir.", False),
)

_BOS = {"", "-", "—", "yok", "boş", "bos", "none", "n/a", "na", "null", "isteğe bağlı", "istege bagli"}
_DIL_ADLARI = {
    "tr": ("türkçe", "turkce", "turkish", "türk"), "it": ("italyanca", "italian", "italiano"),
    "en": ("ingilizce", "english"), "de": ("almanca", "german", "deutsch"),
    "es": ("ispanyolca", "spanish", "español", "espanol"), "fr": ("fransızca", "fransizca", "french",
                                                                              "français", "francais"),
    "pt": ("portekizce", "portuguese", "português", "portugues"), "nl": ("felemenkçe", "hollandaca", "dutch",
                                                                        "nederlands"),
    "pl": ("lehçe", "lehce", "polish", "polski"), "ru": ("rusça", "rusca", "russian", "русский"),
    "ar": ("arapça", "arapca", "arabic", "العربية"), "ja": ("japonca", "japanese", "日本語"),
}


# --- şablon ---------------------------------------------------------------

def _anayasa_govdesi() -> str:
    metin = (yollar.SABLONLAR / "kanal" / "Proje_dosyalari" / "01_Anayasa.md").read_text(encoding="utf-8")
    i = metin.find("\n## 1.")
    return metin[i + 1:] if i >= 0 else metin


def sablon_metni() -> str:
    satirlar = [
        "# KANAL STÜDYOSU · YENİ KANAL DOSYASI", "",
        "Bu dosyayla yeni bir kanal tek seferde eklenir.", "",
        "1. Bu dosyanın tamamını bir yapay zekaya (Claude, ChatGPT…) ver.",
        "2. Altına kanalını birkaç cümleyle anlat: konusu, kimin için, hangi dilde, videolar kaç dakika, anlatıcı nasıl,",
        "   görseller nasıl (karakter var mı, renkler).",
        "3. Yapay zekanın doldurduğu dosyayı Kanal Stüdyosu'nda Kanal ekle › Dosyayla ekle'ye yapıştır ya da dosyayı seç.",
        "",
        "Ses (ElevenLabs), maskot, müzik ve onaylar uygulamada seçilir; bu dosyada yoktur. Eksik kalan yerleri uygulama",
        "gösterir. Anayasa sonradan Kanal dosyaları › 01_Anayasa.md'den de düzenlenebilir.", "",
        "> YAPAY ZEKAYA TALİMAT: Aşağıdaki A ve B bölümlerini kullanıcının anlattığı kanala göre doldur ve dosyanın",
        "> tamamını geri ver. A bölümünde satır adlarını ve === başlıklarını değiştirme; her satırda iki noktadan sonrasını",
        "> yaz, bilmediğini boş bırak. B bölümünde ⟦DOLDUR: …⟧ işaretlerinin yerine kanala uygun metni yaz ve işareti sil;",
        "> diğer maddeleri kanala uymuyorsa düzelt ama başlıkları silme. {{KANAL_ADI}} gibi çift süslü parantezli yerlere",
        "> dokunma, onları uygulama doldurur. Bilgi eksikse önce kullanıcıya sor.", "",
        A_BASLIK, "",
    ]
    for etiket, _yol, _tur, aciklama, zorunlu in ALANLAR:
        satirlar += [f"> {aciklama}" + (" (zorunlu)" if zorunlu else ""), f"{etiket}: ", ""]
    satirlar += [B_BASLIK, "", _anayasa_govdesi().rstrip(), ""]
    return "\n".join(satirlar)


def sablon_dosyasi_yaz() -> None:
    """Kurulum klasörüne şablonu koyar (yoksa). Var olan dosyaya dokunulmaz (kullanıcı içine yazmış olabilir)."""
    yol = yollar.kok() / DOSYA_ADI
    if not yol.exists():
        A.atomik_yaz(yol, sablon_metni())


# --- okuma ----------------------------------------------------------------

def _normal(s: str) -> str:
    """Karşılaştırma için: küçük harf, ı/i ve İ/I aynı sayılır (BÜYÜK HARFLE yazılmış satır adı da tanınır)."""
    s = s.replace("İ", "i").lower().replace("ı", "i").replace("\u0307", "").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()


_ETIKETLER = {_normal(e): (e, y, t, z) for e, y, t, _, z in ALANLAR}


def _bolumler(metin: str) -> tuple[str, str]:
    satirlar = [x for x in metin.replace("\r\n", "\n").split("\n") if not re.fullmatch(r"\s*```\w*\s*", x)]
    a = next((i for i, x in enumerate(satirlar) if _A_DESEN.search(x)), None)
    b = next((i for i, x in enumerate(satirlar) if _B_DESEN.search(x)), None)
    a_bolum = satirlar[(a + 1 if a is not None else 0):(b if b is not None else len(satirlar))]
    b_bolum = satirlar[b + 1:] if b is not None else []
    return "\n".join(a_bolum), "\n".join(b_bolum).strip()


def _satirlar(a_bolum: str) -> dict[str, str]:
    """`Alan: değer` satırları; bir alanın altındaki etiketsiz satırlar o alana eklenir (çok satırlı değer)."""
    degerler: dict[str, list[str]] = {}
    simdiki = None
    for ham in a_bolum.split("\n"):
        x = ham.strip()
        if x.startswith(">") or x.startswith("#"):
            simdiki = None if x.startswith("#") else simdiki
            continue
        temiz = re.sub(r"^[-*•]\s+", "", x).replace("**", "").replace("__", "")
        m = re.match(r"^([^:]{2,60}?)\s*:\s*(.*)$", temiz)
        if m and _normal(m.group(1)) in _ETIKETLER:
            simdiki = _normal(m.group(1))
            degerler[simdiki] = [m.group(2).strip()]
        elif simdiki and x:
            degerler[simdiki].append(temiz)
    return {k: "\n".join(v).strip() for k, v in degerler.items()}


def _bos_mu(v: str) -> bool:
    v = v.strip()
    return _normal(v) in _BOS or v.startswith("⟦") or (v.startswith("(") and v.endswith(")"))


def _dil(v: str) -> str | None:
    n = _normal(v)
    m = re.search(r"\(([a-z]{2})\)", n)
    if m and m.group(1) in kanallar.DILLER:
        return m.group(1)
    if n in kanallar.DILLER:
        return n
    for kod, adlar in _DIL_ADLARI.items():
        if any(re.search(rf"(^|[^\w]){re.escape(a)}($|[^\w])", n) for a in adlar):
            return kod
    return None


def _cevir(tur: str, v: str):
    """→ (değer, hata). Hata varsa değer None."""
    if tur == "metin":
        return v, None
    if tur == "dil":
        d = _dil(v)
        return (d, None) if d else (None, "dil tanınmadı")
    if tur == "sayi":
        m = re.search(r"\d+(?:[.,]\d+)?", v)
        if not m:
            return None, "sayı yok"
        x = float(m.group().replace(",", "."))
        return (int(x) if x == int(x) else x), None
    if tur == "oran":
        return ("9:16" if re.search(r"9\s*:\s*16|dikey|vertical|portrait", v, re.I) else "16:9"), None
    if tur == "karakter":
        if not v.strip().startswith("@") and re.search(r"(^|\W)(yok|none|no|karaktersiz)(\W|$)", _normal(v)):
            return "", None
        ad = v.split()[0].strip(".,;") if v.split() else ""
        return ("@" + ad.lstrip("@")) if ad else "", None
    if tur == "etiket":
        return v.split()[0].strip("[]").strip(".,;").upper(), None
    if tur in ("liste", "liste_ek"):
        return [x.strip().strip("\"'") for x in re.split(r"[,\n;]", v) if x.strip().strip("\"'")], None
    if tur == "renk":
        m = re.search(r"#[0-9A-Fa-f]{6}\b", v)
        return (m.group().upper(), None) if m else (None, "#RRGGBB biçiminde değil")
    return v, None


def _oner_kisaltma(ad: str, kullanilan: set[str]) -> str:
    tr = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiucgiosu")
    taban = re.sub(r"[^a-z0-9]+", "-", ad.translate(tr).lower()).strip("-")[:28] or "kanal"
    if len(taban) < 2:
        taban = (taban + "-kanal")[:28]
    aday, n = taban, 2
    while aday in kullanilan:
        aday, n = f"{taban}-{n}", n + 1
    return aday


def _oner_onek(ad: str, kullanilan: set[str]) -> str:
    tr = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiuCGIOSU")
    kelimeler = re.findall(r"[A-Za-z0-9]+", ad.translate(tr))
    taban = ("".join(k[0] for k in kelimeler) if len(kelimeler) > 1 else (kelimeler[0][:3] if kelimeler else "KN")).upper()
    taban = re.sub(r"^[0-9]+", "", taban)[:8] or "KN"
    aday, n = taban, 2
    while aday in kullanilan:
        aday, n = f"{taban}{n}", n + 1
    return aday


def oku(metin: str) -> dict:
    """Doldurulmuş dosyayı okur → {kanal, anayasa, eksik: [{yol, etiket, neden}], hatalar, uyarilar, okunan, doldur}.
    kanal: varsayılanlarla birleşmiş, kaydedilmeye hazır taslak (kısaltma ve önek boşsa addan önerilir)."""
    if not (metin or "").strip():
        raise ValueError("Metin boş. Doldurulmuş kanal dosyasını yapıştır.")
    a_bolum, b_bolum = _bolumler(metin)
    satir = _satirlar(a_bolum)
    if not satir:
        raise ValueError("Dosyada kanal bilgisi satırı bulunamadı. 'Kanal adı: …' gibi satırlar olmalı "
                         "(Şablonu kopyala ile yeni şablon alabilirsin).")
    k = kanallar.varsayilan()
    k["uzunluk"]["kelime_otomatik"] = True
    eksik, okunan = [], 0
    for anahtar, (etiket, yol, tur, zorunlu) in _ETIKETLER.items():
        v = satir.get(anahtar, "")
        if _bos_mu(v):
            if zorunlu:
                eksik.append({"yol": yol, "etiket": etiket, "neden": "boş"})
            continue
        deger, hata = _cevir(tur, v)
        if hata:
            eksik.append({"yol": yol, "etiket": etiket, "neden": f"{hata}: {v[:60]}"})
            continue
        if tur == "liste_ek":
            deger = list(dict.fromkeys(_al(k, yol) + [x.lower() for x in deger]))
        elif tur == "liste" and not deger:
            continue
        elif yol == "etiketler.ses":
            deger = [x.lower() for x in deger]
        _koy(k, yol, deger)
        okunan += 1
    kullanilan = {c["kisaltma"] for c in kanallar.liste()}
    onekler = {c["kod_oneki"].upper() for c in kanallar.liste()}
    if k.get("ad") and not k.get("kisaltma"):
        k["kisaltma"] = _oner_kisaltma(k["ad"], kullanilan)
    if k.get("ad") and not k.get("kod_oneki"):
        k["kod_oneki"] = _oner_onek(k["ad"], onekler)
    k["kisaltma"], k["kod_oneki"] = str(k["kisaltma"]).strip().lower(), str(k["kod_oneki"]).strip().upper()
    k["ses"]["language_code"] = k["dil"]["hedef"]
    kanallar.kelime_hesapla(k)
    hatalar, uyarilar = kanallar.dogrula(k)
    eksik_yollar = {e["yol"] for e in eksik}
    hatalar = [h for h in hatalar if not any(h.startswith(p) for p in _hata_onekleri(eksik_yollar))]
    uyarilar = [u for u in uyarilar if "voice_id" not in u]  # ses formda seçilir
    if not b_bolum:
        uyarilar.append("Dosyada anayasa bölümü (=== B · KANAL ANAYASASI ===) bulunamadı; anayasa genel şablondan "
                        "başlar.")
    doldur = b_bolum.count(kanallar.DOLDUR)
    if doldur:
        uyarilar.append(f"Anayasada {doldur} doldurulmamış yer (⟦DOLDUR⟧) kaldı; sonra Kanal dosyaları › "
                        "01_Anayasa.md'den tamamlayabilirsin.")
    return {"kanal": k, "anayasa": b_bolum, "eksik": eksik, "hatalar": hatalar, "uyarilar": uyarilar,
            "okunan": okunan, "doldur": doldur}


def _hata_onekleri(yollar_: set[str]) -> tuple[str, ...]:
    """Eksik listesinde zaten gösterilen alanların doğrulama mesajları tekrar edilmez."""
    on = []
    if "ad" in yollar_:
        on += ["Kanal adı", "Kısaltma", "Video kodu öneki"]
    if "uzunluk.hedef_dk" in yollar_:
        on.append("uzunluk.hedef_dk")
    if "dil.hedef" in yollar_:
        on.append("Hedef dil")
    if yollar_ & {"montaj.altyazi.yazi", "montaj.altyazi.kutu"}:
        on.append("Altyazı")
    return tuple(on)


def _al(o: dict, yol: str):
    for p in yol.split("."):
        o = o[p]
    return o


def _koy(o: dict, yol: str, v) -> None:
    p = yol.split(".")
    for x in p[:-1]:
        o = o.setdefault(x, {})
    o[p[-1]] = v
````

### `app/kanal_studyosu/kanallar.py`

```python
"""Kanallar: ekleme, doğrulama, ayarlar, silme, seçim, kanal dosyaları ve içe aktarma.

Her kanal Kanallar/<kisaltma>/ klasöründedir; bütün ayarları kanal.json'dadır (varsayılanlar config/kanal_varsayilan.json).
Silme kalıcı değildir: klasör Çöp Kutusu'na taşınır. CapCut taslaklarından yalnız Kanal Stüdyosu'nun o kanal için
oluşturduğu ve iki izle doğrulananlar (taslaklar.json kaydı + taslak içindeki işaret dosyası) Çöp'e gider; Kanal
Stüdyosu dışında oluşmuş taslaklara hiçbir durumda dokunulmaz.
"""
from __future__ import annotations

import copy
import json
import math
import re
import shutil
import statistics
import uuid
from datetime import datetime
from pathlib import Path

from . import ayarlar as A
from . import cop
from . import kayit
from . import yollar

DILLER = {"tr": "Türkçe", "it": "İtalyanca", "en": "İngilizce", "de": "Almanca", "es": "İspanyolca",
          "fr": "Fransızca", "pt": "Portekizce", "nl": "Felemenkçe", "pl": "Lehçe", "ru": "Rusça",
          "ar": "Arapça", "ja": "Japonca"}
ASAMALAR = (("konu", "1 · Konu"), ("arastirma", "2 · Araştırma"), ("senaryo", "3 · Senaryo (Türkçe)"),
            ("ceviri", "4 · Hedef dil"), ("sahne", "5 · Sahne paketi"), ("paketleme", "6 · Paketleme"))
PROJE_DOSYALARI = ("00_Yonetici.md", "01_Anayasa.md", "02_Defter.md", "03_Aktif_Video.md")
ALT_KLASORLER = ("Proje_dosyalari", "Beceriler", "Varliklar/Muzik", "Varliklar/Maskot", "Varliklar/Karakter",
                 "Varliklar/son_ekran", "Videolar", "Arsiv", "Uretim", "Silinecekler", "Defter_arsivi")
DOLDUR = "⟦DOLDUR"
ISARET = ".kanal_studyosu.json"          # Kanal Stüdyosu'nun oluşturduğu CapCut taslağının içindeki iz
ATLA = {"arsiv", "videolar", "silinecekler", "defter_arsivi", ".yedek", "skill_eski"}
MEDYA = {".mp3", ".m4a", ".wav", ".aac", ".mov", ".mp4", ".png", ".jpg", ".jpeg", ".webp"}

KISALTMA = re.compile(r"^[a-z0-9][a-z0-9-]{1,30}$")
KOD_ONEKI = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*$")
RENK = re.compile(r"^#[0-9A-Fa-f]{6}$")

# Ortalama konuşma hızı (kelime/dk, ElevenLabs hızı 1,0). tr ve it gerçek bir kanalın değerlerinden (12 dk → Türkçe
# 1600–1800, İtalyanca 1950–2050); diğerleri başlangıç tahmini. Her videodan sonra gerçek ses süresi ölçülür ve kanalın
# kendi hızı bu ölçümlerin ortancası olur (uzunluk.hiz_olcum).
KONUSMA_HIZI = {"tr": 142, "it": 167, "en": 155, "de": 135, "es": 165, "fr": 160, "pt": 160, "nl": 145, "pl": 130,
                "ru": 130, "ar": 120, "ja": 150}
KELIME_PAYI = 0.05        # hesaplanan kelime sayısının ± payı
HIZ_OLCUM_SAYISI = 5      # dil başına saklanan son ölçüm


# --- yollar ---------------------------------------------------------------

def klasor(kisaltma: str) -> Path:
    if not KISALTMA.match(kisaltma or ""):
        raise ValueError("Geçersiz kanal kısaltması")
    return yollar.kanallar() / kisaltma


def _ayar_yolu(kisaltma: str) -> Path:
    return klasor(kisaltma) / "kanal.json"


def varsayilan() -> dict:
    return json.loads((yollar.CONFIG / "kanal_varsayilan.json").read_text(encoding="utf-8"))


# --- okuma ----------------------------------------------------------------

def oku(kisaltma: str) -> dict:
    yol = _ayar_yolu(kisaltma)
    if not yol.exists():
        raise ValueError(f"Kanal bulunamadı: {kisaltma}")
    ham = A.json_oku(yol, {}) or {}
    k = A.birlestir(varsayilan(), ham)
    if "kelime_otomatik" not in (ham.get("uzunluk") or {}):
        k["uzunluk"]["kelime_otomatik"] = False  # bu özellikten önce açılmış kanal: elle girilen kelime aralıkları kalır
    return kelime_hesapla(k)


# --- kelime aralıkları (süre × konuşma hızı) ----------------------------------

def konusma_hizi(k: dict, dil: str) -> tuple[float, int]:
    """→ (kelime/dk, kaç ölçüme dayandığı). Ölçüm yoksa dilin ortalaması. Ses hızı (speed) ile çarpılır."""
    olcum = [x["hiz"] for x in ((k.get("uzunluk") or {}).get("hiz_olcum") or {}).get(dil, [])
             if isinstance(x, dict) and isinstance(x.get("hiz"), (int, float))]
    hiz = statistics.median(olcum) if olcum else KONUSMA_HIZI.get(dil, 150)
    hizi = (k.get("ses") or {}).get("speed") or 1
    return hiz * (float(hizi) if isinstance(hizi, (int, float)) and 0.5 <= hizi <= 2 else 1), len(olcum)


def kelime_araligi(k: dict, dil: str) -> list[int]:
    orta = konusma_hizi(k, dil)[0] * float(k["uzunluk"]["hedef_dk"])
    onluk = lambda x: int(math.floor(x / 10 + 0.5) * 10)  # noqa: E731 (arayüzdeki hesapla aynı yuvarlama)
    return [onluk(orta * (1 - KELIME_PAYI)), onluk(orta * (1 + KELIME_PAYI))]


def kelime_hesapla(k: dict) -> dict:
    """kelime_otomatik açıksa Türkçe ve hedef dil kelime aralıklarını süreden hesaplar (k yerinde değişir)."""
    u = k.get("uzunluk") or {}
    dk = u.get("hedef_dk")
    if u.get("kelime_otomatik") and isinstance(dk, (int, float)) and not isinstance(dk, bool) and 1 <= dk <= 60:
        u["calisma_kelime"] = kelime_araligi(k, "tr")
        u["hedef_kelime"] = kelime_araligi(k, (k.get("dil") or {}).get("hedef") or "tr")
    return k


def hiz_kaydet(kisaltma: str, kod: str, dil: str, kelime: int, sure_sn: float, ses_hizi: float = 1) -> float | None:
    """Bir videonun gerçek ses süresinden konuşma hızını kaydeder (aynı video yeniden ölçülürse eskisinin yerine).
    Akla yatkın olmayan ölçüm (çok kısa ya da 60–260 kelime/dk dışı) kaydedilmez. → kelime/dk (hız 1,0'a göre)."""
    if kelime < 50 or sure_sn < 20:
        return None
    hiz = kelime / (sure_sn / 60) / (ses_hizi if isinstance(ses_hizi, (int, float)) and 0.5 <= ses_hizi <= 2 else 1)
    if not 60 <= hiz <= 260:
        return None
    yol = _ayar_yolu(kisaltma)
    ham = A.json_oku(yol, {}) or {}
    olcum = ham.setdefault("uzunluk", {}).setdefault("hiz_olcum", {})
    eski = [x for x in olcum.get(dil, []) if isinstance(x, dict) and x.get("kod") != kod]
    olcum[dil] = (eski + [{"kod": kod, "hiz": round(hiz, 1), "kelime": kelime, "sure_sn": round(sure_sn, 1),
                           "tarih": datetime.now().isoformat(timespec="seconds")}])[-HIZ_OLCUM_SAYISI:]
    A.json_yaz(yol, ham)
    kayit.yaz(f"Konuşma hızı ölçüldü ({kod}, {DILLER.get(dil, dil)}): {kelime} kelime / {sure_sn / 60:.1f} dk → "
              f"dakikada {hiz:.0f} kelime")
    return hiz


def liste() -> list[dict]:
    sonuc = []
    if not yollar.kanallar().exists():
        return sonuc
    for k in sorted(yollar.kanallar().iterdir()):
        if k.is_dir() and (k / "kanal.json").exists() and KISALTMA.match(k.name):
            try:
                c = oku(k.name)
            except (ValueError, json.JSONDecodeError) as e:
                kayit.yaz(f"Kanal okunamadı ({k.name}): {e}", "uyari")
                continue
            sonuc.append({"kisaltma": c["kisaltma"], "ad": c["ad"], "kod_oneki": c["kod_oneki"],
                          "hedef_dil": c["dil"]["hedef"], "hedef_dil_adi": DILLER.get(c["dil"]["hedef"], ""),
                          "test": bool(c.get("test")), "video_sayisi": len(videolar(k.name))})
    return sonuc


def videolar(kisaltma: str) -> list[str]:
    v = klasor(kisaltma) / "Videolar"
    return sorted(p.name for p in v.iterdir() if p.is_dir()) if v.exists() else []


# --- doğrulama ------------------------------------------------------------

def _sayi(d: dict, yol: str, hatalar: list, en_az=None, en_cok=None, tam=False) -> None:
    parca = yol.split(".")
    x = d
    for p in parca:
        x = x[int(p)] if isinstance(x, list) else x.get(p)
    if isinstance(x, bool) or not isinstance(x, (int, float)) or (tam and int(x) != x):
        hatalar.append(f"{yol}: sayı olmalı")
        return
    if (en_az is not None and x < en_az) or (en_cok is not None and x > en_cok):
        hatalar.append(f"{yol}: {en_az}–{en_cok} arasında olmalı")


def dogrula(k: dict, kendi: str | None = None) -> tuple[list[str], list[str]]:
    """→ (hatalar, uyarılar). kendi: düzenlenen kanalın kısaltması (benzersizlik denetiminde kendisi sayılmaz)."""
    h, u = [], []
    k = kelime_hesapla(copy.deepcopy(k))
    k = dict(k, kisaltma=str(k.get("kisaltma", "")).strip().lower(), kod_oneki=str(k.get("kod_oneki", "")).strip().upper())
    ad = str(k.get("ad", "")).strip()
    if not ad or len(ad) > 60:
        h.append("Kanal adı 1–60 karakter olmalı")
    if not KISALTMA.match(str(k.get("kisaltma", ""))):
        h.append("Kısaltma küçük harf, rakam ve tireyle 2–31 karakter olmalı (ör. bilim-kahvesi, tarih-kanali)")
    if not KOD_ONEKI.match(str(k.get("kod_oneki", ""))) or len(str(k.get("kod_oneki", ""))) > 12:
        h.append("Video kodu öneki büyük harf/rakam, tireyle ayrılabilir, en fazla 12 karakter (ör. BK, TRH-VID)")
    for c in liste():
        if c["kisaltma"] == kendi:
            continue
        if c["kisaltma"] == k.get("kisaltma"):
            h.append(f"'{c['kisaltma']}' kısaltması başka bir kanalda kullanılıyor")
        if c["kod_oneki"].upper() == str(k.get("kod_oneki", "")).upper():
            h.append(f"'{c['kod_oneki']}' öneki '{c['ad']}' kanalında kullanılıyor")
    if k.get("dil", {}).get("hedef") not in DILLER:
        h.append("Hedef dil listeden seçilmeli")
    _sayi(k, "kod_hane", h, 2, 3, tam=True)
    _sayi(k, "uzunluk.hedef_dk", h, 1, 60)
    for alan in () if k["uzunluk"].get("kelime_otomatik") else ("calisma_kelime", "hedef_kelime"):
        _sayi(k, f"uzunluk.{alan}.0", h, 50, 20000, tam=True)
        _sayi(k, f"uzunluk.{alan}.1", h, 50, 20000, tam=True)
        a = k["uzunluk"][alan]
        if all(isinstance(x, (int, float)) for x in a) and a[0] >= a[1]:
            h.append(f"uzunluk.{alan}: alt sınır üst sınırdan küçük olmalı")
    _sayi(k, "uzunluk.kart_karakter", h, 500, 20000, tam=True)
    _sayi(k, "uzunluk.hook_esigi", h, 1, 10)
    s = k.get("ses", {})
    for alan, a, b in (("stability", 0, 1), ("similarity_boost", 0, 1), ("style", 0, 1), ("speed", 0.7, 1.2)):
        _sayi(k, f"ses.{alan}", h, a, b)
    if not s.get("voice_id"):
        u.append("Ses (voice_id) seçilmedi; üretim başlamadan önce gerekli")
    if s.get("language_code") and s["language_code"] != k.get("dil", {}).get("hedef"):
        u.append(f"Ses dil kodu ({s['language_code']}) hedef dilden ({k.get('dil', {}).get('hedef')}) farklı")
    g = k.get("gorsel", {})
    if g.get("karakter") and not re.fullmatch(r"@[\wÀ-ÿ\-]{1,30}", g["karakter"]):
        h.append("Karakter etiketi @ ile başlamalı (ör. @Mira) ya da boş bırakılmalı")
    if not isinstance(g.get("yasakli"), list) or not isinstance(g.get("izinli_olumsuz"), list):
        h.append("Yasaklı kelimeler ve izinli olumsuzlamalar liste olmalı")
    e = k.get("etiketler", {})
    sen = e.get("senaryo", {})
    if not isinstance(sen, dict) or set(sen) != {"karakter", "metafor", "sema", "ilk30"} or \
            not all(re.fullmatch(r"[\wÀ-ÿ★\-]{1,20}", str(x)) for x in sen.values()):
        h.append("Senaryo etiketleri: karakter, metafor, şema ve ilk 30 sn için birer kısa ad (boşluksuz)")
    elif len(set(sen.values())) < 4:
        h.append("Senaryo etiketleri birbirinden farklı olmalı")
    if not isinstance(e.get("ses"), list) or not e["ses"] or \
            not all(re.fullmatch(r"[a-z][a-z ]{1,20}", str(x)) for x in e["ses"]):
        h.append("Ses tag'leri küçük harfli kısa kelimeler olmalı (ör. calm, softly)")
    _sayi(k, "etiketler.tag_orani", h, 0, 100)
    m = k.get("montaj", {})
    _sayi(k, "montaj.son_ekran_sn", h, 0, 30)
    _sayi(k, "montaj.muzik_lufs", h, -60, -10)
    mk = m.get("maskot", {})
    n = len(mk.get("dosyalar", []))
    gecersiz = [x for x in mk.get("sira", []) if not re.fullmatch(r"M\d", str(x)) or not 1 <= int(str(x)[1:]) <= n]
    if gecersiz:
        h.append(f"Maskot sırası yalnız M1…M{n} içerebilir ({', '.join(map(str, gecersiz))} geçersiz)" if n else
                 "Maskot dosyası yokken maskot sırası boş olmalı")
    alt = m.get("altyazi", {})
    for r in ("yazi", "kutu"):
        if not RENK.match(str(alt.get(r, ""))):
            h.append(f"Altyazı {('yazı' if r == 'yazi' else 'kutu')} rengi #RRGGBB olmalı")
    _sayi(k, "montaj.altyazi.kutu_opaklik", h, 0, 1)
    _sayi(k, "montaj.altyazi.boyut", h, 1, 40)
    if set(k.get("onaylar", {})) - {x for x, _ in ASAMALAR if x not in ("sahne",)}:
        h.append("Onaylar yalnız konu, araştırma, senaryo, çeviri ve paketleme için ayarlanır")
    modeller = A.genel()["modeller"]
    for is_adi, isa in k.get("isler", {}).items():
        if isa.get("model") not in modeller:
            h.append(f"{is_adi}: bilinmeyen model {isa.get('model')}")
    _sayi(k, "butce.video_usd", h, 0.01, 500)
    for etiket, desen in (k.get("kalip_sayaclari") or {}).items():
        try:
            re.compile(desen)
        except re.error:
            h.append(f"Kalıp sayacı '{etiket}': geçersiz düzenli ifade")
    for kelime in k.get("hassas_kelimeler") or []:
        try:
            re.compile(kelime)
        except re.error:
            h.append(f"Hassas kelime '{kelime}': geçersiz düzenli ifade")
    return h, u


# --- ekleme ---------------------------------------------------------------

def _yer_tutucular(k: dict) -> dict[str, str]:
    return {"{{KANAL_ADI}}": k["ad"], "{{KOD_ONEKI}}": k["kod_oneki"],
            "{{HEDEF_DIL}}": DILLER.get(k["dil"]["hedef"], k["dil"]["hedef"]), "{{HEDEF_DIL_KODU}}": k["dil"]["hedef"]}


def _sablon_yaz(k: dict, hedef: Path) -> None:
    kaynak = yollar.SABLONLAR / "kanal"
    yer = _yer_tutucular(k)
    for dosya in kaynak.rglob("*.md"):
        metin = dosya.read_text(encoding="utf-8")
        for a, b in yer.items():
            metin = metin.replace(a, b)
        A.atomik_yaz(hedef / dosya.relative_to(kaynak), metin)


def anayasa_metni(govde: str, k: dict) -> str:
    """Yeni kanal dosyasının B bölümünden 01_Anayasa.md: şablonun baş kısmı (doldurma notu olmadan) + gövde."""
    sablon = (yollar.SABLONLAR / "kanal" / "Proje_dosyalari" / "01_Anayasa.md").read_text(encoding="utf-8")
    bas = sablon.split("\n## 1.", 1)[0]
    bas = "\n".join(x for x in bas.split("\n") if not x.startswith(">")).replace(
        "Sürüm 1 · kanal açıldı.", "Sürüm 1 · kanal açıldı (yeni kanal dosyasından).")
    metin = re.sub(r"\n{3,}", "\n\n", bas.rstrip()) + "\n\n" + govde.strip() + "\n"
    for a, b in _yer_tutucular(k).items():
        metin = metin.replace(a, b)
    return metin


def ekle(veri: dict, kaynak: str = "sablon", ice_aktar_klasor: str = "", anayasa: str = "") -> dict:
    """Yeni kanal: doğrular, klasörleri kurar, kanal.json'u yazar, şablonları (ya da içe aktarılanları) koyar.
    anayasa: yeni kanal dosyasının anayasa bölümü (varsa 01_Anayasa.md olur)."""
    k = A.birlestir(varsayilan(), veri or {})
    k["kisaltma"] = str(k.get("kisaltma", "")).strip().lower()
    k["kod_oneki"] = str(k.get("kod_oneki", "")).strip().upper()
    if not k["ses"].get("language_code"):
        k["ses"]["language_code"] = k["dil"]["hedef"]
    kelime_hesapla(k)
    hatalar, _ = dogrula(k)
    if hatalar:
        raise ValueError("; ".join(hatalar))
    hedef = klasor(k["kisaltma"])
    if hedef.exists():
        raise ValueError(f"Kanallar/{k['kisaltma']} klasörü zaten var")
    if kaynak == "klasor" and not Path(ice_aktar_klasor).expanduser().is_dir():
        raise ValueError("İçe aktarılacak klasör bulunamadı")
    k.update(kimlik=uuid.uuid4().hex, olusturma=datetime.now().isoformat(timespec="seconds"))
    gecici = hedef.with_name(f".{k['kisaltma']}.kuruluyor")
    if gecici.exists():
        shutil.rmtree(gecici)  # yarım kalmış önceki kurulum (uygulamanın kendi ara klasörü)
    try:
        for alt in ALT_KLASORLER:
            (gecici / alt).mkdir(parents=True, exist_ok=True)
        _sablon_yaz(k, gecici)
        A.json_yaz(gecici / "kanal.json", k)
        A.json_yaz(gecici / "taslaklar.json", [])
        rapor = ice_aktar(gecici, Path(ice_aktar_klasor).expanduser()) if kaynak == "klasor" else []
        if (anayasa or "").strip():
            A.atomik_yaz(gecici / "Proje_dosyalari" / "01_Anayasa.md", anayasa_metni(anayasa, k))
            rapor.append("Anayasa: yeni kanal dosyasından")
        gecici.rename(hedef)
    except Exception:
        shutil.rmtree(gecici, ignore_errors=True)
        raise
    kayit.yaz(f"Kanal eklendi: {k['ad']} ({k['kisaltma']}, {k['kod_oneki']}, {DILLER[k['dil']['hedef']]})")
    if aktif() is None:
        aktif_sec(k["kisaltma"])
    return {"kanal": k, "ice_aktarma": rapor}


# --- içe aktarma ----------------------------------------------------------

_BECERI_ESLEME = (("konu", "konu"), ("arastirma", "arastirma"), ("senaryo", "senaryo"), ("ceviri", "ceviri"),
                  ("italyanca", "ceviri"), ("hedef", "ceviri"), ("translat", "ceviri"), ("sahne", "sahne"),
                  ("paketleme", "paketleme"))


def ice_aktar(kanal_klasoru: Path, kaynak: Path) -> list[str]:
    """kaynak klasördeki beceri, proje dosyası ve medyayı kanal klasörüne KOPYALAR (kaynak değişmez).
    Arsiv/Videolar/Silinecekler gibi klasörlerdeki eski kopyalar atlanır; aynı hedefe birden çok aday varsa
    adında CURRENT geçen, sonra en üst klasördeki seçilir."""
    rapor = []

    def uygun(p: Path) -> bool:
        return not any(x.lower().startswith(tuple(ATLA)) for x in p.relative_to(kaynak).parts[:-1])

    def sec(adaylar: dict[str, list[Path]]) -> dict[str, Path]:
        return {h: min(l, key=lambda p: ("CURRENT" not in p.name, len(p.relative_to(kaynak).parts), len(p.name)))
                for h, l in adaylar.items()}

    beceri: dict[str, list[Path]] = {}
    for skill in kaynak.rglob("SKILL.md"):
        ad = skill.parent.name.lower()
        hedef = next((h for anahtar, h in _BECERI_ESLEME if anahtar in ad), None)
        if hedef and uygun(skill):
            beceri.setdefault(hedef, []).append(skill)
    for hedef, skill in sorted(sec(beceri).items()):
        shutil.copy2(skill, kanal_klasoru / "Beceriler" / hedef / "SKILL.md")
        rapor.append(f"Beceri: {skill.parent.name} → {hedef}")
    proje: dict[str, list[Path]] = {}
    for md in kaynak.rglob("*.md"):
        m = re.match(r"(?:[A-Za-z]+_)?0([0-3])_", md.name)
        if m and md.name != "SKILL.md" and uygun(md):
            proje.setdefault(PROJE_DOSYALARI[int(m.group(1))], []).append(md)
    for hedef, md in sorted(sec(proje).items()):
        shutil.copy2(md, kanal_klasoru / "Proje_dosyalari" / hedef)
        rapor.append(f"Proje dosyası: {md.name} → {hedef}")
    for ad, alt in (("muzik", "Muzik"), ("maskot", "Maskot")):
        for d in (p for p in kaynak.rglob("*") if p.is_dir() and p.name.lower() == ad and uygun(p / "x")):
            for f in sorted(d.iterdir()):
                if f.is_file() and f.suffix.lower() in MEDYA:
                    shutil.copy2(f, kanal_klasoru / "Varliklar" / alt / f.name)
                    rapor.append(f"{alt}: {f.name}")
    return rapor


# --- güncelleme -----------------------------------------------------------

def guncelle(kisaltma: str, degisiklik: dict) -> tuple[dict, list[str]]:
    eski = oku(kisaltma)
    degisiklik = dict(degisiklik or {})
    for sabit in ("kisaltma", "kimlik", "olusturma"):
        degisiklik.pop(sabit, None)
    if "kod_oneki" in degisiklik:
        degisiklik["kod_oneki"] = str(degisiklik["kod_oneki"]).strip().upper()
    yeni = A.birlestir(eski, degisiklik)
    # Listeler birleştirilmez, olduğu gibi alınır
    for yol in (("gorsel", "yasakli"), ("gorsel", "izinli_olumsuz"), ("etiketler", "ses"), ("montaj", "maskot", "dosyalar"),
                ("montaj", "maskot", "sira"), ("hassas_kelimeler",), ("uzunluk", "calisma_kelime"), ("uzunluk", "hedef_kelime"),
                ("kalip_sayaclari",), ("etiketler", "ses_sinir")):
        kaynak = degisiklik
        for p in yol:
            kaynak = kaynak.get(p) if isinstance(kaynak, dict) else None
        if isinstance(kaynak, list) or (isinstance(kaynak, dict) and yol in (("kalip_sayaclari",), ("etiketler", "ses_sinir"))):
            hedef = yeni
            for p in yol[:-1]:
                hedef = hedef[p]
            hedef[yol[-1]] = kaynak
    if videolar(kisaltma):
        for alan, ad in ((("kod_oneki",), "Video kodu öneki"), (("dil", "hedef"), "Hedef dil")):
            a, b = eski, yeni
            for p in alan:
                a, b = a[p], b[p]
            if a != b:
                raise ValueError(f"{ad} bu kanalda video üretildikten sonra değiştirilemez")
    hatalar, uyarilar = dogrula(yeni, kendi=kisaltma)
    if hatalar:
        raise ValueError("; ".join(hatalar))
    if eski["dil"]["hedef"] != yeni["dil"]["hedef"]:
        uyarilar.append("Hedef dil değişti: beceri ve proje dosyalarında eski dil adı geçiyor olabilir; kontrol et")
    A.json_yaz(_ayar_yolu(kisaltma), yeni)
    kayit.yaz(f"Kanal ayarları kaydedildi: {yeni['ad']}")
    return yeni, uyarilar


# --- silme ----------------------------------------------------------------

def taslaklar_dosyasi(kisaltma: str) -> Path:
    return klasor(kisaltma) / "taslaklar.json"


def taslak_kaydet(kisaltma: str, taslak_klasoru: Path) -> None:
    """Kanal Stüdyosu bir CapCut taslağı oluşturunca çağırır: iki iz bırakır (kayıt + taslak içindeki işaret)."""
    k = oku(kisaltma)
    taslak_klasoru = Path(taslak_klasoru)
    A.json_yaz(taslak_klasoru / ISARET, {"kanal_kimlik": k["kimlik"], "kanal": kisaltma,
                                         "olusturma": datetime.now().isoformat(timespec="seconds")})
    kayitli = A.json_oku(taslaklar_dosyasi(kisaltma), []) or []
    if taslak_klasoru.name not in kayitli:
        A.json_yaz(taslaklar_dosyasi(kisaltma), kayitli + [taslak_klasoru.name])


def silinecek_taslaklar(kisaltma: str) -> tuple[list[Path], list[str]]:
    """→ (Çöp'e gidecek taslak klasörleri, dokunulmayacakların nedenleri)."""
    k = oku(kisaltma)
    kok = A.yol("capcut_taslak")
    gidecek, kalan = [], []
    for ad in A.json_oku(taslaklar_dosyasi(kisaltma), []) or []:
        if not isinstance(ad, str) or "/" in ad or ad in ("", ".", ".."):
            continue
        t = kok / ad
        if not t.is_dir():
            continue
        isaret = A.json_oku(t / ISARET, None)
        if isinstance(isaret, dict) and isaret.get("kanal_kimlik") == k["kimlik"]:
            gidecek.append(t)
        else:
            kalan.append(f"{ad}: Kanal Stüdyosu işareti yok ya da başka kanala ait; dokunulmadı")
    return gidecek, kalan


def sil(kisaltma: str, onay_adi: str) -> dict:
    k = oku(kisaltma)
    if str(onay_adi).strip().casefold() != k["ad"].strip().casefold():
        raise ValueError("Silmek için kanal adını aynen yaz")
    akt = A.json_oku(yollar.aktif_dosyasi(), {}) or {}
    if (akt.get("uretim") or {}).get("kanal") == kisaltma:
        raise ValueError("Bu kanalda süren bir üretim var; önce üretimi kapat ya da iptal et")
    gidecek, kalan = silinecek_taslaklar(kisaltma)
    tasinan = []
    for t in gidecek:
        cop.tasi(t)
        tasinan.append(f"CapCut taslağı: {t.name}")
    cop.tasi(klasor(kisaltma))
    tasinan.append(f"Kanal klasörü: Kanallar/{kisaltma}")
    if akt.get("kanal") == kisaltma:
        akt.pop("kanal", None)
        diger = liste()
        if diger:
            akt["kanal"] = diger[0]["kisaltma"]
        A.json_yaz(yollar.aktif_dosyasi(), akt)
    kayit.yaz(f"Kanal silindi (Çöp Kutusu'na taşındı): {k['ad']} · {len(tasinan)} öğe")
    return {"tasinan": tasinan, "dokunulmayan": kalan}


# --- seçim ----------------------------------------------------------------

def aktif() -> str | None:
    k = (A.json_oku(yollar.aktif_dosyasi(), {}) or {}).get("kanal")
    return k if k and (yollar.kanallar() / k / "kanal.json").exists() else None


def aktif_sec(kisaltma: str) -> None:
    oku(kisaltma)
    akt = A.json_oku(yollar.aktif_dosyasi(), {}) or {}
    if (akt.get("uretim") or {}).get("kanal") not in (None, kisaltma):
        raise ValueError("Süren bir üretim varken kanal değiştirilemez")
    akt["kanal"] = kisaltma
    A.json_yaz(yollar.aktif_dosyasi(), akt)


# --- kanal dosyaları (proje dosyaları ve beceriler) -------------------------

def _dosya_yolu(kisaltma: str, ad: str) -> Path:
    if ad in PROJE_DOSYALARI:
        return klasor(kisaltma) / "Proje_dosyalari" / ad
    m = re.fullmatch(r"Beceriler/([a-z]+)/SKILL\.md", ad)
    if m and m.group(1) in dict(ASAMALAR):
        return klasor(kisaltma) / ad
    raise ValueError("Bu dosya düzenlenemez")


def dosyalar(kisaltma: str) -> list[dict]:
    sonuc = []
    for ad in list(PROJE_DOSYALARI) + [f"Beceriler/{a}/SKILL.md" for a, _ in ASAMALAR]:
        yol = _dosya_yolu(kisaltma, ad)
        metin = yol.read_text(encoding="utf-8") if yol.exists() else ""
        sonuc.append({"ad": ad, "var": yol.exists(), "doldur": metin.count(DOLDUR), "boyut": len(metin)})
    return sonuc


def dosya_oku(kisaltma: str, ad: str) -> str:
    yol = _dosya_yolu(kisaltma, ad)
    return yol.read_text(encoding="utf-8") if yol.exists() else ""


def dosya_yaz(kisaltma: str, ad: str, icerik: str) -> None:
    """Önceki hâl kanal klasöründeki .yedek/ altına tarihli kopya olarak saklanır."""
    yol = _dosya_yolu(kisaltma, ad)
    if yol.exists():
        yedek = klasor(kisaltma) / ".yedek" / f"{datetime.now():%Y%m%d_%H%M%S}_{ad.replace('/', '_')}"
        yedek.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(yol, yedek)
    A.atomik_yaz(yol, icerik)


# --- üretime hazırlık -------------------------------------------------------

def eksikler(kisaltma: str) -> list[dict]:
    """Üretim başlamadan tamamlanması gerekenler (zorunlu) ve öneriler."""
    k = oku(kisaltma)
    kl = klasor(kisaltma)
    sonuc = []
    if not k["ses"].get("voice_id"):
        sonuc.append({"zorunlu": True, "mesaj": "Kanal ayarları › Ses: ElevenLabs sesi (voice_id) seçilmedi"})
    doldurulmamis = [d["ad"] for d in dosyalar(kisaltma) if d["doldur"]]
    if doldurulmamis:
        sonuc.append({"zorunlu": False, "mesaj": "Kanal dosyalarında doldurulmamış yer var: " + ", ".join(doldurulmamis)})
    if k["montaj"]["muzik"] and not any(f.suffix.lower() in {".mp3", ".m4a", ".wav", ".aac"}
                                        for f in (kl / "Varliklar/Muzik").glob("*")):
        sonuc.append({"zorunlu": False, "mesaj": "Müzik açık ama Varliklar/Muzik klasörü boş (müziksiz üretilir)"})
    for f in k["montaj"]["maskot"]["dosyalar"]:
        if not (kl / "Varliklar/Maskot" / f).exists():
            sonuc.append({"zorunlu": True, "mesaj": f"Maskot dosyası yok: Varliklar/Maskot/{f}"})
    if k["gorsel"]["karakter"] and not any((kl / "Varliklar/Karakter").glob("*")):
        sonuc.append({"zorunlu": False, "mesaj": f"{k['gorsel']['karakter']} için Varliklar/Karakter'e referans görsel koyabilirsin"})
    return sonuc
```

### `app/kanal_studyosu/kayit.py`

```python
"""Uygulama kaydı: stderr'e (başlatıcı Sistem/kayit.log'a yönlendirir) ve arayüz paneli için son satırlar."""
from __future__ import annotations

import collections
import sys
import threading
from datetime import datetime

_SON = collections.deque(maxlen=1500)
_KILIT = threading.Lock()


def yaz(mesaj: str, duzey: str = "bilgi") -> None:
    satir = f"{datetime.now().strftime('%H:%M:%S')} [{duzey}] {mesaj}"
    with _KILIT:
        _SON.append(satir)
    print(satir, file=sys.stderr, flush=True)


def son(n: int = 1000) -> list[str]:
    with _KILIT:
        return list(_SON)[-n:]
```

### `app/kanal_studyosu/kontroller.py`

```python
"""Modele gitmeden yapılan kontroller.

hatalar  → otomatik düzeltme turuna girer (aşamaya "düzeltme: …" olarak gider).
uyarilar → düzeltme istemez; ONAY ekranında "dikkat" olarak gösterilir.
Kurallar becerilerden, sayılar/etiketler/yasaklı kelimeler seçili kanalın ayarlarından (kanal.json) gelir.
Aşama 4'te TR/hedef dil paragraf uzunluğu, replik ve sayı karşılaştırması yapılmaz (iki dilde doğal olarak farklıdır).
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from . import kanal
from . import metin as M


@dataclass
class Sonuc:
    hatalar: list[str] = field(default_factory=list)
    uyarilar: list[str] = field(default_factory=list)
    bilgiler: list[str] = field(default_factory=list)
    ek: dict = field(default_factory=dict)  # sonraki adımlara taşınan bilgi (ör. maskot argümanları)

    @property
    def temiz(self) -> bool:
        return not self.hatalar

    def sozluk(self) -> dict:
        return {"hatalar": self.hatalar, "uyarilar": self.uyarilar, "bilgiler": self.bilgiler, "ek": self.ek}




def eksik_dosyalar(dosyalar: dict[str, str], beklenen: list[str]) -> list[str]:
    return [f"{ad} dosyası eksik ya da boş" for ad in beklenen if not dosyalar.get(ad, "").strip()]


def konu_karti(kart: str) -> Sonuc:
    s = Sonuc()
    n = len(kart.strip())
    s.bilgiler.append(f"Kart {n} karakter")
    sinir = int(kanal.ayar()["uzunluk"]["kart_karakter"])
    if n > sinir:
        s.hatalar.append(f"Konu kartı {n} karakter; sınır {sinir:,}. En uzun alanları kısalt.".replace(",", "."))
    if "KONU KARTI" not in kart:
        s.hatalar.append(f"Kart 'KONU KARTI · {kanal.onek()}-0X' başlığıyla başlamıyor.")
    return s


def senaryo_tr(tr: str) -> Sonuc:
    s = Sonuc()
    sen = M.ayir(tr)
    k = M.kelime_sayisi(sen.paragraflar)
    s.bilgiler.append(f"Kelime {k} · Paragraf {len(sen.paragraflar)}")
    a, b = kanal.ayar()["uzunluk"]["calisma_kelime"]
    if not a <= k <= b:
        s.hatalar.append(f"Türkçe metin {k} kelime; hedef {_s(a)}–{_s(b)} (etiketler hariç).")
    etiketsiz = [i for i, p in enumerate(sen.paragraflar, 1) if not M.ETIKET.match(p)]
    if etiketsiz:
        s.uyarilar.append("Etiketsiz paragraf: " + ", ".join(f"¶{i}" for i in etiketsiz[:10]))
    _senaryo_etiketleri(tr, s)
    return s


def _s(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def senaryo_etiketleri() -> set[str]:
    return set(kanal.ayar()["etiketler"]["senaryo"].values())


def _etiket_metni() -> str:
    return " ".join(f"[{x}]" for x in kanal.ayar()["etiketler"]["senaryo"].values())


def _senaryo_etiketleri(metin: str, s: Sonuc) -> None:
    """Senaryoda geçerli etiketler yalnız kanal ayarındaki dört etiket."""
    gecerli, yabanci = senaryo_etiketleri(), []
    for i, p in enumerate(M.ayir(metin).paragraflar, 1):
        for t in re.findall(r"\[([^\]\n]{1,60})\]", p):
            if t.strip() not in gecerli:
                yabanci.append(f"¶{i} [{t}]")
    if yabanci:
        s.uyarilar.append(f"Geçersiz etiket (yalnız {_etiket_metni()}): " + ", ".join(yabanci[:10]))


# Hazır metin: karşılaştırmada yazım biçimi farkı sayılmayan işaretler (kıvrık/düz tırnak, üç nokta).
_HAZIR_ESDEGER = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "«": '"', "»": '"', "…": "..."})
HAZIR_UZUN_PARAGRAF = 90  # kelime; yalnız uyarı


def _hazir_kelimeler(metin: str) -> list[str]:
    return " ".join(M.govde(p) for p in M.ayir(metin).paragraflar).translate(_HAZIR_ESDEGER).split()


def hazir_metin(orijinal: str, metin: str, dil: str) -> Sonuc:
    """Kullanıcının hazır metni: model yalnız paragraf araları ve etiketler ekleyebilir. Etiketler ve teslim
    satırları çıkarılınca kelimeler aynen aynı olmalı (hata). Kelime aralığı ve etiket notları uyarıdır."""
    s = Sonuc()
    a, b = _hazir_kelimeler(orijinal), _hazir_kelimeler(metin)
    sen = M.ayir(metin)
    s.bilgiler.append(f"Kelime {M.kelime_sayisi(sen.paragraflar)} · Paragraf {len(sen.paragraflar)}")
    if a != b:
        farklar = []
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
            if op == "equal":
                continue
            once = " ".join(a[max(0, i1 - 4):i1])
            farklar.append(f"“…{once} [{' '.join(a[i1:i2]) or '—'}]” yerine “[{' '.join(b[j1:j2]) or '—'}]”")
            if len(farklar) == 3:
                break
        s.hatalar.append("Metin değişmiş: etiketler çıkarılınca kullanıcının metniyle kelimesi kelimesine aynı "
                         "olmalı. Yalnız paragraf araları ve etiketler eklenebilir. Farklar: " + "; ".join(farklar))
    k = M.kelime_sayisi(sen.paragraflar)
    u = kanal.ayar()["uzunluk"]
    alt, ust = u["calisma_kelime"] if dil == "tr" else u["hedef_kelime"]
    if not alt <= k <= ust:
        s.uyarilar.append(f"Metin {k} kelime; bu dilde hedef {_s(alt)}–{_s(ust)} (hazır metin olduğu için yalnız bilgi).")
    etiketsiz = [i for i, p in enumerate(sen.paragraflar, 1) if not M.ETIKET.match(p)]
    if etiketsiz:
        s.uyarilar.append("Etiketsiz paragraf: " + ", ".join(f"¶{i}" for i in etiketsiz[:10]))
    uzun = [i for i, p in enumerate(sen.paragraflar, 1) if M.kelime_sayisi([p]) > HAZIR_UZUN_PARAGRAF]
    if uzun:
        s.uyarilar.append(f"{HAZIR_UZUN_PARAGRAF} kelimeden uzun paragraf (tek sahne için uzun olabilir): " +
                          ", ".join(f"¶{i}" for i in uzun[:10]))
    _senaryo_etiketleri(metin, s)
    return s


def hazir_kuyruk(metin: str, dil: str) -> str:
    """Hazır metnin teslim satırı (modelin yazdığı değil, kodun saydığı)."""
    sen = M.ayir(metin)
    k, n = M.kelime_sayisi(sen.paragraflar), len(sen.paragraflar)
    sen.kuyruk = (f"Kelime: {k}" if dil == "tr" else f"Parole: {k} · Paragrafi: {n}" if dil == "it"
                  else f"Words: {k} · Paragraphs: {n}")
    return sen.metin()


def senaryo_it(tr: str, it: str) -> Sonuc:
    """Hedef dil final (Aşama 4): kelime aralığı, paragraf sayısı TR ile aynı, hook ≥ eşik, teslim satırları
    (kanal ayarından). Ayrıca çift paragraf. TR/hedef dil uzunluk, replik ve sayı karşılaştırması yapılmaz."""
    s = Sonuc()
    T, I = M.ayir(tr), M.ayir(it)
    k = M.kelime_sayisi(I.paragraflar)
    dk, dil = kanal.hedef_dil().upper(), kanal.dil_adi()
    s.bilgiler.append(f"Kelime {k} · Paragraf {dk} {len(I.paragraflar)} / TR {len(T.paragraflar)}")
    a, b = kanal.ayar()["uzunluk"]["hedef_kelime"]
    if not a <= k <= b:
        s.hatalar.append(f"{dil} metin {k} kelime; hedef {_s(a)}–{_s(b)} (etiketler hariç).")
    if len(T.paragraflar) != len(I.paragraflar):
        s.hatalar.append(f"Paragraf sayısı farklı: TR {len(T.paragraflar)}, {dk} {len(I.paragraflar)}. "
                         f"Her TR paragrafının tek bir {dk} karşılığı olmalı.")
    govdeler = [M.govde(p) for p in I.paragraflar]
    for i in range(len(govdeler)):
        for j in range(i + 1, min(len(govdeler), i + 8)):
            if difflib.SequenceMatcher(None, govdeler[i], govdeler[j]).ratio() > 0.8:
                s.hatalar.append(f"¶{i + 1} ve ¶{j + 1} neredeyse aynı (çift paragraf). "
                                 f"TR ¶{j + 1}'in karşılığı eksik olabilir.")
    if not M.KELIME_SATIRI.search(I.kuyruk):
        s.hatalar.append("Teslim satırları (kelime ve paragraf sayısı, Hook puanı, Bilgi kazancı …) eksik.")
    esik = float(kanal.ayar()["uzunluk"]["hook_esigi"])
    m = re.search(r"Hook puan\w*\s*:\s*(\d+(?:[.,]\d+)?)\s*/\s*10", I.kuyruk)
    if m and float(m.group(1).replace(",", ".")) < esik:
        s.hatalar.append(f"Hook puanı {m.group(1)}/10; en az {esik:g} olmalı.")
    _senaryo_etiketleri(it, s)
    return s


# Eski sistemin iç işaretleri ([SOURCE NEEDED], [SAFETY REVIEW NEEDED]). Artık kullanılmıyor; model eski beceri
# kopyasından ya da önceki aşama metninden taşırsa dosyaya yazılmadan önce mekanik olarak çıkarılır
# (yerlerini "Açık noktalar" satırı tutar). Metnin geri kalanına dokunulmaz.
IC_ISARET = re.compile(r"[ \t]*\[(?:SOURCE NEEDED|SAFETY REVIEW NEEDED)\]")


def ic_isaretleri_temizle(metin: str) -> tuple[str, int]:
    yeni, n = IC_ISARET.subn("", metin)
    return (re.sub(r"[ \t]+\n", "\n", yeni) if n else metin), n


def izinli_tag() -> set[str]:
    return {t.strip().lower() for t in kanal.ayar()["etiketler"]["ses"]}


def tag_sinirlari() -> dict[str, int]:
    return {t.strip().lower(): int(n) for t, n in kanal.ayar()["etiketler"].get("ses_sinir", {}).items()}


def izinli_tag_metni() -> str:
    sinir = tag_sinirlari()
    m = " ".join(f"[{t}]" for t in sorted(izinli_tag()) if t not in sinir)
    return m + "".join(f" ve en fazla {n} [{t}]" for t, n in sinir.items())


def elevenlabs_metni(metin: str) -> list[str]:
    """Seslendirmeye giden metinde yalnız kanal ayarındaki ses tag'leri (sınırlarıyla) olabilir. Başka her köşeli
    not (ör. [SOURCE NEEDED], büyük harfli notlar) seslendirmeyi başlatmadan durdurur."""
    izinli, sinir = izinli_tag(), tag_sinirlari()
    sorun, say = [], {}
    for i, p in enumerate(bloklar(metin), 1):
        for t in re.findall(r"\[([^\]\n]*)\]", p):
            t_ = t.strip().lower()
            if t_ not in izinli:
                sorun.append(f"sahne {i}: [{t}]")
            else:
                say[t_] = say.get(t_, 0) + 1
    for t, n in sinir.items():
        if say.get(t, 0) > n:
            sorun.append(f"[{t}] {say[t]} kez (en fazla {n})")
    return sorun


def duzeltme_mesaji(onay_no: int | None, sonuc: Sonuc) -> str:
    satirlar = "\n".join(f"- {h}" for h in sonuc.hatalar)
    return (f"{duzeltme_basligi(onay_no)} (uygulamanın otomatik kontrolü):\n{satirlar}\n"
            "Yalnızca değişen kısımları <yama> ile ver; dosyayı baştan yazma.")


# --- Aşama 5: sahne paketi --------------------------------------------------------

_YAS = re.compile(r"\b\d+[- ]?(year|yr)s?[- ]old\b", re.I)


def _yasak_deseni() -> re.Pattern | None:
    y = [x for x in kanal.ayar()["gorsel"]["yasakli"] if x.strip()]
    return re.compile(r"\b(" + "|".join(re.escape(x) for x in sorted(y, key=len, reverse=True)) + r")\b", re.I) if y else None


def izinli_olumsuz() -> tuple[str, ...]:
    return tuple(x.strip().lower() for x in kanal.ayar()["gorsel"]["izinli_olumsuz"] if x.strip())


def bloklar(metin: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", metin.replace("\r\n", "\n").strip()) if b.strip()]


def tsv_satirlari(tsv: str) -> list[str]:
    return [s for s in tsv.replace("\r\n", "\n").split("\n") if s.strip()]


def _flow_guvenligi(adlar_metinler: list[tuple[str, str]]) -> list[str]:
    hatalar, yasak, izinli = [], _yasak_deseni(), izinli_olumsuz()
    for yer, p in adlar_metinler:
        bulunan = sorted({m.lower() for m in yasak.findall(p)}) if yasak else []
        if bulunan:
            hatalar.append(f"{yer}: yasaklı kelime {', '.join(bulunan)}")
        if _YAS.search(p):
            hatalar.append(f"{yer}: yaş ifadesi var")
        for m in re.finditer(r"\bno\s+([a-z]+(?:\s[a-z]+)?)", p, re.I):
            if not izinli or not m.group(1).lower().startswith(izinli):
                hatalar.append(f"{yer}: izinsiz olumsuzlama «{m.group(0)}»")
        for m in re.finditer(r"\b(nothing|without|never)\b", p, re.I):
            hatalar.append(f"{yer}: izinsiz olumsuzlama «{m.group(0)}»")
    return list(dict.fromkeys(hatalar))


def sahne_paketi(a: str, b: str, c: str, d: str, it_final: str) -> Sonuc:
    """Sahne becerisi Adım 6 (plan_kontrol ayrıca çalışır). Kurallar kanal ayarından."""
    s = Sonuc()
    pa, pb, rows = bloklar(a), bloklar(b), tsv_satirlari(d)
    s.bilgiler.append(f"Sahne {len(pa)} · Prompt {len(pb)} · Plan satırı {max(0, len(rows) - 1)}")
    if not (len(pa) == len(pb) == len(rows) - 1):
        s.hatalar.append(f"Sayılar eşit değil: A {len(pa)} paragraf, B {len(pb)} prompt, D {len(rows) - 1} satır (başlık hariç).")
    beklenen_baslik = "sahne\tbolum\trol\tduygu\thareket\todak\tefekt\tsonraki_gecis\tmaskot\tgerekce"
    if rows and rows[0].strip() != beklenen_baslik:
        s.hatalar.append("D başlık satırı beklenen sütunlarla aynı değil: " + beklenen_baslik.replace("\t", " · "))
    # Tag kuralları
    izinli, sinir, say = izinli_tag(), tag_sinirlari(), {}
    tagli, onceki = 0, None
    for i, p in enumerate(pa, 1):
        taglar = re.findall(r"\[([^\]]+)\]", p)
        if taglar:
            tagli += 1
            for t in taglar:
                if t.strip().lower() not in izinli:
                    s.hatalar.append(f"A ¶{i}: izinsiz tag [{t}]")
            if len(taglar) > 1:
                s.hatalar.append(f"A ¶{i}: paragrafta birden fazla tag")
            if not p.startswith("["):
                s.hatalar.append(f"A ¶{i}: tag paragrafın başında değil")
            for t in taglar:
                say[t.strip().lower()] = say.get(t.strip().lower(), 0) + 1
            if onceki == taglar[0] and i < len(pa):
                s.uyarilar.append(f"A ¶{i}: aynı tag art arda ([{taglar[0]}])")
            onceki = taglar[0]
        else:
            onceki = None
    oran = 100 * tagli / max(1, len(pa))
    s.bilgiler.append(f"Tag %{oran:.1f}")
    ust = float(kanal.ayar()["etiketler"]["tag_orani"])
    if oran > ust:
        s.hatalar.append(f"Tag'li paragraf oranı %{oran:.1f}; üst sınır %{ust:g}.")
    for t, n in sinir.items():
        if say.get(t, 0) > n:
            s.hatalar.append(f"[{t}] {say[t]} kez; en fazla {n}.")
    if re.search(r"<\s*break|<\s*speak|<\s*prosody", a, re.I):
        s.hatalar.append("A'da <break>/SSML var; duraklama noktalamayla yapılmalı.")
    if re.search(r"\[(" + "|".join(re.escape(x) for x in senaryo_etiketleri()) + r")\]", a):
        s.hatalar.append(f"A'da senaryo etiketi kalmış ({_etiket_metni()}).")
    # Metin birebir
    ga = M.govde(" ".join(pa)).split()
    gi = M.govde(" ".join(M.ayir(it_final).paragraflar)).split()
    if ga != gi:
        fark = next((i for i, (x, y) in enumerate(zip(ga, gi)) if x != y), min(len(ga), len(gi)))
        s.hatalar.append(f"A metni (tag'siz) final metinle birebir değil: {fark + 1}. kelimede ayrılıyor "
                         f"(A: «{' '.join(ga[fark:fark + 6])}» / final: «{' '.join(gi[fark:fark + 6])}»).")
    # Flow güvenliği (B ve C)
    s.hatalar += _flow_guvenligi([(f"B {i:04d}", p) for i, p in enumerate(pb, 1)])
    s.hatalar += _flow_guvenligi([(f"C satır {i}", l) for i, l in enumerate(c.splitlines(), 1) if "→" in l])
    kar = kanal.ayar()["gorsel"]["karakter"]
    if kar:
        yanlis = [i for i, p in enumerate(pb, 1) if kar in p and not p.startswith(kar)]
        if yanlis:
            s.uyarilar.append(f"B: {kar} promptun başında değil: " + ", ".join(f"{i:04d}" for i in yanlis[:10]))
    return s


def paket(paket_md: str) -> Sonuc:
    s = Sonuc()
    if "DEFTER KAYDI" not in paket_md:
        s.hatalar.append("Paket dosyasında '5. DEFTER KAYDI' bloğu yok.")
    # Hashtag satırı: en çok etiket içeren satır (renk kodları #F7F0E1 sayılmaz).
    etiketler = lambda l: [t for t in re.findall(r"(?<!\w)#\w+", l) if not re.fullmatch(r"#[0-9A-Fa-f]{6}", t)]
    etiket_satiri = max(paket_md.splitlines() or [""], key=lambda l: len(etiketler(l)))
    n = len(etiketler(etiket_satiri))
    if n and n != 5:
        s.uyarilar.append(f"Hashtag sayısı {n}; tam 5 olmalı.")
    _kanal_etiketi(paket_md, s)
    return s


def _kanal_etiketi(metin: str, s: Sonuc) -> None:
    etiket = "#" + re.sub(r"\W", "", kanal.ayar()["ad"])
    if len(etiket) > 1 and etiket.lower() not in metin.lower():
        s.uyarilar.append(f"{etiket} etiketi bulunamadı.")


def duzeltme_basligi(onay_no: int | None) -> str:
    return f"ONAY {onay_no} değil, düzeltme" if onay_no else "Düzeltme"


def aciklama_final(final_md: str, zamanlar: list[str]) -> Sonuc:
    """Aşama 6 Mesaj 2: verilen zaman damgaları aynen ve sırayla yer almalı (değiştirilmez, yuvarlanmaz)."""
    s = Sonuc()
    bulunan = re.findall(r"(?m)^\W*(\d{1,2}:\d{2})\b", final_md)
    s.bilgiler.append(f"Bölüm {len(bulunan)}")
    if zamanlar and bulunan != zamanlar:
        s.hatalar.append("Bölüm zaman damgaları verilenlerle birebir ve aynı sırada değil. Beklenen: "
                         + ", ".join(zamanlar) + " · Bulunan: " + (", ".join(bulunan) or "yok"))
    if zamanlar and zamanlar[0] != "0:00":
        s.uyarilar.append("İlk bölüm 0:00'da başlamıyor (YouTube şartı).")
    if 0 < len(zamanlar) < 3:
        s.uyarilar.append("3'ten az bölüm var (YouTube en az 3 ister).")
    sn = [int(z.split(":")[0]) * 60 + int(z.split(":")[1]) for z in zamanlar]
    kisa = [zamanlar[i] for i in range(len(sn) - 1) if sn[i + 1] - sn[i] < 10]
    if kisa:
        s.uyarilar.append("10 saniyeden kısa bölüm: " + ", ".join(kisa))
    _kanal_etiketi(final_md, s)
    return s
```

### `app/kanal_studyosu/llm.py`

```python
"""Model katmanı. Yazım servisi: Claude Code (abonelik, varsayılan; claude_code.py) ya da OpenRouter.

Claude Code seçiliyse istek claude_code.py'ye gider (ücret abonelikten; maliyet kaydına yalnız tahmini tutar
bilgi olarak yazılır, bütçe sınırı uygulanmaz). Aşağıdaki maddeler OpenRouter (Anthropic Messages biçimi) içindir.
Doğrudan Anthropic API seçeneği 22 Eki 2026'da kaldırıldı; "anthropic" yolu yalnız testlerde sahte istemciyle kullanılır.

- Model, efor, araçlar ve token sınırı iş bazında ayar dosyasından gelir.
- Sistem öneki (proje dosyaları 00–02 + aşama becerisi + uygulama çerçevesi + KANAL AYARLARI) önbelleğe alınır.
- Akış (streaming) ile alınır; ilerleme geri çağrısıyla arayüze karakter sayısı gider.
- Web arama sunucu aracıdır; pause_turn gelirse konuşma otomatik sürdürülür.
- Sonnet/Opus'ta sunucu tarafı yedek model (fallbacks="default") açıktır.
- Geçici hatalarda üstel bekleme: 2, 4, 8, 16, 32 sn.
- Sağlayıcı "openrouter" ise aynı istek OpenRouter'ın Anthropic uyumlu girişine gider: model adı eşlenir,
  sunucu tarafı yedek model (Anthropic'e özgü) gönderilmez; OpenRouter bir alanı kabul etmezse (400) o alan
  çıkarılıp yeniden denenir (sırasıyla efor, web arama) ve kayda yazılır.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Callable

from . import ayarlar as A
from . import kayit
from . import maliyet

YEDEK_BETA = "server-side-fallback-2026-07-01"
BEKLEMELER = (2, 4, 8, 16, 32)
DEVAM_SINIRI = 5


class LLMHatasi(Exception):
    """Kullanıcıya gösterilecek kısa Türkçe mesaj taşır."""


class Reddedildi(LLMHatasi):
    pass


class Durduruldu(LLMHatasi):
    """Kullanıcı Durdur'a bastı."""


@dataclass
class Cevap:
    metin: str
    icerik: list[dict]          # konuşma geçmişine aynen eklenecek asistan blokları (düşünme dahil)
    kullanim: dict
    model: str
    usd: float
    yedek_model: str = ""       # yedek model devreye girdiyse adı
    ek_mesajlar: list[dict] = field(default_factory=list)  # pause_turn ile oluşan ara asistan turları


def _blok_sozluk(b) -> dict:
    return b.model_dump(mode="json", exclude_none=True) if hasattr(b, "model_dump") else dict(b)


def _kullanim(u) -> dict:
    d = {k: getattr(u, k, 0) or 0 for k in
         ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
    stu = getattr(u, "server_tool_use", None)
    d["web_search_requests"] = getattr(stu, "web_search_requests", 0) or 0 if stu else 0
    its = getattr(u, "iterations", None)
    if its:
        d["iterations"] = [_blok_sozluk(i) for i in its]
    return d


def _normal(ad: str) -> str:
    """anthropic/claude-sonnet-5.5 → claude-sonnet-5-5 (OpenRouter adları yedek model sanılmasın)."""
    return re.sub(r"\[.*?\]|:.*$", "", str(ad).split("/", 1)[-1]).replace(".", "-").lower()


def dusunceleri_cikar(mesajlar: list[dict]) -> list[dict]:
    """Asistan turlarındaki düşünme bloklarını ve Claude Code oturum işaretlerini çıkarır. Düşünme imzaları onu
    üreten servise bağlıdır; yazım servisi değişince eski imzalar reddedilebilir. Yazılan metinler aynen kalır."""
    yeni = []
    for m in mesajlar:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            m = dict(m, content=[{k: v for k, v in b.items() if k != "oturum"} for b in m["content"]
                                 if b.get("type") not in ("thinking", "redacted_thinking")]
                     or [{"type": "text", "text": "(boş)"}])
        yeni.append(m)
    return yeni


def _topla(a: dict, b: dict) -> dict:
    s = dict(a)
    for k, v in b.items():
        if k == "iterations":
            s["iterations"] = (s.get("iterations") or []) + v
        else:
            s[k] = s.get(k, 0) + v
    return s


def saglayici() -> str:
    return "openrouter" if A.ayarlar().get("saglayici") == "openrouter" else "claude_code"


SAGLAYICI_ADI = {"anthropic": "Anthropic", "openrouter": "OpenRouter", "claude_code": "Claude Code"}
_YONELME = {"anthropic": "Anthropic'e", "openrouter": "OpenRouter'a", "claude_code": "Claude Code'a"}
# OpenRouter bir alanı reddederse çıkarılacak alanlar (sırayla). Yazım sonucu değişmez; yalnız efor/araştırma etkilenir.
AYIKLANABILIR = ("output_config", "tools")


class LLM:
    def __init__(self, istemci=None, saglayici_: str | None = None):
        self._verilen = istemci          # testler için sabit istemci
        self._sabit = saglayici_
        self._istemciler: dict = {}
        self._ayiklanan: set[str] = set()

    @property
    def saglayici(self) -> str:
        """Ayarlardan her istekte okunur: Ayarlar'da değiştirilirse çalışan üretim de sonraki adımda geçer.
        Sahte istemci verilmişse (testler) Anthropic biçimli yol kullanılır."""
        if self._sabit:
            return self._sabit
        s = saglayici()
        return "anthropic" if self._verilen is not None and s == "claude_code" else s

    @property
    def istemci(self):
        if self._verilen is not None:
            return self._verilen
        if self.saglayici not in self._istemciler:
            import anthropic
            if self.saglayici == "openrouter":
                from . import openrouter
                anahtar = A.anahtar("openrouter")
                if not anahtar:
                    raise LLMHatasi("OpenRouter anahtarı kayıtlı değil. Ayarlar'dan ekle.")
                self._istemciler["openrouter"] = openrouter.istemci(anahtar)
            else:
                raise LLMHatasi("Bu yazım servisi istemci kullanmaz.")
        return self._istemciler[self.saglayici]

    def _gonderim(self, p: dict) -> dict:
        """Uygulama parametreleri → sağlayıcıya giden istek."""
        if self.saglayici != "openrouter":
            return p
        from . import openrouter
        g = {k: v for k, v in p.items() if k not in ("betas", "fallbacks") and k not in self._ayiklanan}
        g["model"] = openrouter.model_eslestir(p["model"])
        return g

    def parametreler(self, is_adi: str, sistem: list[str], mesajlar: list[dict]) -> dict:
        ayar = A.ayarlar()
        isa = ayar["isler"][is_adi]
        mod = ayar["modeller"][isa["model"]]
        onbellek = {"type": "ephemeral"}
        if ayar["onbellek_suresi"] == "1h":
            onbellek["ttl"] = "1h"
        sistem_bloklari = [{"type": "text", "text": t} for t in sistem if t]
        if sistem_bloklari:
            sistem_bloklari[-1]["cache_control"] = onbellek
        # İki önbellek noktası: sabit sistem öneki ve (düzeltme turları için) konuşmanın son bloğu.
        p = {"model": isa["model"], "max_tokens": isa["max_token"], "system": sistem_bloklari,
             "messages": mesajlar, "cache_control": dict(onbellek)}
        if not sistem_bloklari:
            del p["system"]
        if mod["efor"] and isa.get("efor"):
            p["output_config"] = {"effort": isa["efor"]}
        if isa.get("web_arama"):
            p["tools"] = [{"type": "web_search_20260209", "name": "web_search", "max_uses": int(isa["web_arama"])}]
        if mod.get("yedek_model") and self.saglayici == "anthropic":
            p["betas"] = [YEDEK_BETA]
            p["fallbacks"] = "default"
        return p

    def tahmin_usd(self, p: dict) -> float:
        """Çağrıdan önce kaba maliyet: giriş token sayımı (ücretsiz uç nokta) + beklenen çıkış."""
        ayar = A.ayarlar()
        f = ayar["modeller"][p["model"]]
        try:
            if self.saglayici != "anthropic":  # sayım uç noktası Anthropic'e özgü
                raise LookupError("sayım yok")
            sayim = {k: p[k] for k in ("model", "system", "messages", "tools") if k in p}
            giris = self.istemci.beta.messages.count_tokens(**sayim).input_tokens
        except Exception as e:  # sayım başarısızsa karakterden tahmin
            if not isinstance(e, LookupError):
                kayit.yaz(f"Token sayımı yapılamadı ({type(e).__name__}); karakterden tahmin ediliyor", "uyari")
            giris = (len(str(p.get("system", ""))) + len(str(p["messages"]))) // 3
        cikis = min(p["max_tokens"], 16000)
        arama = len(p.get("tools") or []) and p["tools"][0].get("max_uses", 0)
        return (giris * f["giris"] + cikis * f["cikis"]) / 1_000_000 + arama * ayar["web_arama_1000_usd"] / 1000

    def istek(self, is_adi: str, video: str, sistem: list[str], mesajlar: list[dict],
              ilerleme: Callable[[int], None] | None = None, butce_onayli: bool = False,
              iptal: Callable[[], bool] | None = None, tur: str = "ilk") -> Cevap:
        if self.saglayici == "claude_code":
            return self._claude_code(is_adi, video, sistem, mesajlar, ilerleme, iptal, tur)
        p = self.parametreler(is_adi, sistem, mesajlar)
        if not butce_onayli:
            maliyet.butce_kontrol(video, self.tahmin_usd(p))
        model = p["model"]
        kullanim: dict = {}
        ara_turlar: list[dict] = []
        metin_parcalari: list[str] = []
        mesajlar_simdi = list(mesajlar)
        yedek = ""
        for devam in range(DEVAM_SINIRI + 1):
            son = self._akis(dict(p, messages=mesajlar_simdi), ilerleme, sum(map(len, metin_parcalari)), iptal)
            kullanim = _topla(kullanim, _kullanim(son.usage))
            bloklar = [_blok_sozluk(b) for b in son.content]
            metin_parcalari += [b.get("text", "") for b in bloklar if b.get("type") == "text"]
            sunulan = getattr(son, "model", model) or model
            # Yedek model yalnız Anthropic'te var; OpenRouter cevapta "unknown" gibi adlar döndürebiliyor.
            if self.saglayici == "anthropic" and sunulan != model and _normal(sunulan) != model:
                yedek = sunulan
            if son.stop_reason in ("refusal", "max_tokens"):
                # Başarısız cevabın da ücreti ödendi: bütçeye ve maliyet kaydına yazılır.
                ayar = A.ayarlar()
                usd = maliyet.hesapla(kullanim, model, ayar, ayar["onbellek_suresi"])
                maliyet.kaydet(video, is_adi, yedek or model, kullanim, usd, tur, son.stop_reason)
                kayit.yaz(f"{is_adi}: {son.stop_reason} · çıkış {kullanim['output_tokens']} · {usd:.4f} $ (kullanılamadı)",
                          "uyari")
            if son.stop_reason == "refusal":
                raise Reddedildi("Model bu adımı yazmayı reddetti (güvenlik). Konu ya da not yumuşatılarak tekrar denenebilir.")
            if son.stop_reason == "max_tokens":
                raise LLMHatasi(f"Cevap çok uzadı ve {p['max_tokens']:,} token sınırında kesildi; yarım metin kullanılamadığı "
                                "için kaydedilmedi. Harcanan tutar bütçeye yazıldı. Tekrar dene bu adımı baştan yazar.".replace(",", "."))
            if son.stop_reason == "pause_turn" and devam < DEVAM_SINIRI:
                ara_turlar.append({"role": "assistant", "content": bloklar})
                mesajlar_simdi = mesajlar_simdi + [ara_turlar[-1]]
                kayit.yaz(f"{is_adi}: web araması sürüyor, konuşma devam ettiriliyor")
                continue
            ayar = A.ayarlar()
            if "tools" in self._ayiklanan and p.get("tools"):
                kayit.yaz(f"{is_adi}: web araması bu sağlayıcıda çalışmadı; araştırma modelin kendi bilgisiyle yapıldı",
                          "uyari")
            usd = maliyet.hesapla(kullanim, model, ayar, ayar["onbellek_suresi"])
            maliyet.kaydet(video, is_adi, yedek or model, kullanim, usd, tur)
            kayit.yaz(f"{is_adi}: {model}{' → ' + yedek if yedek else ''} · giriş {kullanim['input_tokens']} "
                      f"· önbellek okuma {kullanim['cache_read_input_tokens']} · çıkış {kullanim['output_tokens']} "
                      f"· arama {kullanim['web_search_requests']} · {usd:.4f} $")
            return Cevap("".join(metin_parcalari), bloklar, kullanim, model, usd, yedek, ara_turlar)
        raise LLMHatasi("Web araması çok uzun sürdü; adım tekrar denenebilir.")

    def _claude_code(self, is_adi, video, sistem, mesajlar, ilerleme, iptal, tur) -> Cevap:
        from . import claude_code
        try:
            r = claude_code.istek(is_adi, sistem, mesajlar, ilerleme=ilerleme, iptal=iptal)
        except claude_code.ClaudeCodeHatasi as e:
            raise LLMHatasi(str(e))
        k = r["kullanim"]
        maliyet.kaydet(video, is_adi, r["model"], k, 0.0, tur, abonelik=True, tahmini_usd=r["tahmini_usd"])
        kayit.yaz(f"{is_adi}: Claude Code · {r['model']} · giriş {k['input_tokens']} · önbellek okuma "
                  f"{k['cache_read_input_tokens']} · çıkış {k['output_tokens']} · arama {k['web_search_requests']} "
                  f"· abonelik (API karşılığı ~{r['tahmini_usd']:.2f} $)")
        # Oturum kimliği asistan bloğunda saklanır: düzeltme turunda aynı Claude Code oturumu sürdürülür.
        blok = {"type": "text", "text": r["metin"] or "(boş)", "oturum": r["oturum"]}
        return Cevap(r["metin"], [blok], k, r["model"], 0.0)

    def _akis(self, p: dict, ilerleme, onceki: int, iptal=None):
        import anthropic
        ad, ada = SAGLAYICI_ADI[self.saglayici], _YONELME[self.saglayici]
        beklemeler = list(BEKLEMELER) + [None]
        while beklemeler:
            bekle = beklemeler[0]
            try:
                yazilan = onceki
                with self.istemci.beta.messages.stream(**self._gonderim(p)) as akis:
                    for olay in akis:
                        if iptal and iptal():
                            # Akış kapatılır; o ana kadar yazılan kısmın ücreti sağlayıcıda işlenmiş olur.
                            raise Durduruldu("Durduruldu. Tekrar dene ile bu adım baştan yazılır.")
                        if getattr(olay, "type", "") == "content_block_delta" and \
                                getattr(olay.delta, "type", "") == "text_delta":
                            yazilan += len(olay.delta.text)
                            if ilerleme:
                                ilerleme(yazilan)
                    return akis.get_final_message()
            except anthropic.AuthenticationError:
                raise LLMHatasi(f"{ad} anahtarı geçersiz. Ayarlar'dan yeni anahtar gir.")
            except anthropic.PermissionDeniedError as e:
                kayit.yaz(f"403: {e.message}", "hata")
                raise LLMHatasi(f"{ad} hesabı bu işlem için yetkili değil (kredi ya da izin). Ayrıntı kayıt panelinde.")
            except anthropic.BadRequestError as e:
                kayit.yaz(f"400: {e.message}", "hata")
                kalan = [k for k in AYIKLANABILIR if k in p and k not in self._ayiklanan]
                if self.saglayici == "openrouter" and kalan:
                    self._ayiklanan.add(kalan[0])
                    kayit.yaz(f"OpenRouter '{kalan[0]}' alanını kabul etmedi; o alan olmadan yeniden deneniyor", "uyari")
                    continue
                raise LLMHatasi("İstek kabul edilmedi. Ayrıntı kayıt panelinde.")
            except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
                if bekle is None:
                    raise LLMHatasi(f"{ada} şu an ulaşılamıyor ya da yoğun. Biraz sonra Tekrar dene.")
                kayit.yaz(f"Geçici hata ({type(e).__name__}); {bekle} sn sonra tekrar denenecek", "uyari")
                beklemeler.pop(0)
                time.sleep(bekle)
            except anthropic.APIStatusError as e:
                if e.status_code >= 500 and bekle is not None:
                    kayit.yaz(f"Sunucu hatası {e.status_code}; {bekle} sn sonra tekrar", "uyari")
                    beklemeler.pop(0)
                    time.sleep(bekle)
                    continue
                kayit.yaz(f"API hatası {e.status_code}: {e.message}", "hata")
                if e.status_code == 402:
                    raise LLMHatasi(f"{ad} kredisi yetersiz. Hesabına kredi yükleyip Tekrar dene.")
                raise LLMHatasi(f"{ad} bir hata döndürdü. Ayrıntı kayıt panelinde.")
        raise LLMHatasi(f"{ada} şu an ulaşılamıyor ya da yoğun. Biraz sonra Tekrar dene.")
```

### `app/kanal_studyosu/maliyet.py`

```python
"""Token ve tahmini $ sayacı, bütçe sınırı.

Her API çağrısı Sistem/maliyet.jsonl'ye (kanal alanıyla; aylık bütçe bütün kanallar için ortak) bir satır olarak eklenir (video ve iş bazında).
Fiyatlar ayar dosyasındadır ($ / 1M token). Önbelleğe yazma: 5 dk için girişin
1,25 katı, 1 saat için 2 katı.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import ayarlar as A
from . import yollar


def _fiyat(model: str, ayar: dict) -> dict:
    return ayar["modeller"].get(model) or ayar["modeller"][max(
        ayar["modeller"], key=lambda m: ayar["modeller"][m]["cikis"])]  # bilinmeyen model: en pahalı varsayılır


def hesapla(kullanim: dict, model: str, ayar: dict, onbellek_suresi: str = "5m") -> float:
    """kullanim: input_tokens, output_tokens, cache_creation_input_tokens,
    cache_read_input_tokens, web_search_requests, iterations (yedek model devreye girdiyse)."""
    yazma_katsayi = 2.0 if onbellek_suresi == "1h" else 1.25
    parcalar = kullanim.get("iterations") or [dict(kullanim, model=model)]
    toplam = 0.0
    for p in parcalar:
        f = _fiyat(p.get("model") or model, ayar)
        toplam += (p.get("input_tokens", 0) * f["giris"]
                   + p.get("cache_creation_input_tokens", 0) * f["giris"] * yazma_katsayi
                   + p.get("cache_read_input_tokens", 0) * f["onbellek_okuma"]
                   + p.get("output_tokens", 0) * f["cikis"]) / 1_000_000
    toplam += kullanim.get("web_search_requests", 0) * ayar["web_arama_1000_usd"] / 1000
    return round(toplam, 6)


TUR_ADI = {"ilk": "İlk yazım", "oto": "Otomatik düzeltme", "kullanici": "Senin düzeltmen", "tekrar": "Tekrar dene",
           "kesildi": "Kesilen / reddedilen", "": "Ayrılmamış (eski kayıt)"}


def kaydet(video: str, is_adi: str, model: str, kullanim: dict, usd: float, tur: str = "ilk",
           sonuc: str = "", abonelik: bool = False, tahmini_usd: float = 0.0) -> dict:
    """tur: ilk | oto_duzeltme_N | kullanici_duzeltme | tekrar. sonuc: '' ya da max_tokens/refusal (ücret ödendi,
    cevap kullanılamadı). abonelik: Claude Code (usd 0, bütçeye sayılmaz; tahmini_usd yalnız bilgi)."""
    from . import kanallar
    satir = {"zaman": datetime.now(timezone.utc).isoformat(), "kanal": kanallar.aktif() or "", "video": video,
             "is": is_adi, "model": model,
             "usd": usd, "tur": tur, **({"sonuc": sonuc} if sonuc else {}),
             **({"abonelik": True, "tahmini_usd": round(tahmini_usd, 4)} if abonelik else {}),
             **{k: v for k, v in kullanim.items() if k != "iterations"}}
    yollar.maliyet_dosyasi().parent.mkdir(parents=True, exist_ok=True)
    with open(yollar.maliyet_dosyasi(), "a", encoding="utf-8") as f:
        f.write(json.dumps(satir, ensure_ascii=False) + "\n")
    return satir


def satirlar() -> list[dict]:
    try:
        with open(yollar.maliyet_dosyasi(), encoding="utf-8") as f:
            return [json.loads(s) for s in f if s.strip()]
    except FileNotFoundError:
        return []


def ozet(video: str | None = None) -> dict:
    ay = datetime.now(timezone.utc).strftime("%Y-%m")
    tum = satirlar()
    ay_top = sum(s["usd"] for s in tum if s["zaman"].startswith(ay))
    vid = [s for s in tum if video and s["video"] == video]
    asama: dict[str, float] = {}
    for s in vid:
        asama[s["is"]] = asama.get(s["is"], 0) + s["usd"]
    ayar = A.ayarlar()
    return {"abonelik_tahmini_usd": round(sum(s.get("tahmini_usd", 0) for s in vid), 2),
            "abonelik": any(s.get("abonelik") for s in vid),
            "ay_usd": round(ay_top, 4), "ay_sinir": ayar["butce"]["aylik_usd"],
            "video_usd": round(sum(s["usd"] for s in vid), 4), "video_sinir": ayar["butce"]["video_usd"],
            "asamalar": {k: round(v, 4) for k, v in asama.items()}}


class ButceAsimi(Exception):
    pass


def butce_kontrol(video: str, tahmini_usd: float) -> None:
    """Çağrı yapılmadan önce: sınır aşılacaksa ButceAsimi (kullanıcıya sorulur)."""
    o = ozet(video)
    if o["video_usd"] + tahmini_usd > o["video_sinir"]:
        raise ButceAsimi(f"Bu video için bütçe sınırına geldik: harcanan {o['video_usd']:.2f} $, "
                         f"bu adım tahminen {tahmini_usd:.2f} $, sınır {o['video_sinir']:.0f} $.")
    if o["ay_usd"] + tahmini_usd > o["ay_sinir"]:
        raise ButceAsimi(f"Bu ayın bütçe sınırına geldik: harcanan {o['ay_usd']:.2f} $, "
                         f"bu adım tahminen {tahmini_usd:.2f} $, sınır {o['ay_sinir']:.0f} $.")


def _sutun(s: dict) -> str:
    if s.get("sonuc"):
        return "kesildi"
    t = s.get("tur", "")
    return "oto" if t.startswith("oto") else "kullanici" if t.startswith("kullanici") else t


def dokum(video: str) -> str:
    """Video için ayrıntılı maliyet dökümü (Markdown): aşama × tür tablosu ve istek istek liste."""
    vid = [s for s in satirlar() if s.get("video") == video]
    sutunlar = ["ilk", "oto", "kullanici", "tekrar", "kesildi"] + (["" ] if any("tur" not in s for s in vid) else [])
    tablo: dict[str, dict[str, list]] = {}
    for s in vid:
        is_ = s["is"].replace("_yedek", "")
        tablo.setdefault(is_, {}).setdefault(_sutun(s), []).append(s["usd"])
    hucre = lambda l: f"{sum(l):.2f} $ ({len(l)})" if l else "—"
    st = [f"# {video} · Maliyet dökümü (tahmini, API)", "",
          "| İş | " + " | ".join(TUR_ADI[c] for c in sutunlar) + " | Toplam |",
          "|---|" + "---|" * (len(sutunlar) + 1)]
    for is_, d in tablo.items():
        st.append(f"| {is_} | " + " | ".join(hucre(d.get(c, [])) for c in sutunlar) +
                  f" | **{sum(sum(v) for v in d.values()):.2f} $** |")
    st.append("| **Toplam** | " + " | ".join(hucre([u for d in tablo.values() for u in d.get(c, [])])
                                            for c in sutunlar) + f" | **{sum(s['usd'] for s in vid):.2f} $** |")
    st += ["", "Parantez içi: istek sayısı. Kesilen / reddedilen: ücreti ödenen ama kullanılamayan cevap.",
           "Kesin tutar için sağlayıcının panelindeki kullanım geçmişine bak."]
    if any(s.get("abonelik") for s in vid):
        st += ["", f"Claude Code (abonelik) istekleri 0 $ sayılır; API'yle olsaydı tahmini karşılığı "
                   f"~{sum(s.get('tahmini_usd', 0) for s in vid):.2f} $ (yalnız bilgi)."]
    st += ["", "## İstek istek",
           "| Saat (UTC) | İş | Tür | Model | Giriş | Önbellek okuma | Çıkış | Arama | $ |", "|---|---|---|---|---|---|---|---|---|"]
    for s in vid:
        tur = (s.get("tur") or "?") + (f" · {s['sonuc']}" if s.get("sonuc") else "")
        st.append((f"| {s['zaman'][5:16].replace('T', ' ')} | {s['is']} | {tur} | {s.get('model', '')} | "
                  f"{s.get('input_tokens', 0) + s.get('cache_creation_input_tokens', 0):,} | "
                  f"{s.get('cache_read_input_tokens', 0):,} | {s.get('output_tokens', 0):,} | "
                  f"{s.get('web_search_requests', 0)} | "
                  + (f"abonelik (~{s.get('tahmini_usd', 0):.2f})" if s.get("abonelik") else f"{s['usd']:.4f}")
                  + " |").replace(",", "."))
    return "\n".join(st) + "\n"
```

### `app/kanal_studyosu/metin.py`

```python
"""Senaryo metinleri: paragraf ayrıştırma, kelime sayımı, mekanik yama.

Paragraf = boş satırla ayrılan blok. Etiket satırı ([MIRA] [★30sn]) paragrafın
parçasıdır. Dosya sonundaki teslim satırları ("Parole: …", "Kelime: …" ile
başlayan kuyruk) paragraf sayılmaz.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

ETIKET = re.compile(r"\[[^\]\n]{1,40}\]")
# "Açık noktalar" satırı dosyaya düşerse de konuşma metni sayılmaz (seslendirmeye/sahnelere gitmez).
KUYRUK_BASI = re.compile(r"^\s*\**\s*(Parole|Kelime|Paragrafi|Paragraf|Words|Açık noktalar)\s*\**\s*:"
                         r"|^\s*\**\s*[\wÀ-ÿ]+\s*\**\s*:\s*\**\s*\d{3,5}\b", re.IGNORECASE)
# Teslim satırındaki kelime sayısı (dil fark etmez): "Parole: 2003 · Paragrafi: 71", "Words: 1980", "Kelime: 1720"
KELIME_SATIRI = re.compile(r"(?m)^\s*\**\s*[\wÀ-ÿ]+\s*\**\s*:\s*\**\s*\d{3,5}\b")


@dataclass
class Senaryo:
    paragraflar: list[str]
    kuyruk: str  # teslim satırları (boş olabilir)

    def metin(self) -> str:
        govde = "\n\n".join(self.paragraflar)
        return govde + ("\n\n" + self.kuyruk if self.kuyruk else "") + "\n"


def ayir(metin: str) -> Senaryo:
    satirlar = metin.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    kuyruk = ""
    for i, s in enumerate(satirlar):
        if KUYRUK_BASI.match(s):
            kuyruk = "\n".join(satirlar[i:]).strip()
            satirlar = satirlar[:i]
            break
    bloklar = [b.strip() for b in re.split(r"\n\s*\n", "\n".join(satirlar)) if b.strip()]
    return Senaryo(bloklar, kuyruk)


def govde(paragraf: str) -> str:
    """Etiketsiz, tek boşluklu konuşma metni."""
    return " ".join(ETIKET.sub(" ", paragraf).split())


def kelime_sayisi(metin_ya_da_paragraflar) -> int:
    if isinstance(metin_ya_da_paragraflar, str):
        paragraflar = ayir(metin_ya_da_paragraflar).paragraflar
    else:
        paragraflar = metin_ya_da_paragraflar
    return sum(len([w for w in govde(p).split() if re.search(r"\w", w)]) for p in paragraflar)


# --- Mekanik yama -----------------------------------------------------------
# Model düzeltme turunda yalnızca değişen kısımları verir. Kod bunları
# numarasıyla/anahtarıyla birebir yerine koyar; içerik üretmez.

class YamaHatasi(ValueError):
    pass


def yama_uygula(metin: str, yamalar: list[dict]) -> str:
    """yamalar: {'paragraf': N, 'islem': 'degistir'|'sil'|'sonrasina_ekle', 'icerik': …}
    ya da {'satir': 'Başlık', 'icerik': …} ya da {'bolum': '§4', 'icerik': …}
    ya da {'kuyruk': True, 'icerik': …}. Paragraf numaraları yamadan önceki dosyaya göredir."""
    paragraf_yamalari = [y for y in yamalar if "paragraf" in y]
    diger = [y for y in yamalar if "paragraf" not in y]
    for y in diger:
        if y.get("kuyruk"):
            s = ayir(metin)
            s.kuyruk = y["icerik"].strip()
            metin = s.metin()
        elif "satir" in y:
            metin = _satir_degistir(metin, y["satir"], y["icerik"])
        elif "bolum" in y:
            metin = _bolum_degistir(metin, y["bolum"], y["icerik"])
        else:
            raise YamaHatasi("Tanınmayan yama")
    if paragraf_yamalari:
        s = ayir(metin)
        n = len(s.paragraflar)
        for y in paragraf_yamalari:
            if not 1 <= int(y["paragraf"]) <= n:
                raise YamaHatasi(f"¶{y['paragraf']} yok (dosyada {n} paragraf var)")
        # Önce yerinde değişiklikler (numara kaymaz), sonra silme/ekleme sondan başa.
        for y in paragraf_yamalari:
            if y.get("islem", "degistir") == "degistir":
                s.paragraflar[int(y["paragraf"]) - 1] = y["icerik"].strip()
        for y in sorted((y for y in paragraf_yamalari if y.get("islem", "degistir") != "degistir"),
                        key=lambda y: int(y["paragraf"]), reverse=True):
            i = int(y["paragraf"]) - 1
            if y["islem"] == "sil":
                del s.paragraflar[i]
            elif y["islem"] == "sonrasina_ekle":
                yeni = [b.strip() for b in re.split(r"\n\s*\n", y["icerik"].strip()) if b.strip()]
                s.paragraflar[i + 1:i + 1] = yeni
            else:
                raise YamaHatasi(f"Bilinmeyen işlem: {y['islem']}")
        metin = s.metin()
    return metin


def _satir_degistir(metin: str, anahtar: str, yeni: str) -> str:
    satirlar = metin.split("\n")
    for i, s in enumerate(satirlar):
        if s.strip().startswith(anahtar):
            satirlar[i] = yeni.strip()
            return "\n".join(satirlar)
    raise YamaHatasi(f"'{anahtar}' ile başlayan satır bulunamadı")


def _bolum_degistir(metin: str, baslik: str, yeni: str) -> str:
    satirlar = metin.split("\n")
    temiz = [s.lstrip("# ").strip() for s in satirlar]
    bas = next((i for i, s in enumerate(temiz)
                if s.startswith(baslik) and not s[len(baslik):len(baslik) + 1].isdigit()), None)
    if bas is None:
        raise YamaHatasi(f"'{baslik}' bölümü bulunamadı")
    bit = len(satirlar)
    for j in range(bas + 1, len(satirlar)):
        if temiz[j].startswith("§") or satirlar[j].startswith("#"):
            bit = j
            break
    return "\n".join(satirlar[:bas] + [yeni.strip()] + satirlar[bit:])
```

### `app/kanal_studyosu/onkontrol.py`

```python
"""Her açılışta genel ön kontrol (programlar, kurulum klasörü, anahtarlar) ve seçili kanalın üretime hazırlığı."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import ayarlar as A
from . import kanallar
from . import yollar


def program(ad: str) -> str | None:
    """Programın yolu. Windows'ta winget kurulumundan sonra PATH henüz yenilenmemiş olabilir: bilinen klasörlere de bakılır."""
    bulunan = shutil.which(ad)
    if bulunan:
        return bulunan
    yerel = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local")))
    adaylar = list((yerel / "Microsoft/WinGet/Links").glob(f"{ad}.exe"))
    for kok in (Path(os.environ.get("ProgramFiles", "C:/Program Files")), yerel / "Microsoft/WinGet/Packages"):
        adaylar += list(kok.glob(f"ImageMagick*/{ad}.exe")) + list(kok.glob(f"*FFmpeg*/**/bin/{ad}.exe"))
    return str(adaylar[0]) if adaylar else None


_program = program  # eski ad (üretim modülleri kullanır)


def _madde(ad: str, tamam: bool, mesaj: str, zorunlu: bool = True) -> dict:
    return {"ad": ad, "tamam": tamam, "mesaj": mesaj, "zorunlu": zorunlu}


def _pillow() -> bool:
    try:
        import PIL  # noqa: F401  (araçlar uygulamanın kendi Python ortamında çalışır)
        return True
    except ImportError:
        return False


def ai84_dogrula(anahtar: str = "") -> tuple[bool, str]:
    from .ai84 import AI84, AI84Hatasi
    anahtar = anahtar or A.anahtar("ai84")
    if not anahtar:
        return False, "AI84 anahtarı kayıtlı değil. Ayarlar'dan ekle."
    try:
        return True, f"AI84 anahtarı geçerli · {AI84(anahtar).krediler():,} kredi kaldı.".replace(",", ".")
    except AI84Hatasi as e:
        return False, str(e)


def calistir() -> dict:
    m = []
    m.append(_madde("Python", sys.version_info >= (3, 10), f"Python {sys.version.split()[0]}"))
    kok = yollar.kok()
    m.append(_madde("Kurulum klasörü", kok.is_dir() and os.access(kok, os.W_OK), str(kok)))
    eksik_prog = [p for p in ("ffmpeg", "ffprobe", "magick") if not program(p)]
    m.append(_madde("ffmpeg / ImageMagick", not eksik_prog,
                    "Hepsi kurulu." if not eksik_prog else "Eksik: " + ", ".join(eksik_prog) +
                    " ('1 - Ilk kurulum.cmd' dosyasını çalıştır; kurduktan sonra uygulamayı kapatıp yeniden aç)."))
    m.append(_madde("Pillow", _pillow(), "Kurulu" if _pillow() else "Maskot için gerekli. Uygulamayı yeniden aç (ilk açılışta kurulur).",
                    zorunlu=False))
    from .araclar import ARACLAR, araclar_klasoru
    eksik_arac = [x for x in ARACLAR if not (araclar_klasoru() / x).exists()]
    m.append(_madde("Montaj araçları", not eksik_arac, "Tam." if not eksik_arac else "Eksik: " + ", ".join(eksik_arac)))
    taslak = A.yol("capcut_taslak")
    tamam = taslak.is_dir() and os.access(taslak, os.W_OK)
    m.append(_madde("CapCut taslak klasörü", tamam, "Erişilebilir." if tamam else
                    f"{taslak} bulunamadı ya da yazılamıyor (CapCut kurulu mu? Ayarlar'dan yolu düzelt)."))
    if A.ayarlar().get("saglayici") == "openrouter":
        try:
            import anthropic  # noqa: F401
            m.append(_madde("OpenRouter kütüphanesi", True, "Kurulu"))
        except ImportError:
            m.append(_madde("OpenRouter kütüphanesi", False, "Kurulu değil. Uygulamayı .app ile yeniden aç (ilk açılışta kurulur)."))
        yazim = A.anahtar("openrouter")
        m.append(_madde("Yazım servisi: OpenRouter", bool(yazim),
                        "Anahtar kayıtlı." if yazim else "OpenRouter anahtarı kayıtlı değil. Ayarlar'dan ekle."))
    else:
        from . import claude_code
        ok, mesaj = claude_code.durum()
        m.append(_madde("Yazım servisi: Claude Code (abonelik)", ok, mesaj))
    m.append(_madde("Seslendirme anahtarı (AI84)", bool(A.anahtar("ai84")),
                    "kayıtlı" if A.anahtar("ai84") else "kayıtlı değil. Ayarlar'dan ekle."))
    akt = kanallar.aktif()
    if not akt:
        m.append(_madde("Kanal", False, "Henüz kanal yok. Kanal ekle."))
    else:
        c = kanallar.oku(akt)
        eks = kanallar.eksikler(akt)
        m.append(_madde(f"Kanal: {c['ad']}", not any(e["zorunlu"] for e in eks),
                        "Üretime hazır" if not eks else f"{len(eks)} not (kanal kartında)"))
    acik = capcut_acik()
    m.append(_madde("CapCut", not acik, "Kapalı." if not acik else
                    "Açık. Montaj adımından önce kapatman gerekecek.", zorunlu=False))
    return {"maddeler": m, "hazir": all(x["tamam"] for x in m if x["zorunlu"])}


def capcut_acik() -> bool:
    from .sistem_win import capcut_acik as acik
    return acik()
```

### `app/kanal_studyosu/openrouter.py`

```python
"""OpenRouter üzerinden Claude (Anthropic hesabı olmadan).

OpenRouter, Anthropic Messages biçimini birebir kabul eden bir uç nokta sunar (taban: https://openrouter.ai/api,
kimlik: OpenRouter anahtarı Bearer olarak). Uygulamanın Anthropic katmanı aynen kullanılır; burada yalnızca:
- model adları eşlenir (claude-sonnet-5-5 → anthropic/claude-sonnet-5.5; ayar dosyasından, yoksa OpenRouter listesinden),
- anahtar denenir (GET /api/v1/key, ücretsiz).
İstek ayrıntıları (desteklenmeyen alanların ayıklanması) llm.py'dedir.
"""
from __future__ import annotations

import re
import threading
import urllib.error
import urllib.request

from . import ayarlar as A
from . import kayit
from .ai84 import KIMLIK, AI84, AI84Hatasi, _curl, _json

API = "https://openrouter.ai/api"
_ESLESME: dict[str, str] = {}
_KILIT = threading.Lock()


def _get(yol: str, anahtar: str = "") -> tuple[int, dict]:
    bas = {"Accept": "application/json", **({"Authorization": f"Bearer {anahtar}"} if anahtar else {})}
    if _curl():
        try:
            kod, j, _ = AI84._curl_istek("GET", API + yol, bas, None, 25)
        except AI84Hatasi as e:  # ağ hatası (metin AI84'e göre yazılmış; yalnız ayrıntı alınır)
            return 0, {"message": str(e).split("(", 1)[-1].rstrip(").")}
        return kod, j
    try:
        with urllib.request.urlopen(urllib.request.Request(API + yol, headers={**bas, "User-Agent": KIMLIK}),
                                    timeout=25) as c:
            return c.status, _json(c.read())
    except urllib.error.HTTPError as e:
        return e.code, _json(e.read())
    except (urllib.error.URLError, OSError) as e:
        return 0, {"message": str(getattr(e, "reason", e))}


def _normal(ad: str) -> str:
    """anthropic/claude-sonnet-5.5[1m] → claude-sonnet-5-5 (ekler ve ":batch" gibi varyantlar yok sayılır)."""
    return re.sub(r"\[.*?\]|:.*$", "", ad.split("/", 1)[-1]).replace(".", "-").lower()


def model_eslestir(ic_model: str) -> str:
    """Uygulamadaki model adı → OpenRouter model kimliği. Önce ayar dosyasındaki sabit eşleme (kullanılan üç model,
    2 Ekim 2026 testinde doğrulandı), yoksa OpenRouter model listesinden; listede de yoksa 'anthropic/claude-x-y.z'."""
    sabit = A.ayarlar().get("openrouter", {}).get("modeller", {}).get(ic_model)
    if sabit:
        return sabit
    with _KILIT:
        if ic_model in _ESLESME:
            return _ESLESME[ic_model]
        kod, j = _get("/v1/models")
        adaylar = [m.get("id", "") for m in (j.get("data") or []) if str(m.get("id", "")).startswith("anthropic/")]
        adaylar.sort(key=lambda a: (":" in a, "[" in a, a))  # önce eksiz ad
        bulunan = next((a for a in adaylar if _normal(a) == ic_model.lower()), "")
        if not bulunan:
            kayit.yaz(f"OpenRouter'da {ic_model} bulunamadı (liste {kod}); 'anthropic/{ic_model}' deneniyor", "uyari")
            bulunan = "anthropic/" + re.sub(r"-(\d+)-(\d+)$", r"-\1.\2", ic_model)
        _ESLESME[ic_model] = bulunan
        return bulunan


def dogrula(anahtar: str = "") -> tuple[bool, str]:
    anahtar = anahtar or A.anahtar("openrouter")
    if not anahtar:
        return False, "OpenRouter anahtarı kayıtlı değil. Ayarlar'dan ekle."
    kod, j = _get("/v1/key", anahtar)
    if kod == 200:
        d = j.get("data", j)
        kalan = d.get("limit_remaining")
        ek = f" · kalan limit {kalan:.2f} $" if isinstance(kalan, (int, float)) else ""
        ucretsiz = " · ücretsiz hesap (kredi yükle)" if d.get("is_free_tier") else ""
        return True, f"OpenRouter anahtarı geçerli{ek}{ucretsiz}."
    if kod == 401:
        return False, "OpenRouter anahtarı geçersiz (HTTP 401)."
    if kod == 0:
        return False, f"OpenRouter'a ulaşılamadı ({j.get('message', 'ağ hatası')})."
    msg = (j.get("error") or {}).get("message") if isinstance(j.get("error"), dict) else j.get("message")
    return False, f"OpenRouter'a bağlanılamadı (HTTP {kod}){': ' + str(msg) if msg else ''}."


def bakiye(anahtar: str = "") -> float | None:
    """Kalan bakiye ($). Önce /credits (toplam yüklenen − toplam harcanan), olmazsa anahtarın kalan limiti.
    Okunamazsa None (gösterge '—' yazar)."""
    anahtar = anahtar or A.anahtar("openrouter")
    if not anahtar:
        return None
    kod, j = _get("/v1/credits", anahtar)
    d = j.get("data", j) if kod == 200 else {}
    if isinstance(d.get("total_credits"), (int, float)) and isinstance(d.get("total_usage"), (int, float)):
        return round(d["total_credits"] - d["total_usage"], 2)
    kod, j = _get("/v1/key", anahtar)
    kalan = (j.get("data", j) if kod == 200 else {}).get("limit_remaining")
    if isinstance(kalan, (int, float)):
        return round(kalan, 2)
    kayit.yaz(f"OpenRouter bakiyesi okunamadı (credits {kod})", "uyari")
    return None


def istemci(anahtar: str):
    import anthropic
    # Kimlik Bearer ile gider; api_key boş bırakılır (OpenRouter belgesindeki Claude Code kurulumu gibi).
    return anthropic.Anthropic(base_url=API, auth_token=anahtar, api_key=None, max_retries=2, timeout=900,
                               default_headers={"X-Title": "Kanal Studyosu"})
```

### `app/kanal_studyosu/ses_kenar.py`

```python
"""Sahne sesinin kenarları: sondaki kesik "dit" ve sondaki izole tık (kullanıcı kararı, 2 Eki 2026).

Hesap, kullanıcının bir videoyu elle düzelttiği ve kulakla onayladığı iki betikten birebir alınmıştır:
  ses_kenar_duzelt.py → analiz() ve filtre()   (tail/tık ve onset, afade değerleri)
  ses_kenar_kontrol.py → kesik() ve sinif()    (1 ms blok tepeleri, sert/orta kesik)
Analiz, sahne sesinin seviyesi ayarlanmış ve sonuna sessizlik eklenmiş hâli (kayıpsız WAV) üzerinde yapılır;
betikler de bitmiş sahne sesini ölçüyordu. Eşikler ayar dosyasında: video.kenar.
"""
from __future__ import annotations

import array
import math
import subprocess

SR = 48000

VARSAYILAN = {
    "ornek_esigi": 8,            # |örnek| > 8 → sesli (son sesli örnek)
    "blok_ms": 5,                # sesli bölüm blokları
    "blok_db": -50,              # blok RMS > -50 dB → sesli
    "bosluk_blok": 12,           # ≤12 blokluk boşluk aynı bölüm
    "tik_ms": 30,                # son bölüm ≤30 ms …
    "tik_sessizlik_ms": 300,     # … ve öncesinde ≥300 ms sessizlik → tık
    "onset_blok_ms": 10,
    "onset_db": -45,
    "onset_pay": 0.025,          # fade-in başı = onset − 25 ms
    "fade_in": 0.010,
    "fade_in_basta": 0.004,      # onset ≈ 0 ise
    "fade_out": 0.030,
    "kontrol_geri_ms": 12,
    "kontrol_tepe": 300,
    "kontrol_taban": 30,
    "sert_db": 25, "sert_dbfs": -35,
    "orta_db": 20, "orta_dbfs": -45,
}


def ayar(kenar: dict | None) -> dict:
    return {**VARSAYILAN, **(kenar or {})}


def pcm(yol, ffmpeg: str = "ffmpeg") -> array.array:
    """Mono 48 kHz 16 bit örnekler (betiklerdeki pcm())."""
    r = subprocess.run([ffmpeg, "-v", "error", "-i", str(yol), "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                       capture_output=True, timeout=600)
    a = array.array("h")
    a.frombytes(r.stdout[:len(r.stdout) // 2 * 2])
    return a


def _rms_db(s, n: int) -> float:
    r = math.sqrt(sum(x * x for x in s) / n) / 32768
    return -99 if r <= 1e-5 else 20 * math.log10(r)


def _son_sesli(a, esik: int) -> int | None:
    for i in range(len(a) - 1, -1, -1):
        if abs(a[i]) > esik:
            return i
    return None


def analiz(a, k: dict) -> dict | None:
    """→ {tik, tail, onset, hc} (saniye); ses tamamen sessizse None."""
    son = _son_sesli(a, k["ornek_esigi"])
    if son is None:
        return None
    e = son / SR
    n5 = int(SR * k["blok_ms"] / 1000)
    bloklar = [_rms_db(a[i:i + n5], n5) for i in range(0, len(a) - n5, n5)]
    sp = [i for i, x in enumerate(bloklar) if x > k["blok_db"]]
    tik, tail = False, e
    if sp:
        bolumler, s, p = [], sp[0], sp[0]
        for i in sp[1:]:
            if i - p > k["bosluk_blok"]:
                bolumler.append((s, p))
                s = i
            p = i
        bolumler.append((s, p))
        if len(bolumler) > 1:
            ls, le = bolumler[-1]
            _, pe = bolumler[-2]
            if (le - ls + 1) * k["blok_ms"] <= k["tik_ms"] and (ls - pe) * k["blok_ms"] >= k["tik_sessizlik_ms"]:
                tik, tail = True, (pe + 1) * k["blok_ms"] / 1000
    n10 = int(SR * k["onset_blok_ms"] / 1000)
    esik = 10 ** (k["onset_db"] / 20)
    onset = None
    for i in range(0, len(a) - n10, n10):
        if math.sqrt(sum(x * x for x in a[i:i + n10]) / n10) / 32768 > esik:
            onset = i / SR
            break
    onset = onset or 0
    hc = max(0.0, onset - k["onset_pay"])
    return {"tik": tik, "tail": round(tail, 4), "onset": round(onset, 4), "hc": round(hc, 4)}


def filtre(an: dict | None, k: dict) -> str:
    """afade zinciri; sessiz seste boş."""
    if not an:
        return ""
    d1 = k["fade_in"] if an["hc"] > 0 else k["fade_in_basta"]
    fo = max(0.0, an["tail"] - k["fade_out"])
    return (f"afade=t=in:st={an['hc']:.4f}:d={d1}:curve=hsin,"
            f"afade=t=out:st={fo:.4f}:d={k['fade_out']}:curve=hsin")


def kesik(a, k: dict) -> tuple[float, float]:
    """(düşüş dB, tepe dBFS): son sesli örnekten 12 ms geriye 1 ms blok tepeleri (betikteki cut())."""
    ms = SR // 1000

    def tepe(i):
        return max((abs(x) for x in a[i * ms:(i + 1) * ms]), default=0)

    son = _son_sesli(a, k["ornek_esigi"])
    if son is None:
        return (0, -99)
    ke, en = son // ms, (0, -99)
    for i in range(max(0, ke - k["kontrol_geri_ms"]), ke + 1):
        hi = tepe(i)
        lo = max(tepe(i + 1), tepe(i + 2), k["kontrol_taban"])
        dr = 20 * math.log10(max(hi, 1) / lo)
        if hi >= k["kontrol_tepe"] and dr > en[0]:
            en = (dr, -99 if hi <= 0 else 20 * math.log10(hi / 32768))
    return en


def sinif(c: tuple[float, float], k: dict) -> str:
    if c[0] >= k["sert_db"] and c[1] >= k["sert_dbfs"]:
        return "sert"
    if c[0] >= k["orta_db"] and c[1] >= k["orta_dbfs"]:
        return "orta"
    return ""


def rms_toplam(a) -> float:
    return 20 * math.log10(max(1e-9, math.sqrt(sum(x * x for x in a) / max(1, len(a))) / 32768))


def ozet(kayitlar: list[dict]) -> dict:
    """Sahne kayıtlarından (scene['kenar']) video özeti; temiz = sonra 0 sert, 0 orta."""
    say = {"sahne": len(kayitlar), "once_sert": 0, "once_orta": 0, "sonra_sert": 0, "sonra_orta": 0, "tik": 0,
           "seviye_db": 0.0, "kalan": []}
    for x in kayitlar:
        if x.get("once"):
            say["once_" + x["once"]] += 1
        if x.get("sonra"):
            say["sonra_" + x["sonra"]] += 1
            say["kalan"].append(f"sahne {x['sahne']:04d} ({x['sonra']}, {x['sonra_db']:.0f} dB)")
        say["tik"] += 1 if x.get("tik") else 0
        say["seviye_db"] = max(say["seviye_db"], abs(x.get("seviye_farki", 0)))
    say["seviye_db"] = round(say["seviye_db"], 2)
    say["temiz"] = say["sonra_sert"] == say["sonra_orta"] == 0
    say["metin"] = (f"{say['sahne']} sahne · düzeltme öncesi sert {say['once_sert']} / orta {say['once_orta']} → "
                    f"sonrası {say['sonra_sert']}/{say['sonra_orta']} · sonda susturulan tık {say['tik']} · "
                    f"en büyük seviye değişimi {say['seviye_db']} dB")
    return say
```

### `app/kanal_studyosu/sistem_win.py`

```python
"""Windows'a özgü işler (Kanal Stüdyosu Windows sürümü). Mac sürümündeki Anahtar Zinciri, Finder, pgrep ve `open`
yerine geçer. Testlerin Linux'ta da çalışabilmesi için Windows dışında zararsız yedek davranışlar vardır.

- surec_yasiyor: os.kill(pid, 0) Windows'ta süreci SONLANDIRIR; onun yerine OpenProcess/GetExitCodeProcess.
- klasor_ac: Dosya Gezgini (os.startfile).
- capcut_acik: tasklist ile CapCut.exe.
- anahtar_*: Windows Kimlik Bilgisi Yöneticisi (keyring kütüphanesi); kütüphane yoksa ortam değişkeni.
- capcut_varsayilan / capcut_kullanici_verisi: %LOCALAPPDATA%\\CapCut\\User Data.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

WINDOWS = sys.platform == "win32"
_GIZLI = 0x08000000 if WINDOWS else 0  # CREATE_NO_WINDOW: alt süreçler siyah pencere açmasın


def gizli() -> dict:
    """subprocess çağrılarına eklenecek bayrak (Windows'ta konsol penceresi açılmaz)."""
    return {"creationflags": _GIZLI} if WINDOWS else {}


def alt_surecleri_gizle() -> None:
    """Uygulama konsolsuz (pythonw) çalışır; her ffmpeg/curl çağrısında siyah pencere açılmasın diye bütün alt
    süreçlere CREATE_NO_WINDOW eklenir. Yalnız Windows'ta, açılışta bir kez."""
    if not WINDOWS or getattr(subprocess.Popen, "_ks_gizli", False):
        return
    asil = subprocess.Popen.__init__

    def yeni(self, *a, **k):
        k["creationflags"] = k.get("creationflags", 0) | _GIZLI
        asil(self, *a, **k)
    subprocess.Popen.__init__ = yeni
    subprocess.Popen._ks_gizli = True


def surec_yasiyor(pid: int) -> bool:
    if pid <= 0:
        return False
    if not WINDOWS:
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ctypes.get_last_error() == 5  # erişim reddi: süreç var ama başka kullanıcının
    try:
        kod = wintypes.DWORD()
        if not k32.GetExitCodeProcess(h, ctypes.byref(kod)):
            return False
        return kod.value == 259  # STILL_ACTIVE
    finally:
        k32.CloseHandle(h)


def klasor_ac(yol) -> None:
    yol = str(yol)
    if WINDOWS:
        os.startfile(yol)  # noqa: S606 (yalnız kendi klasörlerimiz)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", yol])
    else:
        subprocess.Popen(["xdg-open", yol])


def capcut_acik() -> bool:
    if not WINDOWS:
        return False
    try:
        c = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe", "/NH"], capture_output=True, text=True,
                           **gizli()).stdout
        return "capcut.exe" in c.lower()
    except OSError:
        return False


def capcut_kullanici_verisi() -> Path:
    yerel = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(yerel) / "CapCut" / "User Data"


def capcut_varsayilan() -> str:
    return str(capcut_kullanici_verisi() / "Projects" / "com.lveditor.draft")


# --- anahtarlar ------------------------------------------------------------------

def _keyring():
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def anahtar_oku(servis: str, hesap: str, ortam: str) -> str:
    kr = _keyring()
    if kr is None:
        return os.environ.get(ortam, "")
    try:
        return kr.get_password(servis, hesap) or os.environ.get(ortam, "")
    except Exception:
        return os.environ.get(ortam, "")


def anahtar_yaz(servis: str, hesap: str, deger: str) -> None:
    kr = _keyring()
    if kr is None:
        raise ValueError("Anahtar kaydı için 'keyring' kütüphanesi gerekli (uygulamayı başlatıcıyla aç; ilk açılışta kurulur).")
    try:
        kr.set_password(servis, hesap, deger)
    except Exception as e:
        raise ValueError(f"Anahtar Windows Kimlik Bilgisi Yöneticisi'ne kaydedilemedi ({type(e).__name__}).")


def anahtar_sil(servis: str, hesap: str) -> None:
    kr = _keyring()
    if kr is None:
        return
    try:
        kr.delete_password(servis, hesap)
    except Exception:
        pass
```

### `app/kanal_studyosu/son_kontrol.py`

```python
"""Son kontrol (uygulama içinde): kod kontrolleri + yapay zekâ kontrolleri → RAPOR.md ve 01_OKU_BENI.md.

- Sahne–görsel uyumu ve görselde yazı: görsel model (iş 'uyum'), 12'lik kontak sayfaları; kanalın görsel kuralları soruda.
- Rapor özeti ve kullanıcı mesajı: Haiku (iş 'rapor').
- Sayım, senkron, hassas kelime, dosya düzeni: kod.
"""
from __future__ import annotations

import base64
import json
import re
from datetime import datetime

from . import ayarlar as A
from . import dosya_duzeni
from . import kanal
from . import maliyet
from . import metin as M

UYUM_SORUSU = """Ekteki kontak sayfalarında her küçük resim bir sahne; altında sarı sahne numarası var.
Aşağıda her sahnenin seslendirme cümlesi var.

Kanalın görsel kuralları (kanal ayarından); bunlara uyan görseller SORUN DEĞİLDİR:
{kurallar}

Her sahne için kontrol et:
1) Görsel cümleyle uyuşuyor mu? Yalnızca gerçek uyumsuzlukları "zayif" say: yanlış mekân/nesne, metnin
   anlattığına ters duygu (ör. ağır bir anda belirgin gülümseme), konuyla ilgisiz görsel.
2) Görselde okunabilir yazı, harf ya da kelime var mı?
Yalnızca SORUNLU sahneleri JSON olarak ver, başka bir şey yazma:
{{"0012": {{"uyum": "zayif", "yazi": false, "not": "kısa Türkçe açıklama"}}, ...}}
Sorun yoksa {{}} yaz.

{liste}"""


def gorsel_uyum(kod: str, llm) -> dict:
    sayfalar = sorted((kanal.arsiv_klasoru(kod) / "odak").glob("sayfa*.jpg"),
                      key=lambda p: int(re.search(r"\d+", p.stem).group(0)))
    paragraflar = [M.govde(p) for p in (kanal.video_klasoru(kod) / "02_ElevenLabs_seslendirme_metni.txt")
                   .read_text(encoding="utf-8").strip().split("\n\n") if p.strip()]
    liste = "\n".join(f"{i:04d}: {p[:170]}" for i, p in enumerate(paragraflar, 1))
    icerik = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                           "data": base64.standard_b64encode(s.read_bytes()).decode()}}
              for s in sayfalar]
    kurallar = kanal.ayar()["gorsel"].get("kurallar") or "- Görselde yazı ve logo olmaz."
    kurallar = "\n".join(l if l.lstrip().startswith("-") else f"- {l}" for l in kurallar.splitlines() if l.strip())
    icerik.append({"type": "text", "text": UYUM_SORUSU.format(liste=liste, kurallar=kurallar)})
    cevap = llm.istek("uyum", kod, [], [{"role": "user", "content": icerik}])
    m = re.search(r"\{.*\}", cevap.metin, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except ValueError:
        return {"?": {"uyum": "?", "yazi": False, "not": "Model cevabı okunamadı; kontak sayfalarına elle bak."}}


def rapor_yaz(kod: str, veri: dict, uyum: dict, llm) -> str:
    """RAPOR.md (Arsiv) ve 01_OKU_BENI.md (Videolar). Döner: kullanıcıya kısa özet."""
    m = maliyet.ozet(kod)
    sorunlu = [f"- Sahne {n}: {v.get('not', '')}" + (" · görselde yazı var" if v.get("yazi") else "")
               for n, v in sorted(uyum.items())]
    fazla = [p.name for p in dosya_duzeni.fazlalar(kod)]
    satirlar = [
        f"# {kod} · Üretim raporu", f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}", "",
        "## Özet bilgiler",
        f"- Konu / başlık: {veri.get('baslik', '')}",
        *([f"- Başlangıç: {veri['baslangic']}"] if veri.get("baslangic") else []),
        *([f"- Bu üretimde kapalı onaylar: {veri['onaysiz']} (kontroller temizse beklemeden geçti)"]
          if veri.get("onaysiz") else []),
        f"- Süre / sahne: {veri.get('sure', '')} / {veri.get('sahne', '')}",
        *([f"- Ses kenarı: {veri['ses_kenar']}"] if veri.get("ses_kenar") else []),
        f"- CapCut taslağı: **{kod}** (CapCut'ı açınca listede; görünmezse kapatıp aç)",
        f"- Müzik: {veri.get('muzik', '') or 'bilgi yok'}",
        f"- Maskot sahneleri: {veri.get('maskot', '') or '-'}",
        f"- Altyazı satırı: {veri.get('srt_satir', '')}",
        (f"- Yazım: Claude Code aboneliği (API'yle olsaydı ~{m['abonelik_tahmini_usd']:.2f} $; abonelikten ücret düşmez)"
         + (f" · OpenRouter: {m['video_usd']:.2f} $" if m["video_usd"] else "") if m.get("abonelik") else
         f"- Maliyet (API): {m['video_usd']:.2f} $ · aşamalar: " +
         ", ".join(f"{k} {v:.2f} $" for k, v in m["asamalar"].items())),
        "  (ayrıntılı döküm, Kanal Defteri dahil: Kapanış'tan sonra `MALIYET.md`)",
        "", "## Kod kontrolleri",
        f"- Senkron (senk_kontrol): {veri.get('senk', '')}",
        f"- Hassas kelime: {veri.get('hassas', '')}",
        f"- Odak: {veri.get('odak', '')}",
        f"- Dosya düzeni: " + ("temiz" if not fazla else "fazla dosya: " + ", ".join(fazla)),
        "", "## Sahne–görsel uyumu (yapay zekâ)",
        *(sorunlu or ["- Sorunlu sahne bulunmadı."]),
        "", "## Senin işin", "- CapCut'ta taslağı aç, rötuş yap, dışa aktar.",
        "- Kapak görsellerini Flow'da üret (04 dosyasındaki kapak promptları); iki kapağı Test & compare ile yarıştır.",
    ]
    if veri.get("uyarilar"):
        satirlar += ["", "## Uyarılar", *[f"- {u}" for u in veri["uyarilar"]]]
    rapor = "\n".join(satirlar) + "\n"
    ozet = ""
    try:
        cevap = llm.istek("rapor", kod, [], [{"role": "user", "content":
                          "Aşağıdaki üretim raporunu kullanıcı için en fazla 6 satırlık, sade Türkçe bir özete çevir. "
                          "Teknik terim (token, port, JSON) kullanma. Önce sonuç, sonra yapılması gerekenler.\n\n" + rapor}])
        ozet = cevap.metin.strip()
    except Exception as e:  # özet olmasa da rapor yazılır
        ozet = f"(Özet yazılamadı: {e})"
    rapor = rapor.replace("## Özet bilgiler", f"## Kısa özet\n{ozet}\n\n## Özet bilgiler", 1)
    A.atomik_yaz(kanal.arsiv_klasoru(kod) / "RAPOR.md", rapor)
    oku_beni = "\n".join([
        f"# {kod} — Üretim klasörü", "",
        f"**Başlık:** {veri.get('baslik', '')}",
        f"**Süre / sahne:** {veri.get('sure', '')} / {veri.get('sahne', '')}",
        f"**CapCut taslağı:** {kod}",
        f"**Müzik:** {veri.get('muzik', '') or '-'} · **Maskot:** {veri.get('maskot', '') or '-'}",
        f"**Sahne videoları:** {veri.get('video_klasoru', '')}",
        "", "## Kısa özet", ozet, "",
        f"Ayrıntılı rapor: `Arsiv/{kod}/RAPOR.md` · Üreten: Kanal Stüdyosu {A.SURUM}", ""])
    A.atomik_yaz(kanal.video_klasoru(kod) / "01_OKU_BENI.md", oku_beni)
    return ozet
```

### `app/kanal_studyosu/studio_baglanti.py`

```python
"""Ses (AI84 → ElevenLabs) ve sahne videosu (ffmpeg) üretimi.

Dosya düzeni (kanal klasörünün içinde; araçlar bu düzeni bekler):
  Kanallar/<kanal>/Uretim/<kod-…-id8>/
      video.json  script.txt  visuals/sahneNNNN.jpg  audio/sahneNNNN.mp3  scene-videos/sahneNNNN.mp4

Korumalar (eski motordan aynen):
- Aynı metin + aynı ses ayarı (hash) için ses yeniden üretilmez; aynı görsel+ses+ayar için video yeniden üretilmez.
- AI84 iş numarası video.json'a yazılır; bağlantı koparsa "Tekrar dene" yeni ücretli istek yerine aynı işi sorgular.
- Gönderim anında uygulama kapanmışsa (iş numarası alınamadan) sahne 'belirsiz' işaretlenir; yalnız Tekrar dene'de
  yeniden gönderilir (en fazla o sahne için çift ücret riski).
- Ses YouTube seviyesine (−14 LUFS, iki geçişli loudnorm) getirilir; görselin bulanık hâli arka plan olur;
  her sahne sesten 0,4 sn uzundur (nefes payı; senk_kontrol bunu hata saymaz).
Ses ayarı kanal ayarından (kanal.json → ses) gelir ve uygulama tarafından değiştirilmez.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import ai84 as AI
from . import ayarlar as A
from . import kayit
from . import kanal
from . import kontroller
from . import ses_kenar as SK

KILIT = ".kanal_studyosu_kilit"
GORSEL = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
LOUD = {"youtube": {"I": -14, "TP": -1.5, "LRA": 11}}


class StudioHatasi(Exception):
    pass


def _simdi() -> str:
    return datetime.now(timezone.utc).isoformat()


def _program(ad: str) -> str:
    from .onkontrol import _program as bul
    return bul(ad) or ad


def _istemci() -> AI.AI84:
    return AI.AI84(A.anahtar("ai84"))


# --- kanal ve video kayıtları ------------------------------------------------------

def ses_ayari() -> dict:
    return dict(A.ayarlar()["ses"])


def ses_dogrula(ses: dict) -> list[str]:
    """Ses ayarı kanal ayarındaki gibi kullanılır; eksikse üretim durur (uygulama düzeltmez)."""
    sorun = []
    if not ses.get("voice_id"):
        sorun.append("ses (voice_id) seçilmedi")
    if not ses.get("model_id"):
        sorun.append("ses modeli yok")
    return sorun


def kanal_klasoru() -> Path:
    return kanal.uretim_klasoru()


def kanal_bilgisi() -> dict:
    k = kanal.ayar()
    return {"id": k["kimlik"], "name": k["ad"]}


def kisa_konu(kart: str) -> str:
    m = re.search(r"KONU KARTI\s*·\s*[A-Z0-9-]+-\d+\s*·\s*(.+)", kart)
    return m.group(1).strip()[:40] if m else ""


def _slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ]+", "-", s).strip("-").lower()[:50] or "kayit"


def _videolar():
    for f in kanal_klasoru().glob("*/video.json"):
        yield f.parent, json.loads(f.read_text(encoding="utf-8"))


def _video(vid: str) -> tuple[Path, dict]:
    for p, d in _videolar():
        if d.get("id") == vid:
            return p, d
    raise StudioHatasi("Video kaydı bulunamadı.")


def _kaydet(p: Path, d: dict) -> None:
    d["updated_at"] = _simdi()
    A.json_yaz(p / "video.json", d)


def video_bul_ya_da_olustur(kod: str, ad: str, vid: str | None) -> tuple[str, str]:
    """→ (kanal_id, video_id). Kayıtlı video varsa o kullanılır (kaldığı yerden devam)."""
    sorun = ses_dogrula(ses_ayari())
    if sorun:
        raise StudioHatasi("Ses ayarı eksik: " + "; ".join(sorun) + ". Kanal ayarları › Ses'ten tamamla.")
    k = kanal_bilgisi()
    if vid:
        try:
            _video(vid)
            return k["id"], vid
        except StudioHatasi:
            kayit.yaz(f"Kayıtlı video bulunamadı ({vid}); yeni video açılıyor", "uyari")
    if not _slug(ad).startswith(kod.lower()):
        raise StudioHatasi("Video adı video koduyla başlamalı.")
    vid = uuid.uuid4().hex
    p = kanal_klasoru() / f"{_slug(ad)}-{vid[:8]}"
    for x in ("visuals", "audio", "scene-videos", "temp", "logs"):
        (p / x).mkdir(parents=True, exist_ok=True)
    d = {"id": vid, "channel_id": k["id"], "name": ad.strip(), "stage": "script", "voice_snapshot": ses_ayari(),
         "video_settings": A.ayarlar()["video"], "script_approved": False, "media_approved": False, "scenes": [],
         "created_at": _simdi(), "updated_at": _simdi(), "olusturan": "Kanal Stüdyosu"}
    _kaydet(p, d)
    (p / "script.txt").write_text("", encoding="utf-8")
    return k["id"], vid


def video_klasoru(cid: str, vid: str) -> Path:
    return _video(vid)[0]


def _ayristir(t: str) -> list[str]:
    return [re.sub(r"\s*\n\s*", " ", x).strip() for x in
            re.split(r"\n\s*\n+", t.replace("\r\n", "\n").replace("\r", "\n").strip()) if x.strip()]


def metin_ver(cid: str, vid: str, metin: str, beklenen: int) -> None:
    p, d = _video(vid)
    parcalar, eski, sahneler = _ayristir(metin), d["scenes"], []
    for i, x in enumerate(parcalar, 1):
        s = eski[i - 1] if i <= len(eski) and eski[i - 1].get("text") == x else \
            {"id": uuid.uuid4().hex, "audio_status": "pending", "video_status": "pending"}
        s.update(number=i, text=x)
        sahneler.append(s)
    d.update(scenes=sahneler, script_approved=True, stage="visuals", voice_snapshot=ses_ayari())
    A.atomik_yaz(p / "script.txt", metin)
    _kaydet(p, d)
    if len(sahneler) != beklenen:
        raise StudioHatasi(f"{len(sahneler)} sahne algılandı, beklenen {beklenen}.")


def _sure(f: Path) -> float | None:
    if not f.exists():
        return None
    q = subprocess.run([_program("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", str(f)], capture_output=True, text=True)
    try:
        return round(float(q.stdout.strip()), 3) if q.returncode == 0 else None
    except ValueError:
        return None


def _numara(ad: str) -> int | None:
    m = re.match(r"(?i)^sahne-?(\d{4})(?:[^0-9].*)?\.[^.]+$", ad)
    return int(m.group(1)) if m else None


def tara(p: Path, d: dict, tam: bool = False) -> dict:
    """visuals/ (ve tam=True ise audio/) eşleşmesi; sahne kayıtlarını günceller."""
    by: dict[int, list[Path]] = {}
    for f in (p / "visuals").iterdir():
        if f.is_file() and f.suffix.lower() in GORSEL | VIDEO and _numara(f.name):
            by.setdefault(_numara(f.name), []).append(f)
    say = {"matched": 0, "missing": 0, "conflicts": 0, "audio_missing": 0, "audio_invalid": 0}
    satirlar = []
    for s in d["scenes"]:
        fs, r = by.get(s["number"], []), {"scene": s["number"]}
        if not fs:
            say["missing"] += 1
            s["media_file"] = None
        elif len(fs) > 1:
            say["conflicts"] += 1
            s["media_file"] = None
        else:
            f = fs[0]
            tur = "image" if f.suffix.lower() in GORSEL else "video"
            say["matched"] += 1
            s.update(media_file="visuals/" + f.name, media_type=tur)
            r["type"] = tur
            if tur == "video":
                r["media_duration"] = _sure(f)
        if tam:
            a = p / "audio" / f"sahne{s['number']:04d}.mp3"
            sure = _sure(a)
            if not a.exists():
                say["audio_missing"] += 1
            elif not sure:
                say["audio_invalid"] += 1
            else:
                s.update(audio_file="audio/" + a.name, audio_duration=sure)
                r["audio_duration"] = sure
                if r.get("type") == "video" and r.get("media_duration") is not None:
                    z = r["media_duration"] - sure
                    tol = float(d["video_settings"].get("tolerance_seconds", .3))
                    r["duration_kind"] = "video_long" if z > tol else "video_short" if z < -tol else "matched"
        satirlar.append(r)
    ok = say["missing"] == say["conflicts"] == 0 and (not tam or say["audio_missing"] == say["audio_invalid"] == 0)
    rapor = {"ok": ok, "counts": say, "rows": satirlar}
    d["last_media_scan"] = rapor
    _kaydet(p, d)
    return rapor


def gorselleri_koy(cid: str, vid: str, kaynak: dict[int, Path]) -> dict:
    """kaynak: sahne no → görsel. visuals/sahneNNNN.jpg olarak kopyalanır, kontrol edilip onaylanır."""
    p, d = _video(vid)
    (p / "visuals").mkdir(exist_ok=True)
    for n, yol in sorted(kaynak.items()):
        hedef = p / "visuals" / f"sahne{n:04d}{Path(yol).suffix.lower() or '.jpg'}"
        if not hedef.exists() or hedef.stat().st_size != Path(yol).stat().st_size:
            shutil.copy2(yol, hedef)
    r = tara(p, d)
    c = r["counts"]
    if not r["ok"]:
        raise StudioHatasi(f"Görsel eşleşmesi: {c['matched']} eşleşen, {c['missing']} eksik, {c['conflicts']} çakışan.")
    d.update(media_approved=True, stage="tts")
    _kaydet(p, d)
    return c


# --- ses ---------------------------------------------------------------------------

def _ses_hash(metin: str, ses: dict) -> str:
    # Eski motorla aynı formül: önceden üretilmiş sesler de tanınır.
    return hashlib.sha256((metin + "\0" + json.dumps(ses, sort_keys=True)).encode()).hexdigest()


# Kullanıcı kararı (2 Eki 2026): yalnız ses servisine giden kopyada kıvrık apostrof/tırnak düzleştirilir.
DUZ = str.maketrans({"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'})


def _tts_govde(ses: dict, metin: str) -> dict:
    b = {"text": metin.translate(DUZ), "voice_id": ses["voice_id"], "model_id": ses["model_id"],
         "output_format": ses.get("output_format", "mp3_44100_128"), "with_transcript": False,
         "voice_settings": {k: ses[k] for k in ("stability", "similarity_boost", "style", "speed", "use_speaker_boost")}}
    if ses.get("language_code"):
        b["language_code"] = ses["language_code"]
    return b


def _log(p: Path, olay: str, mesaj: str, n=None) -> None:
    (p / "logs").mkdir(exist_ok=True)
    with open(p / "logs" / "events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": _simdi(), "event": olay, "message": mesaj, "scene": n}, ensure_ascii=False) + "\n")


def _istek_kaydi(p: Path, n: int, govde: dict, jid, dosya: str) -> None:
    """logs/tts_istekleri.jsonl: sahneye ait TAM istek (anahtar başlıkta gider, burada yok) → birebir tekrar."""
    (p / "logs").mkdir(exist_ok=True)
    satir = {"time": _simdi(), "scene": n, "audio_file": "audio/" + dosya, "job_id": jid, **govde,
             "apply_text_normalization": govde.get("apply_text_normalization", "gönderilmedi"),
             "seed": govde.get("seed", "gönderilmedi")}
    with open(p / "logs" / "tts_istekleri.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(satir, ensure_ascii=False) + "\n")


def seslendir(vid: str, ilerleme, tekrar: bool = False, iptal=None, api: AI.AI84 | None = None) -> dict:
    p, d = _video(vid)
    sorun = kontroller.elevenlabs_metni("\n\n".join(x["text"] for x in d["scenes"]))
    if sorun:  # ikinci güvence: AI84'e izinsiz köşeli not gitmesin
        raise StudioHatasi("Seslendirme başlatılmadı; metinde izin verilmeyen köşeli not var: " + "; ".join(sorun[:8]))
    ses = d.get("voice_snapshot") or ses_ayari()
    api = api or _istemci()
    toplam, ok, hatali, kredi = len(d["scenes"]), 0, 0, 0
    for s in d["scenes"]:
        if iptal and iptal():
            return {"durum": "durdu", "ok": ok, "failed": hatali, "total": toplam}
        h, a, st = _ses_hash(s["text"], ses), p / "audio" / f"sahne{s['number']:04d}.mp3", s.get("audio_status")
        if st == "completed" and s.get("generated_hash") == h and a.exists():
            ok += 1
            continue
        if st == "submitting" and not s.get("job_id"):
            s.update(audio_status="unknown",
                     audio_error="Önceki gönderimin sonucu belirsiz (uygulama gönderim anında kapanmış olabilir).")
            _kaydet(p, d)
            st = "unknown"
        if st == "unknown" and not s.get("job_id") and not tekrar:
            hatali += 1
            continue
        if st == "failed" and not tekrar:
            hatali += 1
            continue
        ilerleme(f"Ses {s['number']}/{toplam} · {ok} tamam" + (f", {hatali} hatalı" if hatali else ""))
        try:
            jid = s.get("job_id") if s.get("job_hash", h) == h else None
            if not jid:
                s.update(audio_status="submitting", job_id=None, job_hash=h)
                _kaydet(p, d)
                govde = _tts_govde(ses, s["text"])
                q = api.tts_gonder(govde)
                jid = q.get("job_id") or q.get("task_id")
                _istek_kaydi(p, s["number"], govde, jid, a.name)
                s.update(job_id=jid, job_hash=h, audio_status="queued")
                _kaydet(p, d)
            job = api.tts_bekle(jid)
            ham = api.indir(job["audioUrl"])
            if len(ham) < 128:
                raise AI.AI84Hatasi("İndirilen ses geçersiz.", 2)
            gecici = p / "temp" / (a.name + ".part")
            gecici.parent.mkdir(exist_ok=True)
            gecici.write_bytes(ham)
            os.replace(gecici, a)
            kredi += int(job.get("credit_cost") or 0)
            s.update(audio_status="completed", audio_file="audio/" + a.name, audio_duration=_sure(a), generated_hash=h,
                     job_id=None, job_hash=None, audio_error=None, credit_cost=job.get("credit_cost"))
            ok += 1
            _log(p, "tts_completed", "Ses üretildi", s["number"])
        except AI.AI84Hatasi as e:
            # İş başarısız bittiyse (failed) iş numarası silinir; zaman aşımında korunur (Tekrar dene aynı işi sorgular).
            sakla = e.kategori is None and s.get("job_id")
            s.update(audio_status="failed", audio_error=str(e), **({} if sakla else {"job_id": None, "job_hash": None}))
            hatali += 1
            _log(p, "tts_failed", str(e), s["number"])
            if e.http in (401, 403):  # anahtar/hesap sorunu: diğer sahneleri denemenin anlamı yok
                _kaydet(p, d)
                raise StudioHatasi(str(e))
        _kaydet(p, d)
    if hatali == 0:
        d["stage"] = "check"
        _kaydet(p, d)
    kayit.yaz(f"Ses: {ok} başarılı, {hatali} hatalı · AI84 kredi {kredi}")
    return {"durum": "bitti", "ok": ok, "failed": hatali, "total": toplam, "kredi": kredi}


def ses_olcumu(vid: str) -> tuple[int, float] | None:
    """Konuşma hızı ölçümü için → (kelime, süre sn). Süre bütün sahne seslerinin toplamı + sahne arası duraklar
    (videodaki gibi); ses tag'leri ([calm] gibi) kelime sayılmaz. Bir sahnenin süresi bilinmiyorsa None."""
    p, d = _video(vid)
    sahneler = d.get("scenes") or []
    if not sahneler or any(not isinstance(s.get("audio_duration"), (int, float)) for s in sahneler):
        return None
    kelime = sum(len([w for w in re.sub(r"\[[^\]\n]*\]", " ", s["text"]).split() if re.search(r"\w", w)])
                 for s in sahneler)
    ara = float((d.get("video_settings") or {}).get("pause_seconds", .4))
    return kelime, sum(s["audio_duration"] for s in sahneler) + ara * len(sahneler)


# --- sahne videosu -------------------------------------------------------------------

def _vf(w: int, h: int, fps: int, fit: str) -> str:
    if fit == "crop":
        return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps},format=yuv420p"
    if fit == "blur":
        # Arka plan: görselin kendisi, ekranı dolduracak şekilde büyütülüp bulanıklaştırılır (hız için küçük boyutta).
        bw, bh = max(2, w // 8 // 2 * 2), max(2, h // 8 // 2 * 2)
        return (f"split=2[bg][fg];[bg]scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},gblur=sigma=6,"
                f"eq=brightness=-0.06,scale={w}:{h},setsar=1[bgb];[fg]scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"setsar=1[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2,fps={fps},format=yuv420p")
    return f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={fps},format=yuv420p"


def _loudnorm(a: Path, mod: str) -> str:
    """İki geçişli loudnorm: önce ölç, sonra ölçülen değerlerle doğrusal normalizasyon filtresi."""
    t = LOUD.get(mod)
    if not t:
        return ""
    q = subprocess.run([_program("ffmpeg"), "-hide_banner", "-nostats", "-i", str(a), "-af",
                        f"loudnorm=I={t['I']}:TP={t['TP']}:LRA={t['LRA']}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=600)
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', q.stderr)
    if q.returncode or not m:
        raise StudioHatasi("Ses seviyesi ölçülemedi.")
    x = json.loads(m.group(0))
    if any(not re.fullmatch(r"-?\d+(\.\d+)?", str(x.get(k, ""))) for k in
           ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")):
        return ""  # sessiz/çok kısa ses: dokunma
    return (f"loudnorm=I={t['I']}:TP={t['TP']}:LRA={t['LRA']}:measured_I={x['input_i']}:measured_TP={x['input_tp']}:"
            f"measured_LRA={x['input_lra']}:measured_thresh={x['input_thresh']}:offset={x['target_offset']}:"
            "linear=true,aresample=48000,")


def _dosya_hash(f: Path) -> str:
    h = hashlib.sha256()
    with open(f, "rb") as x:
        for b in iter(lambda: x.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def videolari_uret(vid: str, ilerleme, tekrar: bool = False, iptal=None) -> dict:
    p, d = _video(vid)
    rapor = tara(p, d, True)
    if not rapor["ok"]:
        raise StudioHatasi("Son kontrolde eksik veya çakışan dosya var.")
    satir = {x["scene"]: x for x in rapor["rows"]}
    s0 = {"loudness": "youtube", **d["video_settings"]}
    w, h, fps = int(s0.get("width", 1920)), int(s0.get("height", 1080)), int(s0.get("fps", 30))
    ara = float(s0.get("pause_seconds", .4))
    toplam, ok, hatali = len(d["scenes"]), 0, 0
    for s in d["scenes"]:
        if iptal and iptal():
            return {"durum": "durdu", "ok": ok, "failed": hatali, "total": toplam}
        r = satir[s["number"]]
        m, a = p / s["media_file"], p / s["audio_file"]
        tur = r.get("duration_kind", "image")
        ek = "-video-uzun" if tur == "video_long" else "-video-kisa" if tur == "video_short" else ""
        cikti = p / "scene-videos" / f"sahne{s['number']:04d}{ek}.mp4"
        hedef = max(r.get("media_duration") or 0, (r["audio_duration"] or 0) + ara)
        imza = hashlib.sha256((_dosya_hash(m) + _dosya_hash(a) + json.dumps(s0, sort_keys=True)).encode()).hexdigest()
        if s.get("video_status") == "completed" and s.get("video_signature") == imza and cikti.exists():
            ok += 1
            continue
        if s.get("video_status") == "failed" and not tekrar:
            hatali += 1
            continue
        ilerleme(f"Sahne videosu {s['number']}/{toplam} · {ok} tamam" + (f", {hatali} hatalı" if hatali else ""))
        s["video_status"] = "processing"
        _kaydet(p, d)
        try:
            filtre = _vf(w, h, fps, s0.get("fit", "blur"))
            komut = [_program("ffmpeg"), "-y"] + (["-loop", "1"] if s["media_type"] == "image" else []) + \
                ["-i", str(m), "-i", str(a)]
            if s["media_type"] == "video":
                filtre += f",tpad=stop_mode=clone:stop_duration={max(0, hedef - (r.get('media_duration') or 0)):.3f}"
            gecici = str(cikti) + ".part.mp4"
            ses_filtresi = _loudnorm(a, s0.get("loudness")) + f"apad=pad_dur={max(0, hedef - r['audio_duration']):.3f}"
            kenar, wav = None, None
            if s0.get("kenar"):  # kenar yumuşatma: yalnız bu ayarla açılmış (yeni) videolarda
                k = SK.ayar(s0["kenar"])
                wav = p / "temp" / f"sahne{s['number']:04d}.kenar.wav"
                wav.parent.mkdir(exist_ok=True)
                q = subprocess.run([_program("ffmpeg"), "-y", "-v", "error", "-i", str(a), "-af", ses_filtresi,
                                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", "-t", f"{hedef:.3f}", str(wav)],
                                   capture_output=True, text=True, timeout=600)
                if q.returncode:
                    raise StudioHatasi(q.stderr[-800:])
                a0 = SK.pcm(wav, _program("ffmpeg"))
                kenar = SK.analiz(a0, k)
                komut[-1] = str(wav)  # ses girişi: seviyesi ayarlı kayıpsız WAV (ses tek kez kodlanır)
                ses_filtresi = SK.filtre(kenar, k) or "anull"
            komut += ["-vf", filtre, "-af", ses_filtresi, "-map", "0:v:0", "-map", "1:a:0",
                      "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a",
                      "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", "-t", f"{hedef:.3f}", gecici]
            q = subprocess.run(komut, capture_output=True, text=True, timeout=1800)
            if q.returncode:
                raise StudioHatasi(q.stderr[-800:])
            if wav:
                a1 = SK.pcm(gecici, _program("ffmpeg"))
                once, sonra = SK.kesik(a0, k), SK.kesik(a1, k)
                s["kenar"] = {"sahne": s["number"], **(kenar or {"sessiz": True}),
                              "once": SK.sinif(once, k), "once_db": round(once[0], 1),
                              "sonra": SK.sinif(sonra, k), "sonra_db": round(sonra[0], 1),
                              "seviye_farki": round(SK.rms_toplam(a0) - SK.rms_toplam(a1), 3)}
                wav.unlink(missing_ok=True)  # uygulamanın kendi ara dosyası; ham mp3 audio/ içinde aynen durur
            os.replace(gecici, cikti)
            s.update(video_status="completed", video_file="scene-videos/" + cikti.name, video_signature=imza,
                     output_duration=_sure(cikti), duration_kind=tur, video_error=None)
            ok += 1
            _log(p, "render_completed", "Video üretildi", s["number"])
        except (StudioHatasi, subprocess.TimeoutExpired, OSError) as e:
            s.update(video_status="failed", video_error=str(e)[-800:])
            hatali += 1
            _log(p, "render_failed", str(e)[-300:], s["number"])
        _kaydet(p, d)
    d["stage"] = "render"
    _kaydet(p, d)
    return {"durum": "bitti", "ok": ok, "failed": hatali, "total": toplam}


def kenar_ozeti(vid: str) -> dict | None:
    """Sahne seslerinin kenar kontrolü özeti (kenar ayarı olmayan eski videolarda None)."""
    _, d = _video(vid)
    if not d.get("video_settings", {}).get("kenar"):
        return None
    return SK.ozet([s["kenar"] for s in d["scenes"] if s.get("kenar")])


def is_calistir(tur: str, cid: str, vid: str, ilerleme, tekrar: bool = False, iptal=None) -> dict:
    """tts: seslendirme, render: sahne videoları. Durdur o anki sahne bitince etkili olur."""
    j = seslendir(vid, ilerleme, tekrar, iptal) if tur == "tts" else videolari_uret(vid, ilerleme, tekrar, iptal)
    ad = "Ses" if tur == "tts" else "Sahne videosu"
    if j["durum"] == "durdu":
        raise StudioHatasi(f"Durduruldu ({j['ok']}/{j['total']} sahne hazır). Tekrar dene kaldığı yerden sürer; "
                           "biten sahneler yeniden üretilmez.")
    kayit.yaz(f"{ad}: {j['ok']} başarılı, {j['failed']} hatalı")
    return j


def son_kontrol(cid: str, vid: str) -> None:
    p, d = _video(vid)
    r = tara(p, d, True)
    c = r["counts"]
    if not r["ok"]:
        raise StudioHatasi(f"Son kontrol: {c['audio_missing']} ses eksik, {c['audio_invalid']} ses bozuk, "
                           f"{c['missing']} görsel eksik.")
    d["stage"] = "render"
    _kaydet(p, d)


def videolari_dogrula(klasor: Path, beklenen: int) -> dict:
    """ffprobe: hepsi 1920x1080, 30 fps, sesli. → {'sure': sn, 'sorunlar': [...]}"""
    dosyalar = [f for f in sorted((klasor / "scene-videos").glob("sahne*.mp4"))
                if re.fullmatch(r"sahne\d{4}(-video-(uzun|kisa))?\.mp4", f.name)]
    sorun, toplam = [], 0.0
    if len(dosyalar) != beklenen:
        sorun.append(f"{len(dosyalar)} sahne videosu var, beklenen {beklenen}.")
    for f in dosyalar:
        q = subprocess.run([_program("ffprobe"), "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", str(f)],
                           capture_output=True, text=True)
        try:
            j = json.loads(q.stdout)
            v = next(x for x in j["streams"] if x["codec_type"] == "video")
            toplam += float(j["format"]["duration"])
        except (ValueError, KeyError, StopIteration):
            sorun.append(f"{f.name} okunamadı")
            continue
        if (v.get("width"), v.get("height")) != (1920, 1080):
            sorun.append(f"{f.name} boyut {v.get('width')}x{v.get('height')}")
        if v.get("r_frame_rate") not in ("30/1", "30000/1000"):
            sorun.append(f"{f.name} kare hızı {v.get('r_frame_rate')}")
        if not any(x["codec_type"] == "audio" for x in j["streams"]):
            sorun.append(f"{f.name} ses yok")
    return {"sure": round(toplam, 2), "sorunlar": sorun}


def sure_metni(sn: float) -> str:
    m, s = divmod(int(round(sn)), 60)
    return f"{m}:{s:02d}"


# --- aynı videoda iki süreç çalışmasın ----------------------------------------------------

def kilit_al(klasor: Path, kod: str) -> None:
    """Video klasörüne kilit dosyası; başka bir Kanal Stüdyosu süreci aynı videoda çalışıyorsa durur."""
    k = klasor / KILIT
    if k.exists():
        try:
            pid = int(json.loads(k.read_text(encoding="utf-8")).get("pid", 0))
            from .sistem_win import surec_yasiyor  # Windows'ta os.kill(pid, 0) süreci sonlandırır
            if surec_yasiyor(pid) and pid != os.getpid():
                raise StudioHatasi("Bu video başka bir Kanal Stüdyosu penceresinde işleniyor.")
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass  # eski/yarım kalmış kilit: üzerine yazılır
    k.write_text(json.dumps({"pid": os.getpid(), "kod": kod, "zaman": time.strftime("%Y-%m-%d %H:%M:%S")}),
                 encoding="utf-8")


def kilit_birak(klasor: Path) -> None:
    k = klasor / KILIT
    if k.exists():
        k.unlink()  # yalnız uygulamanın kendi kilit dosyası; kullanıcı dosyası değil
```

### `app/kanal_studyosu/sunucu.py`

```python
"""Yerel HTTP sunucu (yalnızca 127.0.0.1): her açılışta rastgele erişim anahtarı, yabancı Host başlığı reddedilir."""
from __future__ import annotations

import json
import os
import re
import secrets
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import asamalar as S
from . import ayarlar as A
from . import kanal
from . import kanal_sablonu
from . import kanallar
from . import kayit
from . import maliyet
from . import onkontrol
from . import yollar
from .uretim import Uretim, baslik_bul

WEB = Path(__file__).resolve().parent / "web"
TOKEN = secrets.token_urlsafe(32)
PORT = [0]
DURUM = {"onkontrol": None, "onkontrol_suruyor": False, "uretim": None}
# Kalan bakiye (üst panel): açılışta, her adım bitince, 10 dakikada bir ve tıklanınca yenilenir. Sorgular ücretsiz.
BAKIYE = {"openrouter": None, "ai84": None, "zaman": 0.0, "suruyor": False, "calisiyordu": False}
BAKIYE_SURESI = 600
_KILIT = threading.RLock()


def onkontrol_baslat() -> None:
    with _KILIT:
        if DURUM["onkontrol_suruyor"]:
            return
        DURUM["onkontrol_suruyor"] = True

    def is_():
        try:
            DURUM["onkontrol"] = onkontrol.calistir()
        except Exception as e:
            kayit.yaz(f"Ön kontrol hatası: {e}", "hata")
            DURUM["onkontrol"] = {"maddeler": [{"ad": "Ön kontrol", "tamam": False, "zorunlu": True,
                                                "mesaj": f"Kontrol yapılamadı: {e}"}], "hazir": False}
        finally:
            DURUM["onkontrol_suruyor"] = False

    threading.Thread(target=is_, daemon=True).start()


def bakiye_yenile() -> None:
    with _KILIT:
        if BAKIYE["suruyor"]:
            return
        BAKIYE["suruyor"] = True

    def is_():
        try:
            from . import openrouter
            from .ai84 import AI84, AI84Hatasi
            or_ = openrouter.bakiye() if A.genel().get("saglayici") == "openrouter" else None
            try:
                ai = AI84(A.anahtar("ai84")).krediler() if A.anahtar("ai84") else None
            except AI84Hatasi:
                ai = None
            BAKIYE.update(openrouter=or_, ai84=ai)
        except Exception as e:  # gösterge hiçbir zaman uygulamayı durdurmaz
            kayit.yaz(f"Bakiye okunamadı: {e}", "uyari")
        finally:
            BAKIYE.update(zaman=time.time(), suruyor=False)

    threading.Thread(target=is_, daemon=True).start()


def _bakiye_durumu(u) -> dict:
    calisiyor = bool(u and u.calisiyor())
    if (BAKIYE["calisiyordu"] and not calisiyor) or time.time() - BAKIYE["zaman"] > BAKIYE_SURESI:
        bakiye_yenile()
    BAKIYE["calisiyordu"] = calisiyor
    return {"saglayici": A.genel().get("saglayici", "claude_code"), "openrouter": BAKIYE["openrouter"],
            "ai84": BAKIYE["ai84"], "zaman": BAKIYE["zaman"], "suruyor": BAKIYE["suruyor"]}


def uretim() -> Uretim | None:
    with _KILIT:
        u = DURUM["uretim"]
        if u is not None and u.d.get("kanal") not in (None, kanallar.aktif()):
            DURUM["uretim"] = u = None
        if u is None:
            DURUM["uretim"] = u = Uretim.aktif() if kanallar.aktif() else None
        return u


def _liste_satiri(v: dict) -> dict:
    """Videolar tablosu satırı: uygulamanın ürettiği videolarda rapor düğmesi; başlık boş kaldıysa arşivden doldurulur."""
    v = dict(v)
    kod = v.get("kod", "")
    if v.get("salt_okunur") or not kanal.KOD.match(kod):
        return v
    arsiv = kanal.arsiv_klasoru(kod)
    v["rapor"] = (arsiv / "RAPOR.md").exists()
    if not v.get("baslik"):
        b = baslik_bul(kod, lambda ad: (arsiv / ad).read_text(encoding="utf-8"), uyar=False)
        if b:
            kanal.liste_guncelle(kod, baslik=b)
            v["baslik"] = b
    return v


def genel_durum() -> dict:
    ayar = A.ayarlar()
    akt = kanallar.aktif()
    kanal_ = None
    u = uretim()
    if akt:
        c = kanallar.oku(akt)
        try:
            liste = [_liste_satiri(v) for v in kanal.uretim_listesi()["videolar"].values()]
            siradaki = kanal.siradaki_kod()
        except (OSError, ValueError) as e:
            liste, siradaki = [], None
            kayit.yaz(f"Kanal klasörü okunamadı: {e}", "uyari")
        kanal_ = {"ayar": c, "eksikler": kanallar.eksikler(akt), "dosyalar": kanallar.dosyalar(akt),
                  "videolar": kanallar.videolar(akt), "klasor": str(kanallar.klasor(akt)), "liste": liste,
                  "siradaki": siradaki, "dil_adi": kanal.dil_adi(),
                  "asamalar": [{"kimlik": k, "ad": S.adim_adlari()[k],
                                "onay": S.ASAMALAR[k].onay if k in S.ASAMALAR and S.onay_gerekli(S.ASAMALAR[k], u.d if u else None)
                                else None,
                                "yazi": k in S.ASAMALAR,
                                "ciktilar": S.ASAMALAR[k].ciktilar(u.kod) if u and k in S.ASAMALAR else []}
                               for k in S.gorunum_sirasi(u.d if u else None)],
                  "onay_secilebilir": [{"kimlik": k, "onay": S.ASAMALAR[k].onay, "ad": S.adim_adlari()[k]}
                                       for k in S.ONAY_SECILEBILIR if k in S.sira()],
                  "onaylar": S.onay_varsayilan(), "hazir_diller": S.hazir_diller()}
    return {
        "surum": A.SURUM, "kurulum": str(yollar.kok()),
        "onkontrol": DURUM["onkontrol"], "onkontrol_suruyor": DURUM["onkontrol_suruyor"],
        "kanallar": kanallar.liste(), "aktif": akt, "kanal": kanal_,
        "uretim": u.ozet() if u else None,
        "maliyet": maliyet.ozet(u.kod if u else None),
        "bakiye": _bakiye_durumu(u),
        "diller": kanallar.DILLER, "asamalar": [{"kimlik": k, "ad": a} for k, a in kanallar.ASAMALAR],
        "kanal_varsayilan": kanallar.varsayilan(), "konusma_hizi": kanallar.KONUSMA_HIZI,
        "kelime_payi": kanallar.KELIME_PAYI,
        "ayarlar": {"saglayici": ayar.get("saglayici", "claude_code"), "yollar": ayar["yollar"], "butce": ayar["butce"],
                    "onbellek_suresi": ayar["onbellek_suresi"],
                    "modeller": {k: v["ad"] for k, v in ayar["modeller"].items()},
                    "efor_destekli": [k for k, v in ayar["modeller"].items() if v["efor"]]},
        "anahtarlar": {t: bool(A.anahtar(t)) for t in A.ANAHTARLAR},
    }


class Isleyici(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _gonder(self, veri, kod=200, tur="application/json; charset=utf-8"):
        govde = veri if isinstance(veri, bytes) else json.dumps(veri, ensure_ascii=False).encode()
        self.send_response(kod)
        self.send_header("Content-Type", tur)
        self.send_header("Content-Length", str(len(govde)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(govde)

    def _host_ok(self):
        return self.headers.get("Host", "") in (f"127.0.0.1:{PORT[0]}", f"localhost:{PORT[0]}")

    def _yetkili(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        return self.headers.get("X-App-Token") == TOKEN or q.get("token") == [TOKEN]

    def _govde(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        if not self._host_ok():
            return self._gonder({"hata": "Geçersiz Host"}, 403)
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            html = (WEB / "index.html").read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
            return self._gonder(html.encode(), tur="text/html; charset=utf-8")
        if u.path in ("/app.js", "/stil.css"):
            tur = "text/javascript; charset=utf-8" if u.path.endswith(".js") else "text/css; charset=utf-8"
            return self._gonder((WEB / u.path[1:]).read_bytes(), tur=tur)
        if not self._yetkili():
            return self._gonder({"hata": "Yetkisiz"}, 403)
        try:
            q = urllib.parse.parse_qs(u.query)
            if u.path == "/api/durum":
                return self._gonder(genel_durum())
            if u.path == "/api/kayit":
                return self._gonder({"satirlar": kayit.son()})
            if u.path == "/api/kanal/dosya":
                k, ad = q.get("kanal", [""])[0], q.get("ad", [""])[0]
                return self._gonder({"ad": ad, "icerik": kanallar.dosya_oku(k, ad)})
            if u.path == "/api/flow/istek":
                ur = uretim()
                if not ur:
                    return self._gonder({"hata": "Süren üretim yok"}, 404)
                from . import flow
                return self._gonder(A.json_oku(flow.istek_klasoru(ur.kod) / "istek.json", {}) or {})
            if u.path == "/api/rapor":
                # ?kod=<KOD> → listedeki bitmiş video; kodsuz → süren üretim. Maliyet dökümü varsa altına eklenir.
                kod = q.get("kod", [""])[0]
                if not kod:
                    ur = uretim()
                    if not ur:
                        return self._gonder({"hata": "Süren üretim yok"}, 404)
                    kod = ur.kod
                if not kanal.KOD.match(kod):
                    return self._gonder({"hata": "Geçersiz kod"}, 400)
                arsiv = kanal.arsiv_klasoru(kod)
                icerik = (arsiv / "RAPOR.md").read_text(encoding="utf-8")
                if q.get("kod") and (arsiv / "MALIYET.md").exists():
                    icerik += "\n\n---\n\n" + (arsiv / "MALIYET.md").read_text(encoding="utf-8")
                return self._gonder({"kod": kod, "icerik": icerik})
            if u.path == "/api/dosya":
                ur = uretim()
                ad = q.get("ad", [""])[0]
                if not ur or not re.fullmatch(r"[A-Za-z0-9_.\-]+", ad) or not ad.startswith(ur.kod):
                    return self._gonder({"hata": "Dosya bulunamadı"}, 404)
                return self._gonder({"ad": ad, "icerik": ur.oku(ad)})
            if u.path == "/api/kanal/sablon":
                kanal_sablonu.sablon_dosyasi_yaz()
                return self._gonder({"metin": kanal_sablonu.sablon_metni(),
                                     "dosya": str(yollar.kok() / kanal_sablonu.DOSYA_ADI)})
            if u.path == "/api/kanal/silinecekler":
                k = q.get("kanal", [""])[0]
                gidecek, kalan = kanallar.silinecek_taslaklar(k)
                return self._gonder({"taslaklar": [t.name for t in gidecek], "dokunulmayan": kalan,
                                     "klasor": str(kanallar.klasor(k))})
            return self._gonder({"hata": "Bulunamadı"}, 404)
        except FileNotFoundError:
            return self._gonder({"hata": "Dosya henüz yok"}, 404)
        except (ValueError, KeyError) as e:
            return self._gonder({"hata": str(e).strip("'")}, 400)
        except Exception as e:
            kayit.yaz(f"GET {u.path}: {e}", "hata")
            return self._gonder({"hata": str(e)}, 400)

    def do_POST(self):
        if not self._host_ok():
            return self._gonder({"hata": "Geçersiz Host"}, 403)
        if not self._yetkili():
            return self._gonder({"hata": "Yetkisiz"}, 403)
        yol = urllib.parse.urlparse(self.path).path
        try:
            b = self._govde()
            if yol == "/api/onkontrol":
                onkontrol_baslat()
                return self._gonder({"tamam": True})
            if yol == "/api/bakiye":
                bakiye_yenile()
                return self._gonder({"tamam": True})
            if yol == "/api/uretim/baslat":
                ok = DURUM["onkontrol"]
                if not ok or not ok["hazir"]:
                    raise ValueError("Ön kontrolde eksik var; önce onları tamamla.")
                if uretim():
                    raise ValueError("Zaten süren bir üretim var.")
                if any(e["zorunlu"] for e in kanallar.eksikler(kanal.secili())):
                    raise ValueError("Kanalın üretime hazırlığında eksik var (kanal kartına bak).")
                hazir = (b.get("hazir_metin") or "").strip()
                if b.get("hazir") and not hazir:
                    raise ValueError("Hazır metin boş. Metni yapıştır.")
                kod = kanal.siradaki_kod()
                with _KILIT:
                    DURUM["uretim"] = Uretim.yeni(kod, "", b.get("konu_istegi", ""), hazir_metin=hazir,
                                                  hazir_dil=b.get("hazir_dil", ""),
                                                  onaylar=b.get("onaylar") if isinstance(b.get("onaylar"), dict) else None)
                DURUM["uretim"].izleyici_baslat()
                DURUM["uretim"].baslat()
                return self._gonder({"kod": kod})
            if yol.startswith("/api/asama/"):
                ur = uretim()
                if not ur:
                    raise ValueError("Süren üretim yok.")
                eylem = yol.rsplit("/", 1)[1]
                if eylem == "onay":
                    ur.onayla(b["kimlik"], b.get("not", ""))
                elif eylem == "duzeltme":
                    ur.duzeltme_iste(b["kimlik"], b.get("not", ""))
                elif eylem == "elle":
                    return self._gonder({"kontrol": ur.elle_duzenle(b["kimlik"], b["ad"], str(b.get("icerik", "")))})
                elif eylem == "elle-geri":
                    return self._gonder({"kontrol": ur.elle_geri_al(b["kimlik"], b["ad"])})
                elif eylem == "tekrar":
                    ur.tekrar_dene(bool(b.get("butce_onayli")))
                elif eylem == "devam":
                    ur.devam()
                elif eylem == "flow-kontrol":
                    ur.flow_elle_kontrol()
                elif eylem == "flow-sorun-devam":
                    ur.flow_sorun_devam()
                elif eylem == "flow-a5-duzeltme":
                    ur.flow_a5_duzeltme(b.get("not", ""))
                elif eylem == "muzik-yenile":
                    return self._gonder({"secilen": ur.muzik_yenile()})
                elif eylem == "silme":
                    return self._gonder({"tasinan": ur.silme_karari(bool(b.get("tasi")))})
                elif eylem == "kapat":
                    ur.kapat()
                    with _KILIT:
                        DURUM["uretim"] = None
                elif eylem == "durdur":
                    ur.durdur()
                elif eylem == "iptal":
                    sonuc = ur.iptal_et()
                    with _KILIT:
                        DURUM["uretim"] = None
                    return self._gonder(sonuc)
                else:
                    raise ValueError("Bilinmeyen eylem")
                return self._gonder({"tamam": True})
            if yol == "/api/kanal/dosya-oku":
                return self._gonder(kanal_sablonu.oku(str(b.get("metin") or "")))
            if yol == "/api/kanal/dogrula":
                hatalar, uyarilar = kanallar.dogrula(A.birlestir(kanallar.varsayilan(), b.get("kanal") or {}),
                                                     kendi=b.get("kendi"))
                return self._gonder({"hatalar": hatalar, "uyarilar": uyarilar})
            if yol == "/api/kanal/ekle":
                sonuc = kanallar.ekle(b.get("kanal") or {}, b.get("kaynak", "sablon"), b.get("klasor", ""),
                                      str(b.get("anayasa") or ""))
                onkontrol_baslat()
                return self._gonder({"kisaltma": sonuc["kanal"]["kisaltma"], "ice_aktarma": sonuc["ice_aktarma"]})
            if yol == "/api/kanal/guncelle":
                _, uyarilar = kanallar.guncelle(b["kisaltma"], b.get("kanal") or {})
                onkontrol_baslat()
                return self._gonder({"tamam": True, "uyarilar": uyarilar})
            if yol == "/api/kanal/sec":
                kanallar.aktif_sec(b["kisaltma"])
                onkontrol_baslat()
                return self._gonder({"tamam": True})
            if yol == "/api/kanal/sil":
                sonuc = kanallar.sil(b["kisaltma"], b.get("onay_adi", ""))
                onkontrol_baslat()
                return self._gonder(sonuc)
            if yol == "/api/kanal/dosya":
                kanallar.dosya_yaz(b["kanal"], b["ad"], str(b.get("icerik", "")))
                return self._gonder({"tamam": True})
            if yol == "/api/kanal/klasor-ac":
                from .sistem_win import klasor_ac
                klasor_ac(kanallar.klasor(b["kisaltma"]))
                return self._gonder({"tamam": True})
            if yol == "/api/ayarlar":
                A.ayar_kaydet(b)
                onkontrol_baslat()
                bakiye_yenile()
                return self._gonder({"tamam": True})
            if yol == "/api/anahtar":
                tur = b.get("tur", "")
                if tur not in A.ANAHTARLAR:
                    raise ValueError("Bilinmeyen anahtar türü")
                if b.get("sil"):
                    A.anahtar_sil(tur)
                else:
                    A.anahtar_kaydet(tur, b.get("anahtar", ""))
                onkontrol_baslat()
                return self._gonder({"tamam": True})
            if yol == "/api/anahtar-test":
                tur, deger = b.get("tur"), str(b.get("anahtar") or "").strip()
                if tur == "ai84":
                    ok, msg = onkontrol.ai84_dogrula(deger)
                elif tur == "claude_code":
                    from . import claude_code
                    ok, msg = claude_code.durum()
                elif tur == "openrouter":
                    from . import openrouter
                    ok, msg = openrouter.dogrula(deger)
                else:
                    raise ValueError("Bilinmeyen anahtar türü")
                return self._gonder({"tamam": ok, "mesaj": msg})
            if yol == "/api/kayit/ac":
                from .sistem_win import klasor_ac
                klasor_ac(yollar.kayit_dosyasi())
                return self._gonder({"tamam": True})
            if yol == "/api/kapat":
                from . import tek_kopya
                tek_kopya.sil(yollar.calisan_dosyasi())  # os._exit atexit'i çalıştırmaz
                self._gonder({"tamam": True})
                threading.Timer(0.3, lambda: os._exit(0)).start()
                return
            return self._gonder({"hata": "Bulunamadı"}, 404)
        except (ValueError, KeyError) as e:
            return self._gonder({"hata": str(e).strip("'")}, 400)
        except Exception as e:
            kayit.yaz(f"POST {yol}: {e}", "hata")
            return self._gonder({"hata": str(e)}, 400)


def baslat(port: int = 0) -> ThreadingHTTPServer:
    s = ThreadingHTTPServer(("127.0.0.1", port), Isleyici)
    PORT[0] = s.server_port
    return s
```

### `app/kanal_studyosu/tek_kopya.py`

```python
"""Tek kopya: uygulama zaten açıksa ikinci kopya başlamaz, tarayıcıda açık olan gösterilir.

Açık kopya kendi adresini (pid, port, erişim anahtarı) bir dosyaya yazar. Yeni açılış önce bu dosyaya bakar: süreç
yaşıyor ve sunucu cevap veriyorsa o adres döner. Dosya eskiyse (uygulama çökmüş) yok sayılır ve üzerine yazılır.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


def _yasiyor(pid: int) -> bool:
    # Windows'ta os.kill(pid, 0) süreci sonlandırır; güvenli denetim sistem_win'de.
    from .sistem_win import surec_yasiyor
    return surec_yasiyor(pid)


def calisan(dosya: Path) -> str | None:
    """Açık ve cevap veren kopyanın adresi; yoksa None."""
    try:
        d = json.loads(Path(dosya).read_text(encoding="utf-8"))
        pid, port, token = int(d["pid"]), int(d["port"]), str(d["token"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if pid == os.getpid() or not _yasiyor(pid):
        return None
    try:
        r = urllib.request.Request(f"http://127.0.0.1:{port}/api/durum", headers={"X-App-Token": token})
        with urllib.request.urlopen(r, timeout=3) as c:
            if c.status != 200:
                return None
    except OSError:
        return None
    return f"http://127.0.0.1:{port}/?token={token}"


def kaydet(dosya: Path, port: int, token: str) -> None:
    dosya = Path(dosya)
    dosya.parent.mkdir(parents=True, exist_ok=True)
    gecici = dosya.with_name(dosya.name + ".tmp")
    gecici.write_text(json.dumps({"pid": os.getpid(), "port": port, "token": token}), encoding="utf-8")
    os.chmod(gecici, 0o600)  # erişim anahtarı içerir
    os.replace(gecici, dosya)


def sil(dosya: Path) -> None:
    """Yalnız bu kopyanın yazdığı dosyayı siler."""
    try:
        if int(json.loads(Path(dosya).read_text(encoding="utf-8")).get("pid", -1)) == os.getpid():
            Path(dosya).unlink()
    except (OSError, ValueError):
        pass
```

### `app/kanal_studyosu/uretim.py`

```python
"""Üretim akışı: durum kaydı, adımları çalıştırma, otomatik düzeltme, onaylar.

Adımlar (asamalar.sira()): A1–A6 yazı aşamaları → FLOW → STUDIO → CAPCUT → A6_2 → SON → KAPANIS → BITTI
(hedef dil Türkçe ise A4 yok). Durum: Kanallar/<kanal>/Arsiv/<KOD>/_uygulama/durum.json (her adımdan sonra atomik yazılır).
Aşama konuşmaları: _uygulama/konusma_A3.json (asistan blokları düşünme dahil aynen saklanır,
düzeltme turlarında aynen geri gönderilir). Kod çıktı içeriği yazmaz; yalnızca modelin
verdiği dosyaları/yamaları uygular.
"""
from __future__ import annotations

import hashlib
import re
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

from . import araclar
from . import asamalar as S
from . import ayarlar as A
from . import capcut_zinciri as C
from . import cikti
from . import defter
from . import dosya_duzeni
from . import flow
from . import kanal
from . import kanallar
from . import kayit
from . import kontroller as K
from . import maliyet
from . import metin as M
from . import son_kontrol
from . import studio_baglanti as ST
from . import yollar
from .llm import LLM, Durduruldu, LLMHatasi, dusunceleri_cikar



def _aktif_uretim() -> dict | None:
    """Sistem/aktif.json içindeki süren üretim: {"kanal", "kod"}."""
    return (A.json_oku(yollar.aktif_dosyasi(), {}) or {}).get("uretim") or None


def _aktif_yaz(kod: str | None) -> None:
    akt = A.json_oku(yollar.aktif_dosyasi(), {}) or {}
    if kod:
        akt["uretim"] = {"kanal": kanal.secili(), "kod": kod}
    else:
        akt.pop("uretim", None)
    A.json_yaz(yollar.aktif_dosyasi(), akt)
DURAKLAMALAR = ("bekleme", "onay_bekliyor", "hata", "butce_sorusu")


def _simdi() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _ozet_hash(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:12]



def baslik_bul(kod: str, oku, uyar: bool = True) -> str:
    """Seçilen başlık: önce paketin DEFTER KAYDI 'A:' satırı, yoksa konu kartının başlık satırı."""
    for ad, desen in (
            # A: başlık "…" · …  (tırnak türü, iki nokta ve ** kalın yazı serbest; tırnaksızsa ' · ' a kadar)
            (kod + "_6_paket.md",
             r'^\W*A\W*:?\W*başlık\W*?:?\s*(?:«([^»\n]+)»|"([^"\n]+)"|[“„]([^”\n]+)”|\'([^\n]+?)\'\s*(?:·|$)'
             r'|([^·\n]+?)\s*(?:·|$))'),
            (kod + "_1_konu_karti.md", r"^\W*Başlık[^:\n]*:\**\s*(.+?)\s*(?:\(\d+\s*kr\)|$)")):
        try:
            m = re.search(desen, oku(ad), re.M | re.I)
        except FileNotFoundError:
            continue
        bulunan = next((g for g in m.groups() if g), "") if m else ""
        bulunan = bulunan.strip().strip("*`«»\"“”").strip()
        if bulunan and bulunan not in ("…", "..."):
            return bulunan
    if uyar:
        kayit.yaz("Başlık paket ve konu kartında bulunamadı; rapora boş yazılıyor", "uyari")
    return ""


def kanal_studyosu_aktif() -> str | None:
    from . import kanallar
    return kanallar.aktif()


class Uretim:
    """Bir videonun üretimi. Aynı anda tek iş çalışır."""

    def __init__(self, kod: str, llm: LLM | None = None):
        self.kod = kod
        self.llm = llm or LLM()
        self.yol = kanal.uygulama_klasoru(kod) / "durum.json"
        self.d = A.json_oku(self.yol, None)
        if self.d:  # eski sürümle başlamış kayıtlar: yeni adımlar eklenir
            for k in S.gorunum_sirasi(self.d):
                self.d["asamalar"].setdefault(k, {"durum": "bekliyor"})
        self.ilerleme = 0
        self.ilerleme_metni = ""
        self._is: threading.Thread | None = None
        self._suren: str | None = None
        self._durdur = False
        self._izleyici: threading.Thread | None = None

    # --- kayıt ---------------------------------------------------------------
    @classmethod
    def yeni(cls, kod: str, studio_verisi: str, konu_istegi: str, llm: LLM | None = None,
             hazir_metin: str = "", hazir_dil: str = "", onaylar: dict | None = None) -> "Uretim":
        """hazir_metin verilirse 1. aşama yerine 'Hazır metin' aşaması çalışır (hazir_dil: tr ya da kanalın hedef dili).
        onaylar: bu üretimde ONAY 2/4/5 istensin mi ({"A2": bool, …}); verilmezse kanal ayarı geçerli."""
        kanal.video_klasoru(kod).mkdir(parents=True, exist_ok=True)
        kanal.arsiv_klasoru(kod).mkdir(parents=True, exist_ok=True)
        u = cls(kod, llm)
        if u.d is None:
            u.d = {"kod": kod, "baslangic": _simdi(), "studio_verisi": studio_verisi,
                   "konu_istegi": konu_istegi, "adim": "A1", "onay_notlari": {}, "sonuclar": {},
                   "kanal": kanal.secili(), "asamalar": {k: {"durum": "bekliyor"} for k in S.sira()}}
            if onaylar is not None:
                u.d["onaylar"] = {k: bool(onaylar.get(k, v)) for k, v in S.onay_varsayilan().items()}
            if hazir_metin.strip():
                if hazir_dil not in S.hazir_diller():
                    raise ValueError("Hazır metnin dili Türkçe ya da kanalın dili olmalı.")
                sira_, gorunum, atlanan = S.hazir_sira(hazir_dil)
                u.d.update(sira=sira_, gorunum=gorunum, adim=sira_[0], hazir_dil=hazir_dil,
                           asamalar={k: {"durum": "atlandi" if k in atlanan else "bekliyor"} for k in gorunum})
                metin_ = hazir_metin.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"
                A.atomik_yaz(kanal.arsiv_klasoru(kod) / (kod + S.HAZIR_ORIJINAL), metin_)
                kayit.yaz(f"{kod}: hazır metinle başladı ({kanal.dil_adi(hazir_dil)}, {len(metin_.split())} kelime); "
                          f"atlanan: {', '.join(atlanan)}")
            u.kaydet()
        _aktif_yaz(kod)
        kanal.liste_guncelle(kod, durum="Üretimde", salt_okunur=False)
        return u

    @classmethod
    def aktif(cls, llm: LLM | None = None) -> "Uretim | None":
        a = _aktif_uretim()
        if not a or a.get("kanal") != kanal_studyosu_aktif():
            return None
        u = cls(a["kod"], llm)
        if u.d is None:
            return None
        # Uygulama çalışırken kapandıysa yarım kalan adım "tekrar dene"ye düşer.
        for ad, s in u.d["asamalar"].items():
            if s["durum"] in ("calisiyor", "kontrol"):
                s.update(durum="hata", hata="Uygulama bu adım sürerken kapandı. Tekrar dene ile kaldığı yerden sürer.")
        u.kaydet()
        u.izleyici_baslat()
        return u

    def kaydet(self) -> None:
        self.d["guncelleme"] = _simdi()
        A.json_yaz(self.yol, self.d)

    def asama_durumu(self, kimlik: str) -> dict:
        return self.d["asamalar"][kimlik]

    def _konusma_yolu(self, kimlik: str) -> Path:
        return kanal.uygulama_klasoru(self.kod) / f"konusma_{kimlik}.json"

    def oku(self, ad: str) -> str:
        return (kanal.arsiv_klasoru(self.kod) / ad).read_text(encoding="utf-8")

    def _yaz(self, ad: str, icerik: str) -> None:
        A.atomik_yaz(kanal.arsiv_klasoru(self.kod) / ad, icerik)

    def _sonuc(self, **alanlar) -> None:
        self.d.setdefault("sonuclar", {}).update(alanlar)
        self.kaydet()

    # --- iş parçacığı --------------------------------------------------------
    def calisiyor(self) -> bool:
        return bool(self._is and self._is.is_alive())

    def _baslat(self, hedef, kimlik: str, *args) -> None:
        if self.calisiyor():
            raise ValueError("Şu an bir adım çalışıyor; bitmesini bekle.")
        self._durdur = False

        def sar():
            # Hata, o an çalışan adıma yazılır (bir adım kendiliğinden sonrakini başlatabilir).
            try:
                hedef(kimlik, *args)
            except maliyet.ButceAsimi as e:
                self._durum_yaz(self._suren or kimlik, durum="butce_sorusu", hata=str(e))
            except (LLMHatasi, araclar.AracHatasi, ST.StudioHatasi) as e:
                self._durum_yaz(self._suren or kimlik, durum="hata", hata=str(e),
                                hata_ayrinti=getattr(e, "ayrinti", ""))
            except Exception as e:  # beklenmeyen: kayda tam iz, ekrana kısa mesaj + kopyalanabilir ayrıntı
                iz = traceback.format_exc()
                kayit.yaz(iz, "hata")
                self._durum_yaz(self._suren or kimlik, durum="hata", hata=f"Beklenmeyen hata: {e}", hata_ayrinti=iz[-4000:])
            finally:
                self.ilerleme_metni = ""

        self._is = threading.Thread(target=sar, daemon=True)
        self._is.start()

    def _durum_yaz(self, kimlik: str, **alanlar) -> None:
        self.d["asamalar"][kimlik].update(alanlar)
        self.kaydet()

    def _bilgi(self, metin: str) -> None:
        self.ilerleme_metni = metin

    def _iptal_mi(self) -> bool:
        return self._durdur

    def _durdur_kontrol(self) -> None:
        if self._durdur:
            raise Durduruldu("Durduruldu. Tekrar dene ile kaldığı yerden sürer.")

    # --- Durdur ve iptal -----------------------------------------------------
    def durdur(self) -> None:
        """Güvenli durdurma: yazım akışı kesilir; ses/video o anki sahneden sonra, araçlar o anki betikten sonra durur."""
        if not self.calisiyor():
            raise ValueError("Şu an çalışan bir adım yok.")
        self._durdur = True
        self._bilgi("Durduruluyor…")
        kayit.yaz(f"{self.kod}: durdurma istendi")

    def iptal_et(self) -> dict:
        """Üretimi iptal eder. Hiçbir şey silinmez:
        - Videolar/<kod> ve Arsiv/<kod> → Arsiv/<kod>_iptal_<zaman>/ altına taşınır,
        - 03_Aktif_Video.md bu üretimden önceki hâline döndürülür (o anki hâli de iptal klasörüne kopyalanır),
        - üretim listesinden çıkarılır; aynı kod bir sonraki üretimde yeniden kullanılır.
        Üretim klasöründeki ses/video ve CapCut taslağı (varsa) yerinde bırakılır."""
        import shutil
        if self.calisiyor():
            raise ValueError("Önce Durdur'a bas ve adımın durmasını bekle.")
        if self.d["adim"] == S.SON_ADIM or self.d.get("defter_tamam"):
            raise ValueError("Kanal Defteri yenilendikten sonra üretim iptal edilemez.")
        damga = datetime.now().strftime("%Y%m%d_%H%M%S")
        hedef = kanal.kok() / "Arsiv" / f"{self.kod}_iptal_{damga}"
        hedef.mkdir(parents=True)
        rit03 = kanal.proje_klasoru() / kanal.AKTIF
        oncekiler = sorted(kanal.arsiv_klasoru(self.kod).glob("03_Aktif_Video_oncesi_*.md"))
        geri = False
        if oncekiler:
            if rit03.exists():
                shutil.copy2(rit03, hedef / "03_Aktif_Video_iptal_anindaki.md")
            A.atomik_yaz(rit03, oncekiler[0].read_text(encoding="utf-8"))  # ilk yedek = bu üretimden önceki hâl
            geri = True
        _aktif_yaz(None)  # izleyici durur
        if kanal.video_klasoru(self.kod).exists():
            shutil.move(str(kanal.video_klasoru(self.kod)), str(hedef / "Videolar_klasoru"))
        if kanal.arsiv_klasoru(self.kod).exists():
            shutil.move(str(kanal.arsiv_klasoru(self.kod)), str(hedef / "Arsiv_klasoru"))
        liste = kanal.uretim_listesi()
        liste["videolar"].pop(self.kod, None)
        A.json_yaz(kanal.uretim_listesi_yolu(), liste)
        kayit.yaz(f"{self.kod}: üretim iptal edildi → {hedef.name}" + (" · 03_Aktif_Video eski hâline döndü" if geri else ""))
        return {"klasor": str(hedef.relative_to(kanal.kok())), "rit03_geri": geri,
                "studio_video": bool(self.d.get("studio_vid")),
                "capcut_taslak": (A.yol("capcut_taslak") / self.kod).exists()}

    # --- kullanıcı eylemleri -------------------------------------------------
    def baslat(self, kimlik: str | None = None, butce_onayli: bool = False) -> None:
        kimlik = kimlik or self.d["adim"]
        if kimlik in S.ASAMALAR:
            self._baslat(self._calistir, kimlik, None, butce_onayli)
        elif kimlik in ADIM_ISLEVLERI:
            self._baslat(self._adim, kimlik, butce_onayli)
        else:
            raise ValueError("Bu adım başlatılamaz.")

    def onayla(self, kimlik: str, not_: str = "") -> None:
        s = self.asama_durumu(kimlik)
        if s["durum"] != "onay_bekliyor":
            raise ValueError("Bu adım onay beklemiyor.")
        if kimlik in S.ASAMALAR:
            sonraki = self._tamamla(kimlik, not_)
            self._sonrakini_baslat(sonraki)
        else:
            # Kod/araç adımında "Yine de devam et": kullanıcı uyarıları kabul etti.
            self.d.setdefault("kabuller", []).append(f"{kimlik}:{s.get('kabul_anahtari', '')}")
            self.kaydet()
            self.baslat(kimlik)

    def _sonrakini_baslat(self, sonraki: str) -> None:
        if sonraki in S.ASAMALAR or sonraki in ADIM_ISLEVLERI:
            self.baslat(sonraki)

    def _tamamla(self, kimlik: str, not_: str = "") -> str:
        """Adımı kapatır, onay sonrası işlerini yapar; sonraki adımı döndürür."""
        if kimlik in S.ASAMALAR:
            asama = S.ASAMALAR[kimlik]
            eksik = [ad for ad in asama.ciktilar(self.kod) if not (kanal.arsiv_klasoru(self.kod) / ad).exists()]
            if eksik:
                raise ValueError(f"Onaylanamaz: {', '.join(eksik)} yok. Düzeltme iste.")
        bugun = datetime.now().strftime("%d.%m.%Y")
        if kimlik == "A1" or kimlik in S.HAZIR:
            kart = self.oku(self.kod + "_1_konu_karti.md")
            kanal.rit03_yenile(self.kod, S.rit03_kart_ile(self.kod, kart, bugun))
        # Final metin: hedef dil senaryosu (A4 ya da hedef dilde hazır metin) ya da hedef dil Türkçe ise Türkçe senaryo
        if kimlik in ("A4", "HI") or (kimlik in ("A3", "HT") and not kanal.ceviri_var()):
            final = self.oku(S.final_dosya(self.kod))
            kanal.rit03_yenile(self.kod, S.rit03_final_ekle(kanal.rit(kanal.AKTIF), self.kod, final, bugun))
            self._yaz("senaryo_final.txt", final)
        if kimlik == "A5":
            self.d["maskot_argumanlari"] = (self.asama_durumu("A5").get("kontrol") or {}).get("ek", {}).get("maskot", "")
        if kimlik == "A6":
            kanal.liste_guncelle(self.kod, durum="Paket hazır · görseller bekleniyor")
        s = self.asama_durumu(kimlik)
        self.d["onay_notlari"][kimlik] = not_
        s.update(durum="tamam", onay_zamani=_simdi(), onay_notu=not_, hata="")
        donus = self.d.pop("donus_adimi", None)
        if donus and kimlik == "A5":
            # Flow sorununda A5'e düzeltme gönderildi: değişen sahneler için Flow'a geri dönülür.
            self.d["adim"] = donus
            self.asama_durumu(donus).update(durum="bekliyor")
            self.d["flow_yeniden"] = True
        else:
            sira_ = S.sira(self.d)
            i = sira_.index(kimlik)
            self.d["adim"] = sira_[i + 1] if i + 1 < len(sira_) else S.SON_ADIM
        self.kaydet()
        asama = S.ASAMALAR.get(kimlik)
        kayit.yaz(f"{self.kod}: " + (f"ONAY {asama.onay} verildi" if asama and S.onay_gerekli(asama, self.d)
                                     else f"{S.adim_adlari().get(kimlik, kimlik)} tamamlandı"))
        return self.d["adim"]

    def duzeltme_iste(self, kimlik: str, not_: str) -> None:
        if not not_.strip():
            raise ValueError("Düzeltme notu boş olamaz.")
        if kimlik not in S.ASAMALAR or self.asama_durumu(kimlik)["durum"] != "onay_bekliyor":
            raise ValueError("Bu adım şu an düzeltme alamaz.")
        asama = S.ASAMALAR[kimlik]
        mesaj = f"{K.duzeltme_basligi(asama.onay)}: {not_.strip()}"
        elle = self.asama_durumu(kimlik).get("elle_bekleyen") or []
        if elle:
            # Model kendi eski hâlini bilir; kullanıcının elle yaptığı değişiklikler ezilmesin diye güncel hâl verilir.
            belgeler = "\n\n".join(S.belge(ad, self.oku(ad)) for ad in elle
                                     if (kanal.arsiv_klasoru(self.kod) / ad).exists())
            mesaj = ("Kullanıcı şu dosyaları elle düzenledi; güncel hâlleri aşağıda. Yamaların paragraf/satır "
                     "numaraları bu güncel hâle göre olsun ve kullanıcının değişikliklerini koru.\n\n"
                     f"{belgeler}\n\n{mesaj}")
            self._durum_yaz(kimlik, elle_bekleyen=[])
        self._baslat(self._calistir, kimlik, mesaj, False)

    # --- elle düzenleme (model çağrılmaz, kredi harcanmaz) ---------------------
    def _elle_kontrol(self, kimlik: str, ad: str) -> S.Asama:
        if kimlik not in S.ASAMALAR:
            raise ValueError("Bu adımın metni düzenlenemez.")
        if self.calisiyor() or self.asama_durumu(kimlik)["durum"] != "onay_bekliyor":
            raise ValueError("Metin yalnız aşama onay beklerken düzenlenebilir.")
        asama = S.ASAMALAR[kimlik]
        if ad not in asama.ciktilar(self.kod):
            raise ValueError("Bu dosya bu aşamaya ait değil.")
        return asama

    def elle_duzenle(self, kimlik: str, ad: str, icerik: str) -> dict:
        """Kullanıcının düzenlediği metni yazar, sonuç dosyalarını ve kod kontrollerini yeniler.
        Modelin yazdığı hâl ilk düzenlemede _uygulama/elle_yedek/ altına saklanır (silinmez)."""
        asama = self._elle_kontrol(kimlik, ad)
        icerik = icerik.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"
        icerik = K.ic_isaretleri_temizle(icerik)[0]
        if not icerik.strip():
            raise ValueError("Metin boş olamaz.")
        eski = self.oku(ad)
        s = self.asama_durumu(kimlik)
        yedekler = s.setdefault("elle_yedek", {})
        if ad not in yedekler:
            yedek = kanal.uygulama_klasoru(self.kod) / "elle_yedek" / f"{kimlik}_{_simdi().replace(':', '-')}_{ad}"
            A.atomik_yaz(yedek, eski)
            yedekler[ad] = str(yedek)
        if icerik != eski:
            self._yaz(ad, icerik)
            if ad not in (s.get("elle_bekleyen") or []):
                s["elle_bekleyen"] = (s.get("elle_bekleyen") or []) + [ad]
            s.setdefault("degisiklikler", []).append(f"{ad.replace(self.kod + '_', '')}: elle düzenlendi")
            kayit.yaz(f"{self.kod} {kimlik}: {ad} elle düzenlendi")
        return self._elle_yenile(asama)

    def elle_geri_al(self, kimlik: str, ad: str) -> dict:
        """Modelin yazdığı (ilk düzenlemeden önceki) hâle döner."""
        self._elle_kontrol(kimlik, ad)
        yedek = (self.asama_durumu(kimlik).get("elle_yedek") or {}).get(ad)
        if not yedek or not Path(yedek).exists():
            raise ValueError("Bu dosya elle düzenlenmemiş.")
        return self.elle_duzenle(kimlik, ad, Path(yedek).read_text(encoding="utf-8"))

    def _elle_yenile(self, asama: S.Asama) -> dict:
        self._hazir_kuyruk(asama)
        self._sonuc_dosyalarini_yaz(asama)  # ör. Aşama 5 → 02_ElevenLabs_seslendirme_metni.txt
        sonuc = S.kontrol(asama, self.kod, self.oku)
        dosyalar = {ad: _ozet_hash(self.oku(ad)) for ad in asama.ciktilar(self.kod)
                    if (kanal.arsiv_klasoru(self.kod) / ad).exists()}
        self._durum_yaz(asama.kimlik, kontrol=sonuc.sozluk(), dosyalar=dosyalar)
        return sonuc.sozluk()

    def tekrar_dene(self, butce_onayli: bool = False) -> None:
        kimlik = next((k for k in S.sira(self.d) if self.asama_durumu(k)["durum"] in ("hata", "butce_sorusu")), None)
        if not kimlik:
            raise ValueError("Tekrar denenecek adım yok.")
        self.baslat(kimlik, butce_onayli)

    def devam(self) -> None:
        """Bekleyen bir kod adımını sürdürür (ör. CapCut kapatıldı, Flow görselleri kontrol edilsin)."""
        kimlik = self.d["adim"]
        if kimlik not in ADIM_ISLEVLERI:
            raise ValueError("Bu adımda devam edilecek bir şey yok.")
        self.baslat(kimlik)

    # --- Flow'a özel kullanıcı eylemleri ---
    def flow_sorun_devam(self) -> None:
        flow.sinyal_arsivle(self.kod)
        self._durum_yaz("FLOW", durum="bekleme", sorun="")

    def flow_a5_duzeltme(self, not_: str) -> None:
        if not not_.strip():
            raise ValueError("Düzeltme notu boş olamaz.")
        flow.sinyal_arsivle(self.kod)
        self.d["donus_adimi"] = "FLOW"
        self._durum_yaz("FLOW", durum="bekliyor", sorun="")
        self.asama_durumu("A5").update(durum="onay_bekliyor")
        self.d["adim"] = "A5"
        self.kaydet()
        self.duzeltme_iste("A5", "Flow'da sorun çıktı. " + not_.strip())

    def muzik_yenile(self) -> str:
        """CapCut taslağı oluştuktan sonra müziği yeni rastgele parçalarla yeniden yapar (eski hâl arşive)."""
        if self.calisiyor():
            raise ValueError("Şu an bir adım çalışıyor; bitmesini bekle.")
        if self.asama_durumu("CAPCUT").get("durum") != "tamam":
            raise ValueError("Müzik, CapCut taslağı oluştuktan sonra yeniden yapılabilir.")
        try:
            secilen = C.muzik_yenile(self.kod)
        except araclar.AracHatasi as e:
            raise ValueError(str(e))
        self._sonuc(muzik=secilen)
        kayit.yaz(f"{self.kod}: müzik yeniden yapıldı · {secilen}")
        return secilen

    def silme_karari(self, tasi: bool) -> list[str]:
        adaylar = [Path(p) for p in self.d.get("silme_adaylari", [])]
        tasinan = dosya_duzeni.silineceklere_tasi(self.kod, adaylar) if tasi else []
        self.d["silme_adaylari"] = []
        self.d["silme_karari"] = "Silinecekler'e taşındı" if tasi else "Kalsın"
        self.kaydet()
        return tasinan

    def kapat(self) -> None:
        """Üretimi kapatır. Cevaplanmamış silme adayları Silinecekler'e taşınır (SKILL A9)."""
        if self.d["adim"] != S.SON_ADIM:
            raise ValueError("Üretim henüz bitmedi.")
        if self.d.get("silme_adaylari"):
            self.silme_karari(True)
        _aktif_yaz(None)

    # --- yazı aşamaları ------------------------------------------------------
    def _calistir(self, kimlik: str, kullanici_mesaji: str | None, butce_onayli: bool) -> None:
        asama = S.ASAMALAR[kimlik]
        self._suren = kimlik
        self.ilerleme = 0
        self._durum_yaz(kimlik, durum="calisiyor", hata="", baslama=_simdi())
        konusma = A.json_oku(self._konusma_yolu(kimlik), None)
        # Maliyet dökümü için isteğin türü: ilk yazım / kullanıcı düzeltmesi / yarıda kalanı tekrar dene
        ilk_tur = "kullanici_duzeltme" if kullanici_mesaji else (
            "tekrar" if konusma is not None and self._yarim(konusma) else "ilk")
        if konusma is None or (kullanici_mesaji is None and not self._yarim(konusma)):
            girdi = {"studio_verisi": self.d.get("studio_verisi"), "konu_istegi": self.d.get("konu_istegi"),
                     "onay_notlari": self.d.get("onay_notlari", {}), "bolumler": self.d.get("bolumler", [])}
            konusma = {"sistem": S.sistem(asama),
                       "mesajlar": [{"role": "user", "content": S.ilk_mesaj(asama, self.kod, self.oku, girdi)}]}
            self._durum_yaz(kimlik, oto_tur=0, kullanici_tur=0, degisiklikler=[])
        elif kullanici_mesaji:
            konusma["mesajlar"].append({"role": "user", "content": kullanici_mesaji})
            s = self.asama_durumu(kimlik)
            self._durum_yaz(kimlik, oto_tur=0, kullanici_tur=s.get("kullanici_tur", 0) + 1, degisiklikler=[])
        A.json_yaz(self._konusma_yolu(kimlik), konusma)

        ayar = A.ayarlar()
        sinir = int(ayar["duzeltme_tur_siniri"])
        onay_ilk = True
        while True:
            oto = self.asama_durumu(kimlik).get("oto_tur", 0)
            # Ucuz model kontrolü geçemezse yedek model (ör. A6_2: Haiku → Sonnet).
            temel = "hazir" if kimlik in S.HAZIR else kimlik
            is_adi = f"{temel}_yedek" if oto >= 1 and f"{temel}_yedek" in ayar["isler"] else temel
            servis = self.llm.saglayici
            if konusma.get("saglayici", servis) != servis:
                konusma["mesajlar"] = dusunceleri_cikar(konusma["mesajlar"])
                kayit.yaz(f"{kimlik}: yazım servisi değişti ({konusma['saglayici']} → {servis}); "
                          "önceki düşünme notları gönderilmeyecek, yazılan metinler aynen kalıyor")
            konusma["saglayici"] = servis
            cevap = self.llm.istek(is_adi, self.kod, konusma["sistem"], konusma["mesajlar"],
                                   ilerleme=self._ilerle, butce_onayli=butce_onayli and onay_ilk,
                                   iptal=self._iptal_mi, tur=f"oto_duzeltme_{oto}" if oto else ilk_tur)
            onay_ilk = False
            konusma["mesajlar"] += cevap.ek_mesajlar + [{"role": "assistant", "content": cevap.icerik}]
            A.json_yaz(self._konusma_yolu(kimlik), konusma)
            s = self.asama_durumu(kimlik)
            s["usd"] = round(s.get("usd", 0) + cevap.usd, 4)
            s["model"] = cevap.yedek_model or cevap.model
            if cevap.yedek_model:
                s["yedek_model_notu"] = f"{cevap.model} reddetti, {cevap.yedek_model} yazdı."
            self._durum_yaz(kimlik, durum="kontrol")

            uygulama_hatalari = self._uygula(asama, cevap.metin)
            self._ic_isaretleri_temizle(asama)
            self._hazir_kuyruk(asama)
            self._sonuc_dosyalarini_yaz(asama)
            sonuc = S.kontrol(asama, self.kod, self.oku)
            sonuc.hatalar = uygulama_hatalari + sonuc.hatalar
            if sonuc.hatalar and oto < sinir:
                kayit.yaz(f"{kimlik}: kontrol {len(sonuc.hatalar)} sorun buldu, otomatik düzeltme {oto + 1}/{sinir}")
                konusma["mesajlar"].append({"role": "user", "content": K.duzeltme_mesaji(asama.onay, sonuc)})
                A.json_yaz(self._konusma_yolu(kimlik), konusma)
                self._durum_yaz(kimlik, durum="calisiyor", oto_tur=oto + 1)
                continue
            dosyalar = {ad: _ozet_hash(self.oku(ad)) for ad in asama.ciktilar(self.kod)
                        if (kanal.arsiv_klasoru(self.kod) / ad).exists()}
            ay = cikti.ayristir(cevap.metin)
            acik = ay.acik_noktalar or self.asama_durumu(kimlik).get("acik_noktalar", "")
            self._durum_yaz(kimlik, durum="onay_bekliyor", kontrol=sonuc.sozluk(), ozet=ay.ozet,
                            acik_noktalar=acik, dosyalar=dosyalar, bitis=_simdi())
            if not S.onay_gerekli(asama, self.d) and sonuc.temiz:
                # ONAY'sız aşama (5, 6_2) ya da kanal ayarında onayı kapatılmış aşama: kontroller temizse geçilir.
                sonraki = self._tamamla(kimlik)
                return self._zincir(sonraki)
            kayit.yaz(f"{self.kod} {kimlik}: onay bekliyor ({'temiz' if sonuc.temiz else 'çözülemeyen sorun var'})")
            return

    def _zincir(self, sonraki: str) -> None:
        """Aynı iş parçacığında sonraki adımı çalıştırır (Durdur istendiyse sonraki adım başlamaz)."""
        if self._durdur:
            kayit.yaz(f"{self.kod}: durduruldu; sıradaki adım ({S.adim_adlari().get(sonraki, sonraki)}) bekliyor")
            return
        if sonraki in S.ASAMALAR:
            return self._calistir(sonraki, None, False)
        if sonraki in ADIM_ISLEVLERI:
            return self._adim(sonraki, False)

    def _ic_isaretleri_temizle(self, asama: S.Asama) -> None:
        for ad in asama.ciktilar(self.kod):
            yol = kanal.arsiv_klasoru(self.kod) / ad
            if not yol.exists():
                continue
            yeni, n = K.ic_isaretleri_temizle(yol.read_text(encoding="utf-8"))
            if n:
                self._yaz(ad, yeni)
                kayit.yaz(f"{self.kod} {asama.kimlik}: {ad} içinden {n} eski iç işaret ([... NEEDED]) çıkarıldı", "uyari")

    def _hazir_kuyruk(self, asama: S.Asama) -> None:
        """Hazır metin aşamasında teslim satırını kod yazar (kelime/paragraf sayısı)."""
        if asama.kimlik not in S.HAZIR:
            return
        ad = asama.ciktilar(self.kod)[2]
        if not (kanal.arsiv_klasoru(self.kod) / ad).exists():
            return
        eski = self.oku(ad)
        yeni = K.hazir_kuyruk(eski, S.hazir_dil(asama.kimlik))
        if yeni != eski:
            self._yaz(ad, yeni)

    def _sonuc_dosyalarini_yaz(self, asama: S.Asama) -> None:
        """Videolar/<kod>/ sonuç dosyaları ve arşivdeki alışılmış kopyalar (çıktı eksikse atlanır)."""
        try:
            dosyalar = S.sonuc_dosyalari(asama, self.kod, self.oku)
        except FileNotFoundError:
            return
        for ad, icerik in dosyalar.items():
            A.atomik_yaz(kanal.video_klasoru(self.kod) / ad, icerik)
        for sonek, ad in S.ARSIV_KOPYALARI.get(asama.kimlik, {}).items():
            kaynak = kanal.arsiv_klasoru(self.kod) / (self.kod + sonek)
            if kaynak.exists():
                self._yaz(ad, kaynak.read_text(encoding="utf-8"))

    @staticmethod
    def _yarim(konusma: dict) -> bool:
        """Son mesaj kullanıcıdansa (cevap gelmeden kesildiyse) aynı konuşma sürdürülür."""
        return bool(konusma.get("mesajlar")) and konusma["mesajlar"][-1]["role"] == "user"

    def _ilerle(self, n: int) -> None:
        self.ilerleme = n

    def _uygula(self, asama: S.Asama, metin: str) -> list[str]:
        """Modelin dosyalarını/yamalarını arşive işler. Döner: modele iletilecek uygulama hataları."""
        beklenen = asama.ciktilar(self.kod)
        a = cikti.ayristir(metin, beklenen)
        hatalar: list[str] = []
        degisiklikler = self.asama_durumu(asama.kimlik).setdefault("degisiklikler", [])

        def eslestir(ad: str) -> str | None:
            if ad in beklenen:
                return ad
            return next((b for b in beklenen if ad.endswith(b[len(self.kod):])), None)

        for ad, icerik in a.dosyalar.items():
            hedef = eslestir(ad)
            if not hedef:
                kayit.yaz(f"{asama.kimlik}: beklenmeyen dosya adı yok sayıldı: {ad}", "uyari")
                continue
            self._yaz(hedef, icerik)
            degisiklikler.append(f"{hedef}: tam dosya")
        for ad, yamalar in a.yamalar.items():
            hedef = eslestir(ad)
            if not hedef:
                hatalar.append(f"Yama bilinmeyen dosyaya: {ad}")
                continue
            try:
                yeni = M.yama_uygula(self.oku(hedef), yamalar)
            except FileNotFoundError:
                hatalar.append(f"{hedef} henüz yok; önce tam dosyayı <dosya> ile ver.")
                continue
            except M.YamaHatasi as e:
                hatalar.append(f"{hedef}: yama uygulanamadı ({e}).")
                continue
            self._yaz(hedef, yeni)
            for y in yamalar:
                yer = (f"¶{y['paragraf']} ({y.get('islem', 'degistir')})" if "paragraf" in y
                       else y.get("satir") or y.get("bolum") or "teslim satırları")
                degisiklikler.append(f"{hedef}: {yer}")
        self.kaydet()
        return hatalar

    # --- kod/araç adımları ---------------------------------------------------
    def _adim(self, kimlik: str, butce_onayli: bool = False) -> None:
        self._suren = kimlik
        self._durum_yaz(kimlik, durum="calisiyor", hata="", baslama=self.asama_durumu(kimlik).get("baslama") or _simdi())
        bitti = ADIM_ISLEVLERI[kimlik](self)
        if bitti:
            self._zincir(self._tamamla(kimlik))

    def _kabul_edildi(self, kimlik: str, anahtar: str) -> bool:
        return f"{kimlik}:{anahtar}" in self.d.get("kabuller", [])

    def _flow(self) -> bool:
        """İstek klasörünü hazırlar, bekler; BITTI.json/kullanıcı kontrolüyle doğrular ve içe alır."""
        k = flow.istek_klasoru(self.kod)
        kart = self.oku(self.kod + "_1_konu_karti.md")
        if not (k / "istek.json").exists() or self.d.pop("flow_yeniden", False):
            degisen = sorted({int(m.group(1)) for x in self.asama_durumu("A5").get("degisiklikler", [])
                              for m in [re.search(r"_5B_gorsel_promptlari\.txt: ¶(\d+)", x)] if m})
            onceki = self.asama_durumu("FLOW").get("eksik", [])
            sadece = sorted(set(degisen) | set(onceki)) if (degisen or onceki) and (k / "istek.json").exists() else None
            flow.istek_hazirla(self.kod, ST.kisa_konu(kart), sadece)
            kayit.yaz(f"{self.kod}: Flow istek klasörü hazırlandı" + (f" (yalnız {len(sadece)} sahne)" if sadece else ""))
        dd = flow.durum(self.kod)
        if dd.get("sorun"):
            self._durum_yaz("FLOW", durum="bekleme", sorun=dd["sorun"])
            return False
        if not dd.get("bitti") and not self.asama_durumu("FLOW").get("elle_kontrol"):
            self._durum_yaz("FLOW", durum="bekleme", komut=flow.ajan_komutu(self.kod), klasor=str(k),
                            cikti=str(flow.cikti_klasoru(self.kod)))
            return False
        self.asama_durumu("FLOW")["elle_kontrol"] = False
        self._bilgi("Görseller kontrol ediliyor…")
        try:
            sonuc = flow.dogrula(self.kod)
        except ValueError as e:
            self._durum_yaz("FLOW", durum="bekleme", sorun="", uyari=str(e))
            return False
        if not sonuc["tamam"]:
            flow.sinyal_arsivle(self.kod)
            flow.istek_hazirla(self.kod, ST.kisa_konu(kart), sonuc["eksik"])
            self._durum_yaz("FLOW", durum="bekleme", eksik=sonuc["eksik"], boyut=sonuc["boyut"], cift=sonuc["cift"],
                            uyari=f"{len(sonuc['eksik'])} sahne eksik ya da hatalı. Ajana yalnız eksikleri üretmesini söyle.")
            return False
        flow.ice_al(self.kod, sonuc["secilen"])
        self._durum_yaz("FLOW", eksik=[], uyari="", cift=sonuc["cift"])
        self._sonuc(flow_gorsel=sonuc["toplam"])
        return True

    def flow_elle_kontrol(self) -> None:
        self.asama_durumu("FLOW")["elle_kontrol"] = True
        self.kaydet()
        self.baslat("FLOW")

    def _studio(self) -> bool:
        kart = self.oku(self.kod + "_1_konu_karti.md")
        metin_ = (kanal.video_klasoru(self.kod) / "02_ElevenLabs_seslendirme_metni.txt").read_text(encoding="utf-8")
        n = len(K.bloklar(metin_))
        sorun = K.elevenlabs_metni(metin_)
        if sorun:  # seslendirme hiç başlamadan durur: kredi harcanmaz
            raise ST.StudioHatasi("Seslendirme başlatılmadı. ElevenLabs metninde izin verilmeyen köşeli not var "
                                  f"(izinli tag'ler: {K.izinli_tag_metni()}): "
                                  + "; ".join(sorun[:8]) + ". Aşama 5'in seslendirme metnini düzelt, sonra Tekrar dene.")
        self._durum_yaz("STUDIO", uyari="")
        self._bilgi("Ses ve sahne videoları hazırlanıyor…")
        cid, vid = ST.video_bul_ya_da_olustur(self.kod, f"{self.kod} {ST.kisa_konu(kart)}".strip(), self.d.get("studio_vid"))
        self.d["studio_vid"] = vid
        self.kaydet()
        klasor = ST.video_klasoru(cid, vid)
        ST.kilit_al(klasor, self.kod)
        try:
            return self._studio_uret(cid, vid, metin_, n, klasor)
        finally:
            ST.kilit_birak(klasor)

    def _hiz_olc(self, vid: str) -> None:
        """Gerçek ses süresinden kanalın konuşma hızını öğrenir (kelime sayısı otomatikse sonraki videolar buna göre
        hesaplanır). Ölçüm üretimi hiçbir zaman durdurmaz."""
        try:
            o = ST.ses_olcumu(vid)
            if o:
                kanallar.hiz_kaydet(kanal.secili(), self.kod, kanal.hedef_dil(), o[0], o[1],
                                    kanal.ayar()["ses"].get("speed") or 1)
        except Exception as e:  # noqa: BLE001
            kayit.yaz(f"Konuşma hızı ölçülemedi: {e}", "uyari")

    def _studio_uret(self, cid: str, vid: str, metin_: str, n: int, klasor: Path) -> bool:
        ST.metin_ver(cid, vid, metin_, n)
        sayim = ST.gorselleri_koy(cid, vid, flow.secilenler_klasorden(self.kod))
        kayit.yaz(f"Sahne görselleri: {sayim['matched']} eşleşen, {sayim['missing']} eksik")
        tekrar = self.asama_durumu("STUDIO").get("deneme", 0) > 0
        self._durum_yaz("STUDIO", deneme=self.asama_durumu("STUDIO").get("deneme", 0) + 1)
        j = ST.is_calistir("tts", cid, vid, self._bilgi, tekrar, self._iptal_mi)
        if j["failed"]:
            raise ST.StudioHatasi(f"Ses: {j['ok']} başarılı, {j['failed']} hatalı. Tekrar dene hatalıları yeniden dener "
                                  "(önce mevcut AI84 işini ücretsiz sorgular).")
        self._hiz_olc(vid)
        ST.son_kontrol(cid, vid)
        self._durdur_kontrol()
        j = ST.is_calistir("render", cid, vid, self._bilgi, tekrar, self._iptal_mi)
        if j["failed"]:
            raise ST.StudioHatasi(f"Sahne videosu: {j['ok']} başarılı, {j['failed']} hatalı. Tekrar dene.")
        v = ST.videolari_dogrula(klasor, n)
        if v["sorunlar"]:
            raise ST.StudioHatasi("Sahne videosu kontrolü: " + "; ".join(v["sorunlar"][:5]))
        ko = ST.kenar_ozeti(vid)
        if ko:  # sahne kenarı kontrolü (kesik "dit"): sonrası 0 sert / 0 orta değilse adım tamamlanmaz
            kayit.yaz("Ses kenarı: " + ko["metin"], "bilgi" if ko["temiz"] else "uyari")
            self._sonuc(ses_kenar=ko["metin"])
            if not ko["temiz"] and not self._kabul_edildi("STUDIO", "kenar"):
                self._durum_yaz("STUDIO", durum="onay_bekliyor", kabul_anahtari="kenar",
                                kontrol={"hatalar": ["Sahne sonunda kesik kaldı: " + x for x in ko["kalan"]],
                                         "uyarilar": [], "bilgiler": [ko["metin"]]},
                                ozet="Ses kenarı kontrolü temiz değil. CapCut'ta bu sahnelerin sonunu dinle. "
                                     "Sorun yoksa Yine de devam et.")
                return False
        self._sonuc(sahne=n, sure_sn=v["sure"], sure=ST.sure_metni(v["sure"]), video_klasoru=str(klasor))
        kanal.liste_guncelle(self.kod, durum="Sahne videoları hazır", sahne=n, sure=ST.sure_metni(v["sure"]))
        return True

    def _capcut(self) -> bool:
        if C.capcut_acik():
            self._durum_yaz("CAPCUT", durum="bekleme", uyari="CapCut açık. CapCut'ı kapat, sonra Devam'a bas.")
            return False
        self._durum_yaz("CAPCUT", uyari="")
        video = Path(self.d["sonuclar"]["video_klasoru"])
        alt = self.d.setdefault("capcut_alt", {})
        if "srt" not in alt:
            self._bilgi("Altyazı üretiliyor…")
            alt["srt"] = C.srt(self.kod, video)
            self.kaydet()
        self._durdur_kontrol()
        if "odak" not in alt:
            alt["odak"] = C.odak(self.kod, video, self.llm, self._bilgi)
            self.kaydet()
        self._durdur_kontrol()
        if "taslak" not in alt:
            self._bilgi("CapCut taslağı kuruluyor…")
            alt["taslak"] = C.taslak(self.kod, video)
            self.kaydet()
        self._durdur_kontrol()
        if "senk1" not in alt:
            self._bilgi("Senkron kontrolü…")
            sk = C.senk(self.kod, metin=True)
            if sk["sorunlar"] and not self._kabul_edildi("CAPCUT", "senk1"):
                self._durum_yaz("CAPCUT", durum="onay_bekliyor", kabul_anahtari="senk1",
                                kontrol={"hatalar": sk["sorunlar"], "uyarilar": sk["normal"], "bilgiler": []},
                                ozet=sk["ozet"])
                return False
            alt["senk1"] = {"temiz": sk["temiz"], "normal": len(sk["normal"]), "sorun": len(sk["sorunlar"])}
            self.kaydet()
        self._durdur_kontrol()
        if "yayin" not in alt:
            self._bilgi("Yayın öncesi son dokunuş: müzik, maskotlar, son ekran (birkaç dakika)…")
            alt["yayin"] = C.yayin_hazirla(self.kod, self.d.get("maskot_argumanlari", ""))
            self.kaydet()
        self._durdur_kontrol()
        if "senk2" not in alt:
            self._bilgi("Son senkron kontrolü…")
            sk = C.senk(self.kod)
            if sk["sorunlar"] and not self._kabul_edildi("CAPCUT", "senk2"):
                self._durum_yaz("CAPCUT", durum="onay_bekliyor", kabul_anahtari="senk2",
                                kontrol={"hatalar": sk["sorunlar"], "uyarilar": sk["normal"], "bilgiler": [sk["son_ekran"]]},
                                ozet=sk["ozet"])
                return False
            alt["senk2"] = {"temiz": sk["temiz"], "son_ekran": sk["son_ekran"], "sorun": len(sk["sorunlar"])}
            self.kaydet()
        self.d["bolumler"] = C.bolum_zamanlari(self.kod)
        self._sonuc(srt_satir=alt["srt"].get("satir"), muzik=alt["yayin"].get("secilen", ""),
                    maskot=self.d.get("maskot_argumanlari", ""),
                    odak=f"{alt['odak']['sahne']} sahne" + (f", varsayılan: {', '.join(alt['odak']['varsayilan'])}"
                                                           if alt['odak']['varsayilan'] else ""),
                    senk="TEMIZ" if alt["senk2"]["temiz"] else f"{alt['senk2']['sorun']} not (kabul edildi)")
        kanal.liste_guncelle(self.kod, durum="CapCut'ta hazır")
        return True

    def _son(self) -> bool:
        self._bilgi("Sahne–görsel uyumu kontrol ediliyor…")
        uyum = son_kontrol.gorsel_uyum(self.kod, self.llm)
        k = self.asama_durumu("A6_2").get("kontrol") or {}
        veri = dict(self.d.get("sonuclar", {}))
        veri["baslik"] = self._baslik()
        veri["hassas"] = "TEMIZ" if "hassas_kelime_kontrol: TEMIZ" in k.get("bilgiler", []) else \
            f"{len(k.get('uyarilar', []))} uyarı"
        veri["uyarilar"] = k.get("uyarilar", []) + self.asama_durumu("FLOW").get("cift", [])
        if self.d.get("hazir_dil"):
            veri["baslangic"] = (f"hazır metinle başladı ({kanal.dil_adi(self.d['hazir_dil'])}); atlanan aşamalar: "
                                 + ", ".join(S.adim_adlari()[k] for k in S.gorunum_sirasi(self.d)
                                             if self.asama_durumu(k).get("durum") == "atlandi"))
        kapali = [f"ONAY {S.ASAMALAR[k].onay}" for k in S.ONAY_SECILEBILIR
                  if k in S.sira(self.d) and not S.onay_gerekli(S.ASAMALAR[k], self.d)]
        if kapali:
            veri["onaysiz"] = ", ".join(kapali)
        self._bilgi("Rapor yazılıyor…")
        ozet = son_kontrol.rapor_yaz(self.kod, veri, uyum, self.llm)
        self._sonuc(rapor_ozet=ozet, uyum_sorunlu=len(uyum))
        return True

    def _kapanis(self) -> bool:
        self._bilgi("Açılış–kapanış defteri güncelleniyor…")
        ak = araclar.acilis_kapanis()
        r = self.d.get("sonuclar", {})
        sure_sahne = f"{r.get('sure', '?')} / {r.get('sahne', '?')}"
        if not self.d.get("defter_tamam"):
            self._bilgi("Kanal Defteri yenileniyor…")
            sonuc = defter.yenile(self.llm, self.kod, sure_sahne, ak, ilerleme=self._ilerle)
            self.d["defter_tamam"] = True
            self._sonuc(defter="yenilendi" if sonuc["tamam"] else
                        "kontrolden geçmedi; eski defter duruyor, aday Arsiv'de (02_Defter_yeni_aday_KONTROLDEN_GECMEDI.md)")
        tasinan = dosya_duzeni.fazlalari_arsive_tasi(self.kod)
        self.d["silme_adaylari"] = [str(p) for p in dosya_duzeni.silme_adaylari(self.kod)]
        kanal.liste_guncelle(self.kod, durum="CapCut'ta hazır", baslik=self._baslik(), sure=r.get("sure", ""),
                             sahne=r.get("sahne"))
        try:  # son iş: defter dahil bütün harcamaların dökümü
            A.atomik_yaz(kanal.arsiv_klasoru(self.kod) / "MALIYET.md", maliyet.dokum(self.kod))
        except Exception as e:
            kayit.yaz(f"Maliyet dökümü yazılamadı: {e}", "uyari")
        self._sonuc(arsive_tasinan=tasinan)
        return True

    def _baslik(self) -> str:
        return baslik_bul(self.kod, self.oku)

    # --- Flow izleyicisi ------------------------------------------------------
    def izleyici_baslat(self) -> None:
        """Uygulama açıkken Flow çıktı klasörünü 5 sn'de bir izler; BITTI.json gelince doğrulamayı başlatır."""
        if self._izleyici and self._izleyici.is_alive():
            return

        def dongu():
            while (_aktif_uretim() or {}).get("kod") == self.kod:
                try:
                    if self.d["adim"] == "FLOW" and not self.calisiyor() and \
                            self.asama_durumu("FLOW")["durum"] == "bekleme":
                        dd = flow.durum(self.kod)
                        if dd.get("bitti") or (dd.get("sorun") and not self.asama_durumu("FLOW").get("sorun")):
                            self.baslat("FLOW")
                except Exception as e:  # izleyici asla düşmesin
                    kayit.yaz(f"Flow izleyici: {e}", "uyari")
                time.sleep(5)

        self._izleyici = threading.Thread(target=dongu, daemon=True)
        self._izleyici.start()

    def ozet(self) -> dict:
        ek = {}
        if self.d["adim"] == "FLOW":
            ek["flow"] = flow.durum(self.kod)
        return {"kod": self.kod, "durum": self.d, "calisiyor": self.calisiyor(), "ilerleme": self.ilerleme,
                "ilerleme_metni": self.ilerleme_metni, "maliyet": maliyet.ozet(self.kod), **ek}


ADIM_ISLEVLERI = {"FLOW": Uretim._flow, "STUDIO": Uretim._studio, "CAPCUT": Uretim._capcut,
                  "SON": Uretim._son, "KAPANIS": Uretim._kapanis}
```

### `app/kanal_studyosu/yollar.py`

```python
"""Kurulum klasörü ve uygulamanın kendi klasörleri.

Uygulama, kullanıcının seçtiği klasöre kopyalanır; ilk açılışta o klasörün içinde Sistem/ ve Kanallar/ kurulur.
Kök klasör sırasıyla: KANAL_STUDYOSU_KOK ortam değişkeni (başlatıcı .app'in bulunduğu klasörü verir) → geliştirme
sırasında depo içindeki calisma/ klasörü.
"""
from __future__ import annotations

import os
from pathlib import Path

KAYNAK = Path(__file__).resolve().parent.parent          # program dosyaları (config/, sablonlar/)
CONFIG = KAYNAK / "config"
SABLONLAR = KAYNAK / "sablonlar"


def kok() -> Path:
    return Path(os.environ.get("KANAL_STUDYOSU_KOK") or (KAYNAK / "calisma")).expanduser().resolve()


def sistem() -> Path:
    return kok() / "Sistem"


def kanallar() -> Path:
    return kok() / "Kanallar"


def ayar_dosyasi() -> Path:
    return sistem() / "ayarlar.json"


def maliyet_dosyasi() -> Path:
    return sistem() / "maliyet.jsonl"


def aktif_dosyasi() -> Path:
    return sistem() / "aktif.json"


def calisan_dosyasi() -> Path:
    """Açık kopyanın adresi (tek_kopya)."""
    return sistem() / "calisan.json"


def kayit_dosyasi() -> Path:
    return sistem() / "kayit.log"


def kur() -> list[str]:
    """İlk açılışta (ve her açılışta, eksikse) klasör düzenini kurar. Var olan hiçbir şeye dokunmaz."""
    olusan = []
    for k in (sistem(), kanallar()):
        if not k.exists():
            k.mkdir(parents=True)
            olusan.append(str(k))
    return olusan
```

### `app/kanal_studyosu/web/index.html`

```html
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kanal Stüdyosu</title>
<link rel="stylesheet" href="/stil.css">
<script>window.TOKEN = "__TOKEN__";</script>
</head>
<body>
<header class="ust">
  <div class="marka"><span class="logo">K</span><span>Kanal Stüdyosu</span></div>
  <div class="ust-sag">
    <button id="bakiye" class="maliyet bakiye" data-eylem="bakiye" title="Kalan bakiye · tıkla: yenile" hidden></button>
    <div id="maliyet" class="maliyet" title="Tahmini API harcaması"></div>
    <div class="kanal-sec" id="kanal-sec"></div>
    <button class="dugme ince" data-eylem="kanal-ekle">+ Kanal ekle</button>
    <button class="dugme ince" data-eylem="ayarlar">Ayarlar</button>
    <button class="dugme ince" data-eylem="kayit">Kayıt</button>
    <button class="dugme ince tehlike" data-eylem="kapat">Kapat</button>
  </div>
</header>
<main id="ana" class="ana"><p class="soluk">Yükleniyor…</p></main>

<dialog id="buyuk-pencere" class="pencere buyuk-pencere">
  <div class="satir" style="justify-content:space-between;margin-bottom:8px"><strong id="buyuk-baslik">Metin</strong>
    <div class="satir" style="gap:6px"><button class="dugme ince" data-eylem="buyuk-kopyala">Kopyala</button>
    <button class="dugme ince" data-eylem="buyuk-kapat">Kapat</button></div></div>
  <pre id="buyuk-icerik"></pre>
</dialog>
<dialog id="kanal-pencere" class="pencere buyuk-pencere"><div id="kanal-formu"></div></dialog>
<dialog id="ayar-penceresi" class="pencere"><form method="dialog" id="ayar-formu"></form></dialog>
<dialog id="sil-pencere" class="pencere"><div id="sil-icerik"></div></dialog>
<dialog id="dosya-pencere" class="pencere buyuk-pencere"><div id="dosya-icerik"></div></dialog>

<aside id="kayit-paneli" class="kayit-paneli" hidden>
  <div class="kayit-baslik"><strong>Kayıt</strong>
    <div class="satir" style="gap:6px">
      <label class="kucuk soluk" style="display:flex;align-items:center;gap:4px;margin:0"><input type="checkbox" id="kayit-hata"> Yalnız hata/uyarı</label>
      <button class="dugme ince" data-eylem="kayit-kopyala">Kopyala</button>
      <button class="dugme ince" data-eylem="kayit-son-hata">Son hatayı kopyala</button>
      <button class="dugme ince" data-eylem="kayit-dosya" title="Bütün geçmiş, uygulama kapansa da silinmez">Tüm geçmişi aç</button>
      <button class="dugme ince" data-eylem="kayit-buyut">Büyüt</button>
      <button class="dugme ince" data-eylem="kayit">Kapat</button></div></div>
  <pre id="kayit-icerik"></pre>
  <div id="kayit-asagi" class="kayit-asagi" hidden><button class="dugme ince" data-eylem="kayit-en-alt">↓ En yeni satırlar</button></div>
</aside>
<div id="bildirim" class="bildirim" hidden></div>
<script src="/app.js"></script>
</body>
</html>
```

### `app/kanal_studyosu/web/app.js`

```javascript
"use strict";
// Kanal Stüdyosu arayüzü. Durum /api/durum'dan okunur; ekran yalnızca durum değiştiğinde yeniden çizilir.

const $ = (s, k = document) => k.querySelector(s);
const kacir = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let D = null;
let imza = "";

async function api(yol, govde) {
  const r = await fetch(yol, {
    method: govde === undefined ? "GET" : "POST",
    headers: { "X-App-Token": window.TOKEN, "Content-Type": "application/json" },
    body: govde === undefined ? undefined : JSON.stringify(govde),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.hata || "İşlem yapılamadı");
  return j;
}

function bildir(m) {
  const b = $("#bildirim");
  b.textContent = m; b.hidden = false;
  clearTimeout(bildir.t); bildir.t = setTimeout(() => (b.hidden = true), 5000);
}

async function yap(fn) {
  try { await fn(); await yenile(true); } catch (e) { bildir(e.message); }
}

async function kopyala(metin) {
  try { await navigator.clipboard.writeText(metin); bildir("Kopyalandı."); }
  catch { const t = document.createElement("textarea"); t.value = metin; document.body.appendChild(t); t.select(); document.execCommand("copy"); t.remove(); bildir("Kopyalandı."); }
}

// --- değer yolları (ör. "uzunluk.hedef_kelime.0") ---------------------------

function al(o, yol) { return yol.split(".").reduce((x, p) => (x == null ? undefined : x[p]), o); }
function koy(o, yol, v) {
  const p = yol.split(".");
  let x = o;
  p.slice(0, -1).forEach((k, i) => { if (x[k] == null) x[k] = /^\d+$/.test(p[i + 1]) ? [] : {}; x = x[k]; });
  x[p[p.length - 1]] = v;
}
const kopya = (o) => JSON.parse(JSON.stringify(o));

function kisaltmaOner(ad) {
  const tr = { ç: "c", ğ: "g", ı: "i", İ: "i", ö: "o", ş: "s", ü: "u", â: "a", î: "i", û: "u" };
  return ad.toLowerCase().replace(/[çğıİöşüâîû]/g, (c) => tr[c] || c).normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 31);
}

// --- kanal formu (sihirbaz ve ayarlar aynı alanları kullanır) ----------------

const IS_ADLARI = { hazir: "Hazır metin", konu: "1 Konu", arastirma: "2 Araştırma", senaryo: "3 Senaryo (TR)", ceviri: "4 Hedef dil", sahne: "5 Sahne paketi", paketleme: "6 Paketleme", bolumler: "6 Bölümler", defter: "Defter yenileme", uyum: "Sahne–görsel uyumu", rapor: "Rapor özeti", odak: "Odak noktası" };

function bolumler() {
  const diller = Object.entries(D.diller);
  return [
    { baslik: "1 · Kimlik", alanlar: [
      { yol: "ad", etiket: "Kanal adı", tur: "metin", ornek: "ör. Bilim Kahvesi" },
      { yol: "kisaltma", etiket: "Kısaltma (klasör adı)", tur: "metin", yalnizEkle: true, aciklama: "Kanallar/ altındaki klasörün adı. Küçük harf, rakam ve tire. Sonradan değişmez." },
      { yol: "kod_oneki", etiket: "Video kodu öneki", tur: "metin", ornek: "ör. BK", aciklama: "Videolar ÖNEK-01, ÖNEK-02… diye adlanır. İlk video üretildikten sonra değişmez." },
      { yol: "kod_hane", etiket: "Numara hanesi", tur: "secim", secenekler: [[2, "2 (01, 02…)"], [3, "3 (001, 002…)"]], gelismis: true },
    ] },
    { baslik: "2 · Dil ve uzunluk", alanlar: [
      { yol: "dil.hedef", etiket: "Videonun dili (hedef dil)", tur: "secim", secenekler: diller, aciklama: "Konu, araştırma ve senaryo Türkçe yazılır; senaryo bu dilde yeniden yazılır, bu dilde seslendirilir. Türkçe seçilirse 4. aşama atlanır." },
      { yol: "uzunluk.hedef_dk", etiket: "Hedef süre (dk)", tur: "sayi" },
      { tur: "kelime_bilgi" },
      { yol: "uzunluk.kelime_otomatik", etiket: "Kelime sayısını uygulama hesaplasın (önerilir)", tur: "onay", gelismis: true, aciklama: "Süre × dilin konuşma hızı; her videodan sonra gerçek ses süresiyle düzelir. Kapatırsan aşağıdaki sayılar kullanılır." },
      { cift: [{ yol: "uzunluk.calisma_kelime.0", etiket: "Türkçe senaryo · en az kelime", tur: "sayi" }, { yol: "uzunluk.calisma_kelime.1", etiket: "en çok kelime", tur: "sayi" }], gelismis: true, elleKelime: true },
      { cift: [{ yol: "uzunluk.hedef_kelime.0", etiket: "Hedef dil senaryo · en az kelime", tur: "sayi" }, { yol: "uzunluk.hedef_kelime.1", etiket: "en çok kelime", tur: "sayi" }], gelismis: true, elleKelime: true },
      { cift: [{ yol: "uzunluk.kart_karakter", etiket: "Konu kartı en fazla karakter", tur: "sayi" }, { yol: "uzunluk.hook_esigi", etiket: "Hook puanı eşiği (/10)", tur: "sayi" }], gelismis: true },
    ] },
    { baslik: "3 · Ses (ElevenLabs)", alanlar: [
      { cift: [{ yol: "ses.voice_id", etiket: "Ses kimliği (voice_id)", tur: "metin" }, { yol: "ses.voice_name", etiket: "Ses adı", tur: "metin" }], aciklama: "ElevenLabs'te sesin sayfasındaki kimlik. Üretim başlamadan önce gerekli." },
      { cift: [{ yol: "ses.model_id", etiket: "Model", tur: "metin" }, { yol: "ses.language_code", etiket: "Dil kodu", tur: "metin" }], gelismis: true },
      { cift: [{ yol: "ses.stability", etiket: "Stability (0–1)", tur: "sayi" }, { yol: "ses.similarity_boost", etiket: "Similarity (0–1)", tur: "sayi" }], gelismis: true },
      { cift: [{ yol: "ses.style", etiket: "Style (0–1)", tur: "sayi" }, { yol: "ses.speed", etiket: "Speed (0,7–1,2)", tur: "sayi" }], gelismis: true },
      { cift: [{ yol: "ses.output_format", etiket: "Çıkış biçimi", tur: "metin" }, { yol: "ses.use_speaker_boost", etiket: "Speaker boost", tur: "onay" }], gelismis: true },
    ] },
    { baslik: "4 · Görsel", alanlar: [
      { yol: "gorsel.karakter", etiket: "Flow karakter etiketi", tur: "metin", ornek: "ör. @Mira (yoksa boş)", aciklama: "Karakterli sahnelerin promptu bununla başlar." },
      { yol: "gorsel.kurallar", etiket: "Kanalın görsel kuralları", tur: "uzun", aciklama: "Son kontroldeki sahne–görsel uyum denetimine verilir (ör. 'çocuk figürü yok; yetişkinler arkadan')." },
      { yol: "gorsel.ifade_notu", etiket: "Karakterin yüz ifadesi notu (isteğe bağlı)", tur: "uzun", aciklama: "Sahne paketi aşamasına eklenir." },
      { yol: "gorsel.yasakli", etiket: "Flow yasaklı kelimeler", tur: "liste", aciklama: "Virgülle ayır. Görsel promptlarında geçerse kod kontrolü hata verir." },
      { yol: "gorsel.oran", etiket: "Görsel oranı", tur: "secim", secenekler: [["16:9", "16:9 yatay"], ["9:16", "9:16 dikey"]] },
      { yol: "gorsel.izinli_olumsuz", etiket: "İzinli olumsuzlamalar ('no …')", tur: "liste", gelismis: true },
      { yol: "gorsel.flow_model", etiket: "Flow modeli", tur: "metin", gelismis: true },
    ] },
    { baslik: "5 · Etiketler", alanlar: [
      { yol: "etiketler.senaryo.karakter", etiket: "Karakter sahnesi etiketi", tur: "metin", aciklama: "Senaryoda karakterli paragrafların başına köşeli parantezle yazılır, ör. [MIRA]." },
      { cift: [{ yol: "etiketler.senaryo.metafor", etiket: "Metafor sahnesi etiketi", tur: "metin" }, { yol: "etiketler.senaryo.sema", etiket: "Şema sahnesi etiketi", tur: "metin" }], gelismis: true },
      { yol: "etiketler.senaryo.ilk30", etiket: "İlk 30 sn etiketi", tur: "metin", gelismis: true },
      { yol: "etiketler.ses", etiket: "İzinli ses tag'leri (ElevenLabs)", tur: "liste", gelismis: true },
      { cift: [{ yol: "etiketler.ses_sinir", etiket: "Tag sınırları", tur: "sinir", aciklama: "ör. whispers:2" }, { yol: "etiketler.tag_orani", etiket: "Tag'li paragraf oranı üst sınırı (%)", tur: "sayi" }], gelismis: true },
      { yol: "hassas_kelimeler", etiket: "Hassas kelimeler (başlık, açıklama, ilk 30 sn)", tur: "liste", aciklama: "Hedef dilde, virgülle. Kelime kökü yazılabilir (ör. depress, trauma)." },
    ] },
    { baslik: "6 · Montaj", alanlar: [
      { yol: "montaj.muzik", etiket: "Arka plan müziği", tur: "onay", aciklama: "Müzik dosyaları kanal klasöründe Varliklar/Muzik'e konur; klasör boşsa video müziksiz olur." },
      { yol: "montaj.muzik_lufs", etiket: "Müzik seviyesi (LUFS)", tur: "sayi", gelismis: true },
      { yol: "montaj.son_ekran_sn", etiket: "Son ekran süresi (sn)", tur: "sayi" },
      { yol: "montaj.maskot.dosyalar", etiket: "Maskot dosyaları (Varliklar/Maskot içindeki adlar)", tur: "liste", aciklama: "Maskot yoksa boş bırak." },
      { yol: "montaj.maskot.sira", etiket: "Maskot sırası", tur: "liste", aciklama: "ör. M1, M2, M1, M2 (1. dosya = M1)." },
      { yol: "montaj.altyazi.yazi_tipi", etiket: "Altyazı yazı tipi", tur: "metin" },
      { cift: [{ yol: "montaj.altyazi.yazi", etiket: "Altyazı yazı rengi", tur: "renk" }, { yol: "montaj.altyazi.kutu", etiket: "Altyazı kutu rengi", tur: "renk" }] },
      { cift: [{ yol: "montaj.altyazi.boyut", etiket: "Altyazı boyutu", tur: "sayi" }, { yol: "montaj.altyazi.kutu_opaklik", etiket: "Kutu opaklığı (0–1)", tur: "sayi" }], gelismis: true },
      { yol: "imza", etiket: "Kapanış imzası (isteğe bağlı)", tur: "metin", ornek: "ör. …e insieme, ti ritroverai.", aciklama: "Her videonun sonunda değişmeden tekrar eden tek satır. Açılış–Kapanış Defteri'nde 'tek sabit satır' olarak geçer." },
      { yol: "kalip_sayaclari", etiket: "Kalıp sayaçları (isteğe bağlı)", tur: "kalip", aciklama: "Açılış–Kapanış Defteri'nde sayılan tekrar kalıpları. Her satıra bir tane: ad: desen (ör. soru_acilis: ^Hai mai). Desen düzenli ifadedir.", gelismis: true },
    ] },
    { baslik: "7 · Onaylar", alanlar: [
      { aciklama: "İşaretli aşamalarda üretim durur ve onayını bekler; işaretsiz aşama kod kontrolleri temizse beklemeden geçer, sorun varsa yine durur. ONAY 1 (konu) ve ONAY 3 (Türkçe senaryo) her zaman istenir. Sahne paketi onaysızdır. Bunlar varsayılandır; her üretimin başında o üretim için değiştirilebilir." },
      ...[["arastirma", "ONAY 2 · Araştırma"], ["ceviri", "ONAY 4 · Hedef dil"], ["paketleme", "ONAY 5 · Paketleme"]]
        .map(([k, e]) => ({ yol: "onaylar." + k, etiket: e, tur: "onay" })),
    ] },
    { baslik: "8 · Modeller ve bütçe", alanlar: [
      { tur: "isler", gelismis: true },
      { yol: "butce.video_usd", etiket: "Video başına bütçe ($)", tur: "sayi" },
    ] },
  ];
}

// Kelime aralığı: süre × konuşma hızı (kanallar.kelime_araligi ile aynı hesap; burada yalnız göstermek için).
function kelimeAraligi(k, dil) {
  const olc = (((k.uzunluk || {}).hiz_olcum || {})[dil] || []).map((x) => x && x.hiz).filter(Number.isFinite).sort((a, b) => a - b);
  const n = olc.length;
  const ort = n ? (n % 2 ? olc[(n - 1) / 2] : (olc[n / 2 - 1] + olc[n / 2]) / 2) : (D.konusma_hizi[dil] || 150);
  const sp = Number((k.ses || {}).speed), hiz = ort * (sp >= 0.5 && sp <= 2 ? sp : 1);
  const orta = hiz * Number(k.uzunluk.hedef_dk), onluk = (x) => Math.floor(x / 10 + 0.5) * 10;
  return { aralik: [onluk(orta * (1 - D.kelime_payi)), onluk(orta * (1 + D.kelime_payi))], hiz: Math.round(hiz), olcum: n };
}

function kelimeBilgi(k) {
  const u = k.uzunluk || {}, hedef = (k.dil || {}).hedef || "tr", dilAdi = D.diller[hedef] || hedef;
  if (!u.kelime_otomatik) return `Elle ayarlı: Türkçe senaryo ${(u.calisma_kelime || []).join("–")} kelime` + (hedef === "tr" ? "" : ` · ${dilAdi} ${(u.hedef_kelime || []).join("–")} kelime`) + ". İstersen Gelişmiş'ten otomatik hesaba geçebilirsin.";
  const dk = Number(u.hedef_dk);
  if (!(dk >= 1 && dk <= 60)) return "Süreyi yazınca uygulama hesaplar.";
  const tr = kelimeAraligi(k, "tr"), hd = kelimeAraligi(k, hedef);
  const kaynak = (x) => x.olcum ? `${x.olcum} videonun gerçek ses süresinden` : "dilin ortalama hızından";
  return `Uygulama hesaplar: Türkçe senaryo ~${tr.aralik.join("–")} kelime (dakikada ~${tr.hiz}, ${kaynak(tr)})` +
    (hedef === "tr" ? "" : ` · ${dilAdi} senaryo ~${hd.aralik.join("–")} kelime (dakikada ~${hd.hiz}, ${kaynak(hd)})`) +
    ". Her videodan sonra gerçek ses süresiyle düzelir.";
}

function alanYollari(a) { return a.cift ? a.cift.map((x) => x.yol) : [a.yol]; }

function alanBul(yol) {
  for (const b of bolumler()) for (const a of b.alanlar) {
    if (a.yol === yol) return { ...a, gelismis: false };
    for (const x of a.cift || []) if (x.yol === yol) return { ...x };
  }
  return null;
}

// Bir bölümün alanları: gelişmiş olanlar katlanmış "Gelişmiş" kutusunda (DOM'da kalır, formOku okur).
function bolumHtml(b, k, mod, haric = new Set()) {
  const alanlar = b.alanlar.map((a) => (a.cift ? { ...a, cift: a.cift.filter((x) => !haric.has(x.yol)) } : a))
    .filter((a) => (a.cift ? a.cift.length : !(a.yol && haric.has(a.yol)) && !(a.tur === "kelime_bilgi" && haric.has("kelime_bilgi"))));
  const normal = alanlar.filter((a) => !a.gelismis), ileri = alanlar.filter((a) => a.gelismis);
  return normal.map((a) => alanHtml(a, k, mod)).join("") +
    (ileri.length ? `<details class="gelismis"><summary>Gelişmiş</summary>${ileri.map((a) => alanHtml(a, k, mod)).join("")}</details>` : "");
}

function alanHtml(a, k, mod) {
  if (a.tur === "kelime_bilgi") return `<div class="alan"><label>Kelime sayısı</label><p class="kucuk" id="kelime-bilgi">${kacir(kelimeBilgi(k))}</p></div>`;
  if (a.cift) return `<div class="alan-cift${a.elleKelime ? " elle-kelime" : ""}" ${a.elleKelime && (k.uzunluk || {}).kelime_otomatik ? "hidden" : ""}>${a.cift.map((x) => alanHtml(x, k, mod)).join("")}</div>${a.aciklama ? `<p class="alan-aciklama">${kacir(a.aciklama)}</p>` : ""}`;
  if (a.tur === "isler") return islerHtml(k);
  if (!a.yol) return `<p class="alan-aciklama">${kacir(a.aciklama)}</p>`;
  if (a.yalnizEkle && mod !== "ekle") return `<label>${kacir(a.etiket)}</label><p><b>${kacir(al(k, a.yol))}</b></p>`;
  const v = al(k, a.yol);
  const id = `a-${a.yol.replace(/\./g, "-")}`;
  let girdi;
  if (a.tur === "secim") girdi = `<select id="${id}" data-yol="${a.yol}" data-tur="secim">${a.secenekler.map(([d, e]) => `<option value="${kacir(d)}" ${String(d) === String(v) ? "selected" : ""}>${kacir(e)}</option>`).join("")}</select>`;
  else if (a.tur === "onay") girdi = `<input type="checkbox" id="${id}" data-yol="${a.yol}" data-tur="onay" ${v ? "checked" : ""}>`;
  else if (a.tur === "uzun") girdi = `<textarea id="${id}" data-yol="${a.yol}" data-tur="metin">${kacir(v)}</textarea>`;
  else if (a.tur === "liste") girdi = `<textarea id="${id}" data-yol="${a.yol}" data-tur="liste" style="min-height:60px">${kacir((v || []).join(", "))}</textarea>`;
  else if (a.tur === "kalip") girdi = `<textarea id="${id}" data-yol="${a.yol}" data-tur="kalip" style="min-height:70px" placeholder="ad: desen">${kacir(Object.entries(v || {}).map(([x, y]) => `${x}: ${y}`).join("\n"))}</textarea>`;
  else if (a.tur === "sinir") girdi = `<input type="text" id="${id}" data-yol="${a.yol}" data-tur="sinir" value="${kacir(Object.entries(v || {}).map(([x, y]) => `${x}:${y}`).join(", "))}">`;
  else if (a.tur === "renk") girdi = `<div class="satir"><input type="color" id="${id}" data-yol="${a.yol}" data-tur="metin" value="${kacir(v)}"><span class="kucuk soluk">${kacir(v)}</span></div>`;
  else girdi = `<input type="${a.tur === "sayi" ? "number" : "text"}" step="any" id="${id}" data-yol="${a.yol}" data-tur="${a.tur}" value="${kacir(v ?? "")}" placeholder="${kacir(a.ornek || "")}">`;
  const neden = F && F.eksikNeden && F.eksikNeden[a.yol];
  return `<div class="alan${neden ? " eksik-alan" : ""}">` + (neden ? `<p class="alan-aciklama hata-yazi">Dosyada: ${kacir(neden)}</p>` : "") + (a.tur === "onay"
    ? `<label class="satir" style="font-weight:500">${girdi} ${kacir(a.etiket)}</label>${a.aciklama ? `<p class="alan-aciklama">${kacir(a.aciklama)}</p>` : ""}`
    : `<label for="${id}">${kacir(a.etiket)}</label>${girdi}${a.aciklama ? `<p class="alan-aciklama">${kacir(a.aciklama)}</p>` : ""}`) + `</div>`;
}

function islerHtml(k) {
  const modeller = Object.entries(D.ayarlar.modeller).filter(([m]) => ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-4-5"].includes(m));
  const satirlar = Object.entries(k.isler).filter(([i]) => !i.endsWith("_yedek")).map(([i, v]) => `<tr><td>${kacir(IS_ADLARI[i] || i)}</td>
    <td><select data-yol="isler.${i}.model" data-tur="secim">${modeller.map(([m, ad]) => `<option value="${m}" ${m === v.model ? "selected" : ""}>${kacir(ad)}</option>`).join("")}</select></td>
    <td><select data-yol="isler.${i}.efor" data-tur="secim"><option value="medium" ${v.efor !== "low" && v.efor !== "high" ? "selected" : ""}>Medium</option><option value="low" ${v.efor === "low" ? "selected" : ""}>Low</option><option value="high" ${v.efor === "high" ? "selected" : ""}>High</option></select></td></tr>`).join("");
  return `<div class="tablo-kap"><table><thead><tr><th>İş</th><th>Model</th><th>Efor</th></tr></thead><tbody>${satirlar}</tbody></table></div>
    <p class="alan-aciklama">Haiku'da efor ayarı kullanılmaz. Model değiştirmek maliyeti etkiler.</p>`;
}

function formOku(kapsayici, k) {
  kapsayici.querySelectorAll("[data-yol]").forEach((el) => {
    const t = el.dataset.tur, yol = el.dataset.yol;
    let v;
    if (t === "onay") v = el.checked;
    else if (t === "sayi") v = el.value === "" ? null : Number(String(el.value).replace(",", "."));
    else if (t === "liste") v = el.value.split(/[,\n]/).map((x) => x.trim()).filter(Boolean);
    else if (t === "sinir") v = Object.fromEntries(el.value.split(",").map((x) => x.split(":").map((y) => y.trim())).filter((x) => x[0]).map(([a, b]) => [a, Number(b)]));
    else if (t === "kalip") v = Object.fromEntries(el.value.split("\n").map((x) => x.trim()).filter((x) => x.includes(":")).map((x) => { const i = x.indexOf(":"); return [x.slice(0, i).trim(), x.slice(i + 1).trim()]; }).filter(([a, b]) => a && b));
    else if (t === "secim" && yol === "kod_hane") v = Number(el.value);
    else v = el.value.trim();
    koy(k, yol, v);
  });
  for (const v of Object.values(k.isler || {})) if (v.model === "claude-haiku-4-5") v.efor = null;
  return k;
}

// Sihirbaz durumu
let F = null;  // {mod: "ekle"|"ayarlar", adim, kanal, kaynak, klasor, hatalar, uyarilar}

function kanalEkleAc() {
  const k = kopya(D.kanal_varsayilan);
  F = { mod: "ekle", yol: "secim", adim: 0, kanal: k, kaynak: "sablon", klasor: "", hatalar: [], uyarilar: [] };
  kanalFormuCiz(); $("#kanal-pencere").showModal();
}

// Dosyayla ekleme: ekranda gösterilen, uygulamada seçilen alanlar (gerisi "diğer ayarlar"da).
const DOSYA_SECILEN = ["ad", "dil.hedef", "uzunluk.hedef_dk", "kisaltma", "kod_oneki", "ses.voice_id", "ses.voice_name", "montaj.muzik", "montaj.maskot.dosyalar",
  "montaj.maskot.sira", "onaylar.arastirma", "onaylar.ceviri", "onaylar.paketleme"];

function dosyaEkranlari() {
  const notlar = (F.hatalar.length ? `<ul class="notlar hata">${F.hatalar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "") +
    (F.uyarilar.length ? `<ul class="notlar uyari">${F.uyarilar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "");
  if (F.yol === "secim") return `<h2 style="margin-top:0">Kanal ekle</h2>
    <div class="secim-kartlari">
      <button type="button" class="secim-karti" data-eylem="kf-yol" data-secim="dosya"><b>Dosyayla ekle <span class="oneri">önerilen</span></b>
        <span class="soluk kucuk">Şablonu bir yapay zekaya (Claude, ChatGPT…) doldurt, buraya yapıştır. Kanal bilgileri ve anayasa birlikte gelir; eksik kalanları uygulama gösterir.</span></button>
      <button type="button" class="secim-karti" data-eylem="kf-yol" data-secim="elle"><b>Elle doldur</b>
        <span class="soluk kucuk">Adım adım form. Anayasayı sonra Kanal dosyaları › 01_Anayasa.md'den doldurursun.</span></button>
    </div>
    <div class="satir" style="margin-top:18px;justify-content:flex-start"><button class="dugme" data-eylem="kf-kapat">Vazgeç</button></div>`;
  if (!F.okundu) return `<h2 style="margin-top:0">Kanal ekle · dosyayla</h2>
    <ol class="kucuk" style="padding-left:20px">
      <li><b>Şablonu kopyala</b> (aynı şablon kurulum klasöründe <code>Yeni_Kanal_Sablonu.md</code> olarak da duruyor).</li>
      <li>Bir yapay zekaya yapıştır, altına kanalını birkaç cümleyle anlat: konusu, kimin için, hangi dilde, kaç dakika, anlatıcı ve görsel tarz.</li>
      <li>Doldurduğu metni aşağıya yapıştır ya da dosyayı seç.</li></ol>
    <div class="satir"><button type="button" class="dugme" data-eylem="kf-sablon-kopyala">Şablonu kopyala</button>
      <label class="dugme">Dosya seç<input type="file" id="kf-dosya" accept=".md,.txt,text/plain,text/markdown" hidden></label></div>
    <textarea id="kf-metin" class="dosya-duzenle" style="min-height:260px" placeholder="Doldurulmuş kanal dosyasını buraya yapıştır">${kacir(F.metin || "")}</textarea>
    ${notlar}
    <div class="satir" style="margin-top:14px;justify-content:space-between"><button class="dugme" data-eylem="kf-yol" data-secim="secim">Geri</button>
      <button class="dugme ana-dugme" data-eylem="kf-dosya-oku">Oku ve devam et</button></div>`;
  const k = F.kanal, b = bolumler();
  const eksikYollar = F.eksik.map((e) => e.yol);
  const gosterilen = new Set([...eksikYollar, ...DOSYA_SECILEN, "kelime_bilgi"]);
  const alan = (yol) => { const a = alanBul(yol); return a ? alanHtml(a, k, "ekle") : ""; };
  const anayasa = F.anayasa ? (F.doldur ? `var, ${F.doldur} yer doldurulmamış (sonra tamamlanabilir)` : "var, tam") : "yok (genel şablondan başlar)";
  return `<h2 style="margin-top:0">Kanal ekle · dosyayla</h2>
    <p class="kucuk">Dosyadan <b>${F.okunan}</b> bilgi okundu · Anayasa: <b>${kacir(anayasa)}</b></p>
    ${F.eksik.length ? `<h3 class="bolum-baslik">Eksik ya da hatalı (${F.eksik.length})</h3>` + eksikYollar.map(alan).join("") : ""}
    <h3 class="bolum-baslik">Kanal</h3>
    ${["ad", "dil.hedef", "uzunluk.hedef_dk"].filter((y) => !eksikYollar.includes(y)).map(alan).join("")}
    <div class="alan"><label>Kelime sayısı</label><p class="kucuk" id="kelime-bilgi">${kacir(kelimeBilgi(k))}</p></div>
    ${["kisaltma", "kod_oneki"].filter((y) => !eksikYollar.includes(y)).map(alan).join("")}
    <h3 class="bolum-baslik">Uygulamada seçilenler</h3>
    <div class="alan-cift">${alan("ses.voice_id")}${alan("ses.voice_name")}</div>
    <p class="alan-aciklama">ElevenLabs'te sesin sayfasındaki kimlik. Şimdi boş bırakabilirsin; üretim başlamadan önce gerekli.</p>
    ${["montaj.muzik", "montaj.maskot.dosyalar", "montaj.maskot.sira"].map(alan).join("")}
    <p class="alan-aciklama" style="margin-top:10px">Onay: işaretli aşamalarda üretim durup onayını bekler (ONAY 1 ve 3 her zaman istenir).</p>
    ${["onaylar.arastirma", "onaylar.ceviri", "onaylar.paketleme"].map(alan).join("")}
    <details class="gelismis"><summary>Dosyadan gelen diğer ayarlar ve gelişmiş ayarlar</summary>
      ${b.map((x) => { const h = bolumHtml(x, k, "ekle", gosterilen); return h ? `<h4 class="bolum-baslik">${kacir(x.baslik)}</h4>${h}` : ""; }).join("")}
    </details>
    ${notlar}
    <div class="satir" style="margin-top:18px;justify-content:space-between">
      <button class="dugme" data-eylem="kf-dosya-geri">Geri</button>
      <button class="dugme ana-dugme" data-eylem="kf-kaydet">Kanalı oluştur</button></div>`;
}

async function kfDosyaOku() {
  F.metin = $("#kf-metin").value;
  try {
    const j = await api("/api/kanal/dosya-oku", { metin: F.metin });
    Object.assign(F, { okundu: true, kanal: j.kanal, anayasa: j.anayasa, eksik: j.eksik, okunan: j.okunan, doldur: j.doldur,
      hatalar: j.hatalar, uyarilar: j.uyarilar, okunanDil: j.kanal.dil.hedef,
      eksikNeden: Object.fromEntries(j.eksik.map((e) => [e.yol, e.neden])) });
  } catch (e) { F.hatalar = [e.message]; F.uyarilar = []; }
  kanalFormuCiz();
}

function kanalAyarAc() {
  F = { mod: "ayarlar", adim: 0, kanal: kopya(D.kanal.ayar), hatalar: [], uyarilar: [] };
  kanalFormuCiz(); $("#kanal-pencere").showModal();
}

function kanalFormuCiz() {
  const b = bolumler();
  const k = F.kanal;
  let govde, alt;
  const notlar = (F.hatalar.length ? `<ul class="notlar hata">${F.hatalar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "") +
    (F.uyarilar.length ? `<ul class="notlar uyari">${F.uyarilar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "");
  if (F.mod === "ekle" && F.yol !== "elle") {
    $("#kanal-formu").innerHTML = dosyaEkranlari();
    return;
  }
  if (F.mod === "ekle") {
    const toplam = b.length + 1;
    const cubuk = `<div class="adim-cubugu">${[...b.map((x) => x.baslik), "9 · Beceriler ve dosyalar"].map((x, i) => `<span class="${i === F.adim ? "simdi" : i < F.adim ? "gecti" : ""}">${kacir(x)}</span>`).join("")}</div>`;
    if (F.adim < b.length) govde = `<h3 class="bolum-baslik">${kacir(b[F.adim].baslik)}</h3>` + bolumHtml(b[F.adim], k, "ekle");
    else govde = `<h3 class="bolum-baslik">9 · Beceriler ve proje dosyaları</h3>
      <p class="soluk kucuk">Kanalın 6 aşama becerisi ve 4 proje dosyası (Yönetici, Anayasa, Defter, Aktif video) kanal klasörüne konur. Sonra "Kanal dosyaları"ndan düzenleyebilirsin.</p>
      <label class="satir" style="font-weight:500"><input type="radio" name="kaynak" value="sablon" ${F.kaynak === "sablon" ? "checked" : ""}> Genel şablondan başla <span class="soluk kucuk">(doldurulacak yerler ⟦DOLDUR⟧ ile işaretli)</span></label>
      <label class="satir" style="font-weight:500"><input type="radio" name="kaynak" value="klasor" ${F.kaynak === "klasor" ? "checked" : ""}> Bir klasörden içe aktar <span class="soluk kucuk">(kaynak klasör değiştirilmez, kopyalanır)</span></label>
      <input type="text" id="ice-klasor" placeholder="ör. ~/Desktop/BaskaKanal" value="${kacir(F.klasor)}" ${F.kaynak === "klasor" ? "" : "disabled"}>
      <p class="alan-aciklama">İçe aktarmada SKILL.md dosyaları adlarına göre (konu, arastirma, senaryo, ceviri/italyanca, sahne, paketleme), proje dosyaları 00_/01_/02_/03_ ile başlayan adlarına göre, Muzik ve Maskot klasörlerindeki medya da kopyalanır. Bulunamayanlar şablondan gelir.</p>`;
    alt = `<div class="satir" style="margin-top:18px;justify-content:space-between">
      <button class="dugme" data-eylem="kf-kapat">Vazgeç</button>
      <div class="satir">${F.adim > 0 ? `<button class="dugme" data-eylem="kf-geri">Geri</button>` : `<button class="dugme" data-eylem="kf-yol" data-secim="secim">Geri</button>`}
      ${F.adim < toplam - 1 ? `<button class="dugme ana-dugme" data-eylem="kf-ileri">İleri</button>` : `<button class="dugme ana-dugme" data-eylem="kf-kaydet">Kanalı oluştur</button>`}</div></div>`;
    govde = `<h2 style="margin-top:0">Kanal ekle</h2>${cubuk}${govde}`;
  } else {
    govde = `<h2 style="margin-top:0">Kanal ayarları · ${kacir(k.ad)}</h2>` + b.map((x) => `<h3 class="bolum-baslik">${kacir(x.baslik)}</h3>` + bolumHtml(x, k, "ayarlar")).join("");
    alt = `<div class="satir" style="margin-top:18px;justify-content:flex-end;position:sticky;bottom:-22px;background:var(--kart);padding:10px 0">
      <button class="dugme" data-eylem="kf-kapat">Vazgeç</button><button class="dugme ana-dugme" data-eylem="kf-kaydet">Kaydet</button></div>`;
  }
  $("#kanal-formu").innerHTML = govde + notlar + alt;
}

function formuAl() {
  formOku($("#kanal-formu"), F.kanal);
  if (F.kanal.kod_oneki) F.kanal.kod_oneki = F.kanal.kod_oneki.toUpperCase();
  if (F.kanal.kisaltma) F.kanal.kisaltma = F.kanal.kisaltma.toLowerCase();
  const r = document.querySelector("input[name=kaynak]:checked");
  if (r) F.kaynak = r.value;
  if ($("#ice-klasor")) F.klasor = $("#ice-klasor").value.trim();
}

async function kfIleri(yon) {
  if (F.mesgul) return;  // art arda tıklama adım atlatmasın
  F.mesgul = true;
  try { await kfAdim(yon); } finally { if (F) F.mesgul = false; }
}

async function kfAdim(yon) {
  formuAl();
  if (F.adim === 0 && F.mod === "ekle" && !F.kanal.kisaltma && F.kanal.ad) F.kanal.kisaltma = kisaltmaOner(F.kanal.ad);
  if (F.adim === 1 && F.mod === "ekle" && F.kanal.ses.language_code === D.kanal_varsayilan.ses.language_code) F.kanal.ses.language_code = F.kanal.dil.hedef;
  const j = await api("/api/kanal/dogrula", { kanal: F.kanal }).catch((e) => ({ hatalar: [e.message], uyarilar: [] }));
  // Yalnız bu adıma kadar olan alanlarla ilgili hataları göstermek zor; ileri giderken hata olsa da geçilir, sonda hepsi denetlenir.
  F.hatalar = yon > 0 && F.adim === 0 ? j.hatalar.filter((x) => /Kanal adı|Kısaltma|öneki|kısaltması/.test(x)) : [];
  F.uyarilar = [];
  if (!F.hatalar.length) F.adim = Math.max(0, F.adim + yon);
  kanalFormuCiz();
}

async function kfKaydet() {
  formuAl();
  try {
    if (F.mod === "ekle") {
      if (F.yol === "dosya" && F.kanal.ses.language_code === F.okunanDil) F.kanal.ses.language_code = F.kanal.dil.hedef;
      const j = await api("/api/kanal/ekle", { kanal: F.kanal, kaynak: F.yol === "dosya" ? "sablon" : F.kaynak, klasor: F.klasor,
        anayasa: F.yol === "dosya" ? F.anayasa : "" });
      $("#kanal-pencere").close();
      const aktarilan = j.ice_aktarma.filter((x) => !x.startsWith("Anayasa:")).length;
      bildir(`Kanal oluşturuldu: ${F.kanal.ad}` + (F.yol === "dosya" && F.anayasa ? " · anayasa dosyadan alındı" : "") + (aktarilan ? ` · ${aktarilan} dosya içe aktarıldı` : ""));
      await api("/api/kanal/sec", { kisaltma: j.kisaltma });
    } else {
      const j = await api("/api/kanal/guncelle", { kisaltma: D.aktif, kanal: F.kanal });
      $("#kanal-pencere").close();
      bildir("Kanal ayarları kaydedildi." + (j.uyarilar.length ? " " + j.uyarilar.join(" ") : ""));
    }
    F = null; await yenile(true);
  } catch (e) {
    F.hatalar = e.message.split("; "); kanalFormuCiz();
  }
}

// --- kanal dosyaları --------------------------------------------------------

async function dosyaAc(ad) {
  const j = await api(`/api/kanal/dosya?kanal=${encodeURIComponent(D.aktif)}&ad=${encodeURIComponent(ad)}`);
  $("#dosya-icerik").innerHTML = `<div class="satir" style="justify-content:space-between"><h2 style="margin:0">${kacir(ad)}</h2>
      <div class="satir"><button class="dugme ince" data-eylem="dosya-kopyala">Kopyala</button></div></div>
    <p class="soluk kucuk">⟦DOLDUR: …⟧ ile işaretli yerleri kanalına göre yaz ve işareti sil. Kaydedince önceki hâl kanal klasöründeki .yedek'e konur.</p>
    <textarea id="dosya-metin" class="dosya-duzenle" data-ad="${kacir(ad)}">${kacir(j.icerik)}</textarea>
    <div class="satir" style="margin-top:12px;justify-content:flex-end">
      <button class="dugme" data-eylem="dosya-kapat">Vazgeç</button><button class="dugme ana-dugme" data-eylem="dosya-kaydet">Kaydet</button></div>`;
  $("#dosya-pencere").showModal();
}

// --- kanal silme -------------------------------------------------------------

async function silAc() {
  const k = D.kanal.ayar;
  const j = await api(`/api/kanal/silinecekler?kanal=${encodeURIComponent(D.aktif)}`);
  $("#sil-icerik").innerHTML = `<h2 style="margin-top:0">Kanalı sil · ${kacir(k.ad)}</h2>
    <div class="tehlike-kutu"><p>Şunlar <b>Çöp Kutusu'na</b> taşınır (Çöp boşaltılana kadar geri alınabilir):</p>
      <ul class="notlar"><li>Kanal klasörü ve içindeki her şey: <code>${kacir(j.klasor)}</code> (videolar, arşiv, beceriler, müzik, maskot)</li>
      ${j.taslaklar.map((t) => `<li>Kanal Stüdyosu'nun bu kanal için oluşturduğu CapCut taslağı: <b>${kacir(t)}</b></li>`).join("")}</ul>
      <p class="kucuk soluk">Kanal Stüdyosu dışında oluşmuş CapCut taslaklarına dokunulmaz.${j.dokunulmayan.length ? " Dokunulmayan: " + kacir(j.dokunulmayan.join("; ")) : ""}</p></div>
    <label for="sil-ad">Onaylamak için kanal adını yaz: <b>${kacir(k.ad)}</b></label>
    <input type="text" id="sil-ad" autocomplete="off">
    <div class="satir" style="margin-top:14px;justify-content:flex-end">
      <button class="dugme" data-eylem="sil-kapat">Vazgeç</button><button class="dugme tehlike" data-eylem="sil-onayla">Kanalı sil</button></div>`;
  $("#sil-pencere").showModal();
}

// --- genel ayarlar --------------------------------------------------------

function anahtarAlani(tur, baslik, ornek) {
  const var_ = D.anahtarlar && D.anahtarlar[tur];
  return `<label>${baslik} ${var_ ? '<span class="soluk kucuk">· kayıtlı</span>' : '<span class="kucuk" style="color:var(--hata)">· kayıtlı değil</span>'}</label>
    <div class="satir"><input type="password" id="anahtar-${tur}" autocomplete="off" placeholder="${var_ ? "Kayıtlı (değiştirmek için yenisini yaz)" : ornek}" style="flex:1 1 220px">
      <button type="button" class="dugme" data-eylem="anahtar-test" data-tur="${tur}">Bağlantıyı test et</button>
      <button type="button" class="dugme" data-eylem="anahtar-kaydet" data-tur="${tur}">Kaydet</button>
      ${var_ ? `<button type="button" class="dugme tehlike" data-eylem="anahtar-sil" data-tur="${tur}">Sil</button>` : ""}</div>
    <p class="kucuk" id="anahtar-sonuc-${tur}" aria-live="polite"></p>`;
}

function ayarFormu() {
  const a = D.ayarlar;
  return `<h2 style="margin-top:0">Ayarlar <span class="soluk kucuk">(bütün kanallar için)</span></h2>
    <label>Yazım servisi</label>
    <select id="saglayici"><option value="claude_code" ${a.saglayici !== "openrouter" ? "selected" : ""}>Claude Code (abonelik)</option>
      <option value="openrouter" ${a.saglayici === "openrouter" ? "selected" : ""}>OpenRouter üzerinden Claude</option></select>
    <p class="soluk kucuk"><b>Claude Code:</b> bütün yazım işleri bu bilgisayardaki Claude Code ile, Pro/Max aboneliğinden yapılır; anahtar gerekmez. Claude Code kurulu ve PowerShell'de <code>claude</code> → /login ile aboneliğinle giriş yapılmış olmalı. Kullanım sınırı dolarsa adım durur, sınır açılınca Tekrar dene. <b>OpenRouter:</b> ücret OpenRouter kredisinden düşer, bütçe sınırları geçerlidir. Görseller (Flow) iki durumda da bugünkü gibi Claude uygulamasındaki beceriyle yapılır.</p>
    <div class="satir"><button type="button" class="dugme" data-eylem="anahtar-test" data-tur="claude_code">Claude Code'u kontrol et</button></div>
    <p class="kucuk" id="anahtar-sonuc-claude_code" aria-live="polite"></p>
    ${anahtarAlani("openrouter", "OpenRouter API anahtarı (yalnız OpenRouter seçiliyse)", "sk-or-…")}
    ${anahtarAlani("ai84", "AI84 API anahtarı (seslendirme)", "AI84 anahtarı")}
    <p class="soluk kucuk">Anahtarlar Windows Kimlik Bilgisi Yöneticisi'nde saklanır, dosyaya yazılmaz.</p>
    <label>Aylık bütçe ($, bütün kanallar · yalnız OpenRouter)</label><input type="number" min="1" step="1" id="aylik" value="${a.butce.aylik_usd}">
    <label>CapCut taslak klasörü</label><input type="text" id="yol-capcut" value="${kacir(a.yollar.capcut_taslak)}">
    <label>Önbellek süresi (yalnız OpenRouter)</label><select id="onbellek"><option value="5m" ${a.onbellek_suresi === "5m" ? "selected" : ""}>5 dakika</option><option value="1h" ${a.onbellek_suresi === "1h" ? "selected" : ""}>1 saat</option></select>
    <p class="soluk kucuk">Kurulum klasörü: ${kacir(D.kurulum)}</p>
    <div class="satir" style="margin-top:16px;justify-content:flex-end">
      <button type="button" class="dugme" data-eylem="ayar-kapat">Vazgeç</button>
      <button type="button" class="dugme ana-dugme" data-eylem="ayar-kaydet">Kaydet</button></div>`;
}

// --- üretim ekranı (ilk sürümdeki ekranın kanala bağlı hâli) --------

const para = (x) => (Number(x) || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " $";
let secilenDosya = {};     // aşama → seçili dosya sekmesi
let gorulenAsama = null;   // tamamlanmış bir aşamaya bakılıyorsa
const taslak = {};         // yazılan notlar (yeniden çizimde korunur)
let duzenlenen = null;     // elle düzenlenen dosya: {kimlik, ad}
const ASAMALAR = () => (D.kanal ? D.kanal.asamalar : []);

const DURUM_ADI = { bekliyor: "Bekliyor", calisiyor: "Çalışıyor", kontrol: "Kontrol ediliyor", onay_bekliyor: "Onay bekliyor", tamam: "Tamam", hata: "Durdu", butce_sorusu: "Bütçe sorusu", bekleme: "Bekliyor" };
const BAKIYE_UYARI_USD = 2;  // bir yazım aşaması bundan pahalı olabilir: yarıda kalmadan kredi yükle

function bakiyeCiz() {
  const b = D.bakiye || {}, parca = [];
  let az = false;
  if (b.saglayici === "openrouter") {
    const v = b.openrouter;
    az = typeof v === "number" && v < BAKIYE_UYARI_USD;
    parca.push(`<span${az ? ' class="az-deger"' : ""}>OpenRouter <b>${typeof v === "number" ? para(v) : "—"}</b></span>`);
  }
  if (b.ai84 !== null && b.ai84 !== undefined) parca.push(`AI84 <b>${Number(b.ai84).toLocaleString("tr-TR")}</b> kredi`);
  else if (b.zaman) parca.push("AI84 <b>—</b>");
  const el = $("#bakiye");
  el.hidden = !parca.length && !b.suruyor;
  el.innerHTML = b.suruyor && !parca.length ? "Bakiye okunuyor…" : "Kalan: " + parca.join(" · ");
  el.classList.toggle("az", az);
  el.title = (az ? "OpenRouter bakiyesi az: yazım aşaması yarıda kalabilir, kredi yükle. " : "") +
    "Kalan bakiye" + (b.zaman ? " · " + new Date(b.zaman * 1000).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }) : "") + " · tıkla: yenile";
}

function maliyetCiz() {
  bakiyeCiz();
  const m = D.maliyet;
  if (m && D.ayarlar.saglayici !== "openrouter") {
    $("#maliyet").innerHTML = "Yazım: <b>Claude Code aboneliği</b>" + (D.uretim && m.abonelik_tahmini_usd ? ` · API karşılığı ~${para(m.abonelik_tahmini_usd)}` : "");
    $("#maliyet").title = "Ücret abonelikten; API karşılığı yalnız bilgi içindir.";
    return;
  }
  $("#maliyet").innerHTML = m ? (D.uretim ? `Bu video <b>${para(m.video_usd)}</b> / ${para(m.video_sinir)} · ` : "") +
    `Bu ay <b>${para(m.ay_usd)}</b> / ${para(m.ay_sinir)}` : "";
}

function adimCubugu(d) {
  const ogeler = ASAMALAR().map((a) => {
    const s = d.asamalar[a.kimlik]?.durum || "bekliyor";
    if (s === "atlandi") return `<span class="adim atlandi" title="Hazır metinle başlandığı için atlandı">${kacir(a.ad)} · atlandı</span>`;
    const sinif = d.adim === a.kimlik ? "simdi" : s === "tamam" ? "tamam" : "";
    const gor = s === "tamam" && a.yazi ? `data-eylem="gor" data-kimlik="${a.kimlik}"` : "";
    return `<span class="adim ${sinif}" ${gor}>${kacir(a.ad)}${s === "tamam" ? " ✓" : ""}</span>`;
  }).join("");
  return `<div class="adimlar">${ogeler}</div>`;
}

function dosyaSekmeleri(a, kimlik, duzenlenebilir = false) {
  const ciktilar = ASAMALAR().find((x) => x.kimlik === kimlik).ciktilar;
  const secili = secilenDosya[kimlik] || ciktilar[0];
  const sekmeler = `<div class="sekmeler">${ciktilar.map((ad) => `<span class="sekme ${ad === secili ? "secili" : ""}" data-eylem="sekme" data-kimlik="${kimlik}" data-ad="${kacir(ad)}">${kacir(ad.replace(D.uretim.kod + "_", ""))}${a.elle_yedek?.[ad] ? " ✎" : ""}</span>`).join("")}</div>`;
  if (!duzenlenebilir) return sekmeler + `<pre class="dosya" id="uretim-dosya" data-ad="${kacir(secili)}">Yükleniyor…</pre>`;
  const geri = a.elle_yedek?.[secili] ? `<button class="dugme ince" data-eylem="elle-geri" data-kimlik="${kimlik}" data-ad="${kacir(secili)}">Modelin yazdığı hâle dön</button>` : "";
  if (duzenlenen && duzenlenen.kimlik === kimlik && duzenlenen.ad === secili) {
    const anahtar = `elle_${kimlik}_${secili}`;
    return sekmeler + `<textarea class="dosya duzenle" id="uretim-duzenle" data-taslak="${kacir(anahtar)}" data-ad="${kacir(secili)}" spellcheck="false">${kacir(taslak[anahtar] ?? "Yükleniyor…")}</textarea>
      <div class="satir" style="margin-top:8px"><button class="dugme ana-dugme" data-eylem="elle-kaydet" data-kimlik="${kimlik}" data-ad="${kacir(secili)}">Kaydet ve kontrol et</button>
      <button class="dugme" data-eylem="elle-vazgec">Vazgeç</button>${geri}</div>
      <p class="soluk kucuk">Kaydet ücretsizdir: model çağrılmaz, yalnız kod kontrolleri yeniden çalışır. Paragraflar arasındaki boş satırları koru; sahneler onlardan oluşur. Modelin yazdığı hâl yedeklenir.</p>`;
  }
  return sekmeler + `<pre class="dosya" id="uretim-dosya" data-ad="${kacir(secili)}">Yükleniyor…</pre>
    <div class="satir" style="margin-top:8px"><button class="dugme" data-eylem="elle-ac" data-kimlik="${kimlik}" data-ad="${kacir(secili)}">Metni burada düzenle</button>${geri}</div>`;
}

function kontrolNotlari(k) {
  if (!k) return "";
  return `${k.bilgiler?.length ? `<div class="etiketler">${k.bilgiler.map((b) => `<span class="etiket">${kacir(b)}</span>`).join("")}</div>` : ""}
    ${k.hatalar?.length ? `<h3>Otomatik düzeltmeyle çözülemeyenler</h3><ul class="notlar hata">${k.hatalar.map((h) => `<li>${kacir(h)}</li>`).join("")}</ul>` : ""}
    ${k.uyarilar?.length ? `<h3>Dikkat</h3><ul class="notlar uyari">${k.uyarilar.map((h) => `<li>${kacir(h)}</li>`).join("")}</ul>` : ""}`;
}

function calisiyorPaneli(baslik, s, u, yazi) {
  const ek = s.oto_tur ? ` · otomatik düzeltme ${s.oto_tur}` : s.kullanici_tur ? " · düzeltmen işleniyor" : "";
  const ilerleme = yazi ? (u.ilerleme ? u.ilerleme.toLocaleString("tr-TR") + " karakter" : "Başlıyor") : (u.ilerleme_metni || "Başlıyor…");
  return `<section class="kart"><h2>${baslik}</h2><div class="yukleniyor"><div class="donen"></div>
    <div><b>${s.durum === "kontrol" ? "Kontrol ediliyor…" : yazi ? "Yazılıyor…" : "Çalışıyor…"}</b>${kacir(ek)}<br>
    <span class="soluk kucuk" id="ilerleme" data-yazi="${yazi ? 1 : 0}">${kacir(ilerleme)}</span></div></div>
    <p class="soluk kucuk">Bu adım ${yazi ? "birkaç dakika" : "uzun (ses ve video için 15–20 dk)"} sürebilir. Uygulamayı kapatırsan kaldığı yerden devam eder.</p>
    <button class="dugme tehlike" data-eylem="durdur">Durdur</button>
    <span class="soluk kucuk">${yazi ? "Yazım hemen kesilir; o ana kadarki kısmın ücreti gider, Tekrar dene ile adım baştan yazılır."
      : "Güvenli durdurma: ses/video o anki sahne, montaj o anki işlem bitince durur. Tekrar dene kaldığı yerden sürer."}</span></section>`;
}

function flowPaneli(u, s) {
  const f = u.flow || {};
  if (s.sorun) {
    return `<section class="kart"><h2>Görseller (Flow) · ajan bir sorun bildirdi</h2>
      <pre class="ozet">${kacir(s.sorun)}</pre>
      <p>Prompt değişmesi gerekiyorsa Aşama 5'e düzeltme gönder; uygulama promptu kendisi değiştirmez. Değişen sahneler için Flow isteği yeniden hazırlanır.</p>
      <textarea data-taslak="flow_duz" placeholder="Örn. 0034 politikaya takıldı: mutfakta yalnız fincan ve pencere olsun.">${kacir(taslak.flow_duz || "")}</textarea>
      <div class="satir" style="margin-top:10px"><button class="dugme ana-dugme" data-eylem="flow-a5">Aşama 5'e düzeltme gönder</button>
      <button class="dugme" data-eylem="flow-sorun-devam">Sorun çözüldü, beklemeye devam</button></div></section>`;
  }
  return `<section class="kart"><h2>Görseller (Flow)</h2>
    ${s.uyari ? `<p class="notlar uyari">${kacir(s.uyari)}</p>` : ""}
    ${s.eksik?.length ? `<p><b>Eksik/hatalı sahneler:</b> ${s.eksik.map((n) => "sahne" + String(n).padStart(4, "0")).join(", ")}</p>` : ""}
    ${s.boyut?.length ? `<ul class="notlar uyari">${s.boyut.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : ""}
    <ol>
      <li>Claude masaüstü uygulamasında <b>yeni bir sohbet</b> aç (Sonnet). <b>kanal-studyosu-flow</b> becerisi yüklü olmalı.</li>
      <li>Şunu yapıştır: <div class="satir" style="margin:6px 0"><code class="ozet" style="flex:1 1 300px;margin:0">${kacir(s.komut || "")}</code>
        <button class="dugme ince" data-eylem="kopyala" data-metin="${kacir(s.komut || "")}">Kopyala</button></div></li>
      <li>Ajan görselleri <b>flow_cikti</b> klasörüne koyup <code>BITTI.json</code> yazınca uygulama kendiliğinden kontrol eder ve devam eder (ses, video, CapCut taslağı ve rapor dahil).</li>
    </ol>
    <div class="yukleniyor"><div class="donen"></div><span>Bekleniyor · klasörde <b>${f.gorsel || 0}</b> görsel${f.zip ? `, ${f.zip} zip` : ""}</span></div>
    <p class="soluk kucuk">İstek klasörü: ${kacir(s.klasor || "")}<br>Görseller buraya: ${kacir(s.cikti || "")}</p>
    <div class="satir" style="margin-top:10px"><button class="dugme" data-eylem="flow-kontrol">Görselleri şimdi kontrol et</button>
      <button class="dugme" data-eylem="partiler">Yarı elle yol (partileri göster)</button></div>
    <div id="partiler"></div>
    <p class="soluk kucuk">Hatırlatma: Flow'un kullanım şartlarını sen izliyorsun. Hesap uyarısı gelirse yarı elle yola dön: partileri kopyala, Flow'a yapıştır, indirilen zip'i yukarıdaki klasöre bırak, sonra "Görselleri şimdi kontrol et".</p></section>`;
}

function bittiPaneli(u, d) {
  const r = d.sonuclar || {};
  const adaylar = d.silme_adaylari || [];
  const kok = D.kanal.klasor + "/";
  return `<section class="kart"><h2>Her şey bitti 🎬</h2>
    <div class="ozet">${kacir(r.rapor_ozet || "")}</div>
    <ul>
      <li><b>CapCut'ta açılacak taslak:</b> ${kacir(u.kod)} (listede yoksa CapCut'ı kapatıp aç)</li>
      <li><b>Süre / sahne:</b> ${kacir(r.sure || "?")} / ${kacir(r.sahne || "?")}</li>
      <li><b>Müzik:</b> ${kacir(r.muzik || "-")}${D.kanal.ayar.montaj.muzik ? ` <button class="dugme mini" data-eylem="muzik-yenile" title="Yeni rastgele parçalarla müziği yeniden yapar; eski hâli arşive kopyalanır">Müziği yeniden yap</button>` : ""}</li>
      <li><b>Kanal Defteri:</b> ${kacir(r.defter || "-")}</li>
      <li><b>Maliyet:</b> ${para(D.maliyet.video_usd)}</li>
    </ul>
    <p><b>Senin işin:</b> CapCut'ta kontrol, rötuş ve dışa aktarma; kapak görsellerini Flow'da üretmek.</p>
    <button class="dugme" data-eylem="rapor">Raporun tamamını göster</button><pre class="dosya" id="rapor" hidden></pre>
    ${adaylar.length ? `<h3>Silme adayları (${adaylar.length})</h3><ul class="notlar">${adaylar.map((x) => `<li>${kacir(x.startsWith(kok) ? x.slice(kok.length) : x)}</li>`).join("")}</ul>
      <p class="soluk kucuk">Uygulama hiçbir şey silmez. "Taşı" dersen kanal klasöründe Silinecekler/${kacir(u.kod)}/ içine taşınır, sen silersin. Cevap vermezsen üretimi kapatırken taşınır.</p>
      <div class="satir"><button class="dugme" data-eylem="silme" data-tasi="1">Silinecekler'e taşı</button><button class="dugme" data-eylem="silme" data-tasi="0">Kalsın</button></div>` :
      d.silme_karari ? `<p class="soluk">Silme adayları: ${kacir(d.silme_karari)}.</p>` : ""}
    <div class="satir" style="margin-top:16px"><button class="dugme ana-dugme" data-eylem="uretim-kapat">Üretimi kapat, ana ekrana dön</button></div></section>`;
}

function uretimEkrani() {
  const u = D.uretim, d = u.durum;
  const kimlik = gorulenAsama || d.adim;
  const tanim = ASAMALAR().find((a) => a.kimlik === kimlik);
  let govde = "";
  if (!tanim) {
    govde = bittiPaneli(u, d);
  } else {
    const s = d.asamalar[kimlik];
    const baslik = kacir(tanim.ad);
    if (gorulenAsama) {
      govde = `<section class="kart"><div class="satir" style="justify-content:space-between"><h2>${baslik} (onaylandı)</h2>
        <button class="dugme ince" data-eylem="geri">Güncel adıma dön</button></div>
        ${s.onay_notu ? `<p><b>Onay notun:</b> ${kacir(s.onay_notu)}</p>` : ""}${dosyaSekmeleri(s, kimlik)}</section>`;
    } else if (s.durum === "calisiyor" || s.durum === "kontrol" || (u.calisiyor && s.durum !== "onay_bekliyor")) {
      govde = calisiyorPaneli(baslik, s, u, tanim.yazi);
    } else if (kimlik === "FLOW" && s.durum === "bekleme") {
      govde = flowPaneli(u, s);
    } else if (s.durum === "bekleme") {
      govde = `<section class="kart"><h2>${baslik}</h2><p>${kacir(s.uyari || "Devam için seni bekliyor.")}</p>
        <button class="dugme ana-dugme" data-eylem="devam">Devam</button></section>`;
    } else if (s.durum === "onay_bekliyor" && !tanim.yazi) {
      govde = `<section class="kart"><h2>${baslik} · kontrol notları</h2>
        <p>${kimlik === "STUDIO" ? "Ses kenarı kontrolü aşağıdaki sahnelerin sonunda kesik buldu. Bu sahnelerin sonunu dinle; sorun değilse <b>Yine de devam et</b>." : "Senkron kontrolü aşağıdaki notları verdi. Notları CapCut'ta düzelttiysen <b>Tekrar kontrol et</b>; sorun değilse <b>Yine de devam et</b>."}</p>
        ${kontrolNotlari(s.kontrol)}<h3>Kontrol çıktısı</h3><pre class="ozet">${kacir(s.ozet || "")}</pre>
        <div class="satir"><button class="dugme ana-dugme" data-eylem="onay" data-kimlik="${kimlik}">Yine de devam et</button>
        <button class="dugme" data-eylem="devam">Tekrar kontrol et</button></div></section>`;
    } else if (s.durum === "onay_bekliyor") {
      const temiz = !(s.kontrol?.hatalar?.length);
      const onayAdi = tanim.onay ? `ONAY ${tanim.onay}` : "Kontrol";
      govde = `<section class="kart"><h2>${baslik} · ${onayAdi}</h2>
        <p class="soluk">${temiz ? "Kod kontrollerinden geçti." : "Kod kontrolü sorun buldu; aşağıda listelendi."}
        ${s.model ? ` · ${kacir(D.ayarlar.modeller[s.model] || s.model)}` : ""}${s.usd ? ` · ${para(s.usd)}` : ""}</p>
        ${s.yedek_model_notu ? `<p class="notlar uyari">${kacir(s.yedek_model_notu)}</p>` : ""}
        ${kontrolNotlari(s.kontrol)}
        ${s.degisiklikler?.length && s.kullanici_tur ? `<h3>Son düzeltmede değişenler</h3><ul class="notlar">${s.degisiklikler.slice(-30).map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : ""}
        ${s.acik_noktalar ? `<h3>Açık noktalar</h3><p class="acik-noktalar ${/^yok\.?$/i.test(s.acik_noktalar.trim()) ? "soluk" : "notlar uyari"}">${kacir(s.acik_noktalar)}</p>` : ""}
        <h3>Özet</h3><div class="ozet">${kacir(s.ozet || "")}</div>
        ${dosyaSekmeleri(s, kimlik, true)}
        <div class="onay-alani">
          <div class="kutu"><h3>${tanim.onay ? "Onayla" : "Devam et"}</h3>
            <textarea data-taslak="onay_${kimlik}" placeholder="İsteğe bağlı not (sonraki aşamaya iletilir)">${kacir(taslak["onay_" + kimlik] || "")}</textarea>
            <button class="dugme ana-dugme" style="margin-top:10px" data-eylem="onay" data-kimlik="${kimlik}">${tanim.onay ? `ONAY ${tanim.onay} ver` : "Yine de devam et"}</button></div>
          <div class="kutu"><h3>Düzeltme iste</h3>
            <textarea data-taslak="duz_${kimlik}" placeholder="Ne değişsin? Örn. ¶12 daha kısa olsun; başlıkta şu kelime geçmesin.">${kacir(taslak["duz_" + kimlik] || "")}</textarea>
            <button class="dugme" style="margin-top:10px" data-eylem="duzeltme" data-kimlik="${kimlik}">Düzeltme gönder</button></div>
        </div></section>`;
    } else if (s.durum === "butce_sorusu") {
      govde = `<section class="kart"><h2>${baslik} · bütçe</h2><p>${kacir(s.hata)}</p>
        <div class="satir"><button class="dugme ana-dugme" data-eylem="tekrar" data-butce="1">Bu adım için devam et</button>
        <button class="dugme" data-eylem="kanal-ayar">Video bütçesini değiştir (Kanal ayarları)</button></div></section>`;
    } else if (s.durum === "hata") {
      govde = `<section class="kart"><h2>${baslik} · durdu</h2><p>${kacir(s.hata)}</p>
        ${s.hata_ayrinti ? `<details class="hata-ayrinti"><summary>Ayrıntı (betiğin çıktısı)</summary><pre class="ozet">${kacir(s.hata_ayrinti)}</pre></details>` : ""}
        <div class="satir"><button class="dugme ana-dugme" data-eylem="tekrar">Tekrar dene</button>
        <button class="dugme" data-eylem="hata-kopyala" data-kimlik="${kimlik}">Hatayı kopyala</button></div></section>`;
    } else {
      govde = `<section class="kart"><h2>${baslik}</h2><p class="soluk">${DURUM_ADI[s.durum] || ""}</p>
        <button class="dugme ana-dugme" data-eylem="tekrar">Başlat</button></section>`;
    }
  }
  const iptalEdilebilir = d.adim !== "BITTI" && !d.defter_tamam;
  return `<div class="satir" style="justify-content:space-between;margin-bottom:14px"><h1 style="margin:0;font-size:24px">${kacir(u.kod)} <span class="soluk kucuk" style="font-weight:400">· ${kacir(D.kanal.ayar.ad)}</span></h1>
    ${iptalEdilebilir ? `<button class="dugme ince tehlike" data-eylem="iptal">Üretimi iptal et</button>` : ""}</div>${adimCubugu(d)}${govde}`;
}

// Metin kutularına (dosya, özet, rapor, betik çıktısı) Kopyala ve Büyüt düğmeleri.
function metinKutulari() {
  document.querySelectorAll("#ana pre.dosya, #ana pre.ozet, #ana div.ozet").forEach((el) => {
    if (el.parentElement.classList.contains("kutu-kap")) return;
    const kap = document.createElement("div");
    kap.className = "kutu-kap";
    el.replaceWith(kap);
    kap.innerHTML = `<div class="kutu-arac"><button class="dugme mini" data-eylem="kutu-kopyala">Kopyala</button><button class="dugme mini" data-eylem="kutu-buyut">Büyüt</button></div>`;
    kap.appendChild(el);
  });
}

async function uretimDosyasiYukle() {
  const t = $("#uretim-duzenle");
  if (t && taslak[t.dataset.taslak] === undefined) {
    try { const ic = (await api("/api/dosya?ad=" + encodeURIComponent(t.dataset.ad))).icerik; taslak[t.dataset.taslak] = ic; t.value = ic; }
    catch (e) { t.value = e.message; }
  }
  const p = $("#uretim-dosya");
  if (!p) return;
  try { p.textContent = (await api("/api/dosya?ad=" + encodeURIComponent(p.dataset.ad))).icerik; }
  catch (e) { p.textContent = e.message; }
}

async function partilerGoster() {
  const k = $("#partiler");
  if (k.innerHTML) { k.innerHTML = ""; return; }
  const j = await api("/api/flow/istek").catch((e) => ({ hata: e.message }));
  if (!j.partiler) { k.innerHTML = `<p class="soluk">${kacir(j.hata || "İstek bulunamadı")}</p>`; return; }
  const ay = j.ayarlar || {};
  window.__partiler = { liste: j.partiler, oran: ay.oran || "16:9", model: ay.model || "Nano Banana 2" };
  k.innerHTML = `<h3>Yarı elle yol · ${j.partiler.length} parti</h3>
    <p class="soluk kucuk">Flow'da proje adı: <b>${kacir(j.proje_adi)}</b> · Ayarlar: ${kacir(window.__partiler.oran)}, x1, ${kacir(window.__partiler.model)}, "Hiçbir zaman". Her partiyi Flow'a yapıştır, bitmesini bekle, sonrakine geç.</p>` +
    j.partiler.map((p, i) => `<div class="kutu" style="margin:8px 0"><div class="satir" style="justify-content:space-between">
      <b>Parti ${i + 1} · ${kacir(p.sahneler[0])}–${kacir(p.sahneler[p.sahneler.length - 1])}</b>
      <button class="dugme ince" data-eylem="parti-kopyala" data-i="${i}">Kopyala</button></div></div>`).join("");
}

function partiKopyala(i) {
  const P = window.__partiler, p = P.liste[i];
  kopyala(`Sıradaki promptları sırayla üret (her biri ${P.oran}, x1, ${P.model}) ve üretilen görselleri sırayla ${p.sahneler.join(", ")} olarak adlandır. Hata olursa bir promptu en fazla 3 kez dene. Onay bekleme.\n\n` + p.promptlar.join("\n\n"));
}

// --- ana ekran ------------------------------------------------------------

function ustCiz() {
  const sec = $("#kanal-sec");
  const kilit = D.uretim ? ` disabled title="Üretim sürerken kanal değiştirilemez"` : ` title="Kanal seç"`;
  sec.innerHTML = D.kanallar.length ? `<select id="kanal-secici"${kilit}>${D.kanallar.map((k) => `<option value="${kacir(k.kisaltma)}" ${k.kisaltma === D.aktif ? "selected" : ""}>${kacir(k.ad)}${k.test ? " (test)" : ""}</option>`).join("")}</select>` : "";
}

function anaEkran() {
  const ok = D.onkontrol;
  const maddeler = ok ? ok.maddeler.map((x) => `<li><span class="isaret ${x.tamam ? "tamam" : x.zorunlu ? "yok" : "bilgi"}">${x.tamam ? "✓" : x.zorunlu ? "✗" : "!"}</span>
      <span><b>${kacir(x.ad)}</b> · <span class="soluk">${kacir(x.mesaj)}</span></span></li>`).join("") : "";
  const kontrol = `<section class="kart"><div class="satir" style="justify-content:space-between"><h2>Başlangıç kontrolü</h2>
      <button class="dugme ince" data-eylem="onkontrol" ${D.onkontrol_suruyor ? "disabled" : ""}>Yeniden kontrol et</button></div>
    ${D.onkontrol_suruyor && !ok ? `<div class="yukleniyor"><div class="donen"></div><span>Kontrol ediliyor…</span></div>` : `<ul class="kontrol-listesi">${maddeler}</ul>`}</section>`;
  if (!D.kanal) {
    return kontrol + `<section class="kart"><h2>Henüz kanal yok</h2>
      <p>Kanal Stüdyosu her kanalı kendi klasöründe, kendi ayarlarıyla çalıştırır. Başlamak için bir kanal ekle.</p>
      <button class="dugme ana-dugme" data-eylem="kanal-ekle">+ Kanal ekle</button>
      <p class="soluk kucuk" style="margin-top:12px">Kurulum klasörü: ${kacir(D.kurulum)}</p></section>`;
  }
  const k = D.kanal.ayar;
  const dil = D.diller[k.dil.hedef] || k.dil.hedef;
  const eksik = D.kanal.eksikler.length ? `<ul class="notlar">${D.kanal.eksikler.map((e) => `<li style="color:var(${e.zorunlu ? "--hata" : "--uyari"})">${kacir(e.mesaj)}</li>`).join("")}</ul>` : `<p style="color:var(--tamam)">✓ Kanal üretime hazır.</p>`;
  const dosyalar = D.kanal.dosyalar.map((d) => `<li data-eylem="dosya-ac" data-ad="${kacir(d.ad)}"><b>${kacir(d.ad.replace("Beceriler/", "Beceri · ").replace("/SKILL.md", ""))}</b>
      ${d.doldur ? `<span class="rozet uyari">${d.doldur} yer doldurulacak</span>` : `<span class="rozet tamam">hazır</span>`}</li>`).join("");
  return kontrol + `
  <section class="kart kanal-karti">
    <div class="satir" style="justify-content:space-between"><h2>${kacir(k.ad)}${k.test ? ' <span class="rozet">test kanalı</span>' : ""}</h2>
      <div class="satir"><button class="dugme ince" data-eylem="kanal-ayar">Kanal ayarları</button>
      <button class="dugme ince" data-eylem="klasor-ac">Klasörü aç</button>
      <button class="dugme ince tehlike" data-eylem="kanal-sil">Kanalı sil</button></div></div>
    <div class="bilgi">
      <span class="soluk">Video kodu</span><span>${kacir(k.kod_oneki)}-01, ${kacir(k.kod_oneki)}-02…</span>
      <span class="soluk">Dil akışı</span><span>Türkçe senaryo → ${kacir(dil)}${k.dil.hedef === "tr" ? " (4. aşama atlanır)" : ""} → ${kacir(dil)} seslendirme</span>
      <span class="soluk">Süre</span><span>~${kacir(k.uzunluk.hedef_dk)} dk · ${kacir(k.uzunluk.hedef_kelime.join("–"))} kelime</span>
      <span class="soluk">Ses</span><span>${kacir(k.ses.voice_name || k.ses.voice_id || "seçilmedi")} · ${kacir(k.ses.model_id)}</span>
      <span class="soluk">Karakter</span><span>${kacir(k.gorsel.karakter || "yok")}</span>
      <span class="soluk">Maskot / müzik</span><span>${k.montaj.maskot.dosyalar.length ? k.montaj.maskot.dosyalar.length + " maskot" : "maskot yok"} · müzik ${k.montaj.muzik ? "açık" : "kapalı"}</span>
      <span class="soluk">Klasör</span><span class="kucuk">${kacir(D.kanal.klasor)}</span>
    </div>
    <h3>Üretime hazırlık</h3>${eksik}
  </section>
  <section class="kart"><h2>Kanal dosyaları</h2>
    <p class="soluk kucuk">Becerileri ve proje dosyalarını burada düzenleyebilirsin. Sayısal sınırlar, etiketler ve ses gibi değerler Kanal ayarları'ndadır; uygulama onları her aşamada modele kendisi verir.</p>
    <ul class="dosya-listesi">${dosyalar}</ul></section>
  ${baslatKarti()}
  ${videolarKarti()}`;
}

// "Sıradaki üretim" kartı: konudan başla ya da hazır metinle başla; bu üretimde istenecek onaylar.
function baslatKarti() {
  const ok = D.onkontrol, hazir = ok && ok.hazir;
  const kanalHazir = !D.kanal.eksikler.some((e) => e.zorunlu);
  const sebep = !hazir ? "Başlangıç kontrolündeki eksikler tamamlanınca açılır." : !kanalHazir ? "Kanalın üretime hazırlığındaki eksikler tamamlanınca açılır." : !D.kanal.siradaki ? "Sıradaki kod bulunamadı." : "";
  const K_ = D.kanal, mod = taslak.mod === "hazir" ? "hazir" : "konu";
  const diller = Object.entries(K_.hazir_diller);
  const dil = taslak.hazir_dil && K_.hazir_diller[taslak.hazir_dil] ? taslak.hazir_dil : diller[diller.length - 1][0];
  const onaylar = K_.onay_secilebilir.map((o) => {
    const acik = taslak["uonay_" + o.kimlik] ?? K_.onaylar[o.kimlik];
    const atlanir = mod === "hazir" && (o.kimlik === "A2" || (o.kimlik === "A4" && dil !== "tr"));
    return `<label class="satir" style="margin:0;font-weight:500;${atlanir ? "opacity:.45" : ""}"><input type="checkbox" data-taslak="uonay_${o.kimlik}" ${acik ? "checked" : ""} ${atlanir ? "disabled" : ""}> ONAY ${o.onay} · ${kacir(o.ad.replace(/^\d · /, ""))}${atlanir ? " (bu yolda yok)" : ""}</label>`;
  }).join("");
  const atlanan = K_.ayar.dil.hedef === "tr" ? "2–3. aşamalar atlanır" : `Türkçe metinde 2–3. aşamalar, ${kacir(K_.dil_adi)} metinde 2–4. aşamalar atlanır`;
  const govde = mod === "konu" ? `
    <label for="konu-istegi">Konu isteğin (isteğe bağlı)</label>
    <input type="text" id="konu-istegi" data-taslak="konu_istegi" value="${kacir(taslak.konu_istegi || "")}" placeholder="Boş bırakırsan konuyu 1. aşama seçer">` : `
    <p class="soluk kucuk">Metnin hazırsa yapıştır. Tek bir yazım adımında konu kartı çıkarılır, Kanal Defteri'ne göre çakışma kontrol edilir, metin sahne paragraflarına bölünüp etiketlenir. <b>Metnin kelimelerine dokunulmaz</b>; uygulama bunu denetler. ${atlanan}.</p>
    <label>Metnin dili</label>
    <div class="satir">${diller.map(([k, ad]) => `<label class="satir" style="margin:0;font-weight:500"><input type="radio" name="hazir-dil" value="${k}" data-taslak="hazir_dil" ${k === dil ? "checked" : ""}> ${kacir(ad)}</label>`).join("")}</div>
    <label for="hazir-metin">Metin</label>
    <textarea id="hazir-metin" data-taslak="hazir_metin" style="min-height:220px" placeholder="Metni buraya yapıştır">${kacir(taslak.hazir_metin || "")}</textarea>`;
  return `<section class="kart">
    <h2>Sıradaki üretim: ${kacir(K_.siradaki || "—")}</h2>
    <div class="sekmeler"><span class="sekme ${mod === "konu" ? "secili" : ""}" data-eylem="baslat-mod" data-mod="konu">Konudan başla</span>
      <span class="sekme ${mod === "hazir" ? "secili" : ""}" data-eylem="baslat-mod" data-mod="hazir">Hazır metinle başla</span></div>
    ${govde}
    ${onaylar ? `<h3>Bu üretimde onay iste</h3><div class="satir" style="gap:16px;flex-wrap:wrap">${onaylar}</div>` : ""}
    <p class="soluk kucuk">Varsayılanlar Kanal ayarları › Onaylar'dan gelir. ONAY 1 ve ONAY 3 her zaman istenir (hazır metinde ilk onay ekranı). Onayı kapalı aşama, kod kontrolleri temizse beklemeden geçer; sorun varsa yine durur.</p>
    <div class="satir" style="margin-top:16px">
      <button class="dugme ana-dugme" data-eylem="baslat" ${sebep ? "disabled" : ""}>${mod === "hazir" ? "Hazır metinle başla" : "Üretime başla"}</button>
      ${sebep ? `<span class="soluk kucuk">${sebep}</span>` : ""}
    </div>
    <p class="soluk kucuk">Aşamalar: ${ASAMALAR().map((a) => kacir(a.ad)).join(" → ")}</p>
  </section>`;
}

function baslatGovdesi() {
  const K_ = D.kanal, mod = taslak.mod === "hazir" ? "hazir" : "konu";
  const onaylar = Object.fromEntries(K_.onay_secilebilir.map((o) => [o.kimlik, !!(taslak["uonay_" + o.kimlik] ?? K_.onaylar[o.kimlik])]));
  const diller = Object.keys(K_.hazir_diller);
  const dil = taslak.hazir_dil && K_.hazir_diller[taslak.hazir_dil] ? taslak.hazir_dil : diller[diller.length - 1];
  return mod === "hazir" ? { hazir: true, hazir_metin: taslak.hazir_metin || "", hazir_dil: dil, onaylar }
    : { konu_istegi: taslak.konu_istegi || "", onaylar };
}

function videolarKarti() {
  const satirlar = D.kanal.liste.map((v) => `<tr><td class="kod"><b>${kacir(v.kod)}</b></td><td>${kacir(v.baslik)}</td><td>${kacir(v.durum)}</td>
      <td>${kacir(v.sure)}${v.sahne ? " / " + v.sahne : ""}</td><td class="soluk kucuk">${v.salt_okunur ? "salt okunur" : v.rapor ? `<button class="dugme mini" data-eylem="liste-rapor" data-kod="${kacir(v.kod)}">Rapor</button>` : ""}</td></tr>`).join("");
  return `<section class="kart"><h2>Videolar</h2>
    <div class="tablo-kap"><table><thead><tr><th>Kod</th><th>Başlık</th><th>Durum</th><th>Süre / sahne</th><th></th></tr></thead>
    <tbody>${satirlar || `<tr><td colspan=5 class="soluk">Henüz video yok.</td></tr>`}</tbody></table></div>
  </section>`;
}


function ekranImzasi() {
  const u = D.uretim;
  return JSON.stringify([D.onkontrol, D.onkontrol_suruyor, D.kanallar, D.aktif, D.kanal, gorulenAsama, duzenlenen,
    u && [u.kod, u.durum.adim, u.durum.asamalar, u.calisiyor, u.flow, u.durum.silme_adaylari, u.durum.silme_karari]]);
}

async function yenile(zorla = false) {
  try { D = await api("/api/durum"); } catch (e) { $("#ana").innerHTML = `<p class="soluk">Uygulamaya ulaşılamıyor. Kapatılmış olabilir.</p>`; return; }
  maliyetCiz();
  const yeni = ekranImzasi();
  if (zorla || yeni !== imza) {
    imza = yeni; ustCiz();
    // Bir dialog içinde yazı yazılıyorsa ana ekran yine çizilir; dialoglar ayrı kaldığı için yazılanlar kaybolmaz.
    $("#ana").innerHTML = D.uretim && D.kanal ? uretimEkrani() : anaEkran();
    metinKutulari();
    uretimDosyasiYukle();
  } else if (D.uretim && $("#ilerleme")) {
    const el = $("#ilerleme");
    el.textContent = el.dataset.yazi === "1"
      ? (D.uretim.ilerleme ? D.uretim.ilerleme.toLocaleString("tr-TR") + " karakter" : "Başlıyor")
      : (D.uretim.ilerleme_metni || "Çalışıyor…");
  }
  if (!$("#kayit-paneli").hidden) kayitYukle();
}

// Kayıt paneli: kullanıcı yukarı kaydırdıysa ya da metin seçiyse yenileme onu aşağı atmaz.
let kayitSatirlari = [];
function kayitGorunen() {
  const yalnizHata = $("#kayit-hata")?.checked;
  const bloklar = [];
  for (const l of kayitSatirlari) { if (/^\d\d:\d\d:\d\d \[/.test(l) || !bloklar.length) bloklar.push(l); else bloklar[bloklar.length - 1] += "\n" + l; }
  return yalnizHata ? bloklar.filter((b) => /^\S+ \[(hata|uyari)\]/.test(b)) : bloklar;
}
async function kayitYukle(zorla = false) {
  const p = $("#kayit-icerik");
  const sel = window.getSelection();
  if (!zorla && sel && !sel.isCollapsed && p.contains(sel.anchorNode)) return;
  const altta = p.scrollHeight - p.scrollTop - p.clientHeight < 40;
  const j = await api("/api/kayit").catch(() => ({ satirlar: [] }));
  kayitSatirlari = j.satirlar.flatMap((x) => x.split("\n"));
  const yeni = kayitGorunen().join("\n");
  if (yeni !== p.textContent) {
    const ust = p.scrollTop;
    p.textContent = yeni;
    p.scrollTop = altta || zorla ? p.scrollHeight : ust;
  }
  $("#kayit-asagi").hidden = p.scrollHeight - p.scrollTop - p.clientHeight < 40;
}

// --- olaylar --------------------------------------------------------------

document.addEventListener("input", (e) => {
  const t = e.target;
  if (t.dataset.taslak) taslak[t.dataset.taslak] = t.type === "checkbox" ? t.checked : t.value;
  if (F && $("#kelime-bilgi") && ["uzunluk.hedef_dk", "dil.hedef", "ses.speed", "uzunluk.kelime_otomatik"].includes(t.dataset.yol)) {
    formOku($("#kanal-formu"), F.kanal); $("#kelime-bilgi").textContent = kelimeBilgi(F.kanal);
    if (t.dataset.yol === "uzunluk.kelime_otomatik") {
      document.querySelectorAll(".elle-kelime").forEach((x) => { x.hidden = t.checked; });
      const dk = Number(F.kanal.uzunluk.hedef_dk);
      if (!t.checked && dk >= 1 && dk <= 60) {  // elle ayara geçerken son hesaplanan değerlerden başla
        const tr = kelimeAraligi(F.kanal, "tr").aralik, hd = kelimeAraligi(F.kanal, F.kanal.dil.hedef).aralik;
        [["uzunluk.calisma_kelime.0", tr[0]], ["uzunluk.calisma_kelime.1", tr[1]], ["uzunluk.hedef_kelime.0", hd[0]], ["uzunluk.hedef_kelime.1", hd[1]]]
          .forEach(([y, v]) => { const el = document.querySelector(`[data-yol="${y}"]`); if (el) el.value = v; });
        formOku($("#kanal-formu"), F.kanal); $("#kelime-bilgi").textContent = kelimeBilgi(F.kanal);
      }
    }
  }
});

document.addEventListener("change", (e) => {
  if (e.target.id === "kayit-hata") kayitYukle(true);
  if (e.target.name === "hazir-dil") { imza = ""; yenile(true); }  // dil değişince atlanan onaylar güncellensin
  if (e.target.id === "kanal-secici") yap(() => api("/api/kanal/sec", { kisaltma: e.target.value }));
  if (e.target.name === "kaynak" && $("#ice-klasor")) $("#ice-klasor").disabled = e.target.value !== "klasor";
  if (e.target.type === "color") e.target.nextElementSibling.textContent = e.target.value;
  if (e.target.id === "kf-dosya" && e.target.files[0]) {
    const r = new FileReader();
    r.onload = () => { $("#kf-metin").value = r.result; };
    r.readAsText(e.target.files[0], "utf-8");
  }
});

document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-eylem]");
  if (!el) return;
  const k = el.dataset.kimlik;
  const eylemler = {
    ...uretimEylemleri(el, k),
    onkontrol: () => yap(() => api("/api/onkontrol", {})),
    "kanal-ekle": () => kanalEkleAc(),
    "kanal-ayar": () => kanalAyarAc(),
    "kanal-sil": () => silAc().catch((x) => bildir(x.message)),
    "klasor-ac": () => api("/api/kanal/klasor-ac", { kisaltma: D.aktif }).catch((x) => bildir(x.message)),
    "kf-ileri": () => kfIleri(1),
    "kf-geri": () => kfIleri(-1),
    "kf-kaydet": () => kfKaydet(),
    "kf-kapat": () => { $("#kanal-pencere").close(); F = null; },
    "kf-yol": () => { if (F.yol === "dosya" && $("#kf-metin")) F.metin = $("#kf-metin").value; F.yol = el.dataset.secim; F.adim = 0; F.hatalar = []; F.uyarilar = []; kanalFormuCiz(); },
    "kf-sablon-kopyala": () => api("/api/kanal/sablon").then((j) => kopyala(j.metin)).catch((x) => bildir(x.message)),
    "kf-dosya-oku": () => kfDosyaOku(),
    "kf-dosya-geri": () => { formuAl(); F.okundu = false; F.hatalar = []; F.uyarilar = []; kanalFormuCiz(); },
    "dosya-ac": () => dosyaAc(el.dataset.ad).catch((x) => bildir(x.message)),
    "dosya-kopyala": () => kopyala($("#dosya-metin").value),
    "dosya-kapat": () => $("#dosya-pencere").close(),
    "dosya-kaydet": () => yap(async () => {
      await api("/api/kanal/dosya", { kanal: D.aktif, ad: $("#dosya-metin").dataset.ad, icerik: $("#dosya-metin").value });
      $("#dosya-pencere").close(); bildir("Dosya kaydedildi.");
    }),
    "sil-kapat": () => $("#sil-pencere").close(),
    "sil-onayla": () => yap(async () => {
      const ad = D.kanal.ayar.ad;
      const j = await api("/api/kanal/sil", { kisaltma: D.aktif, onay_adi: $("#sil-ad").value });
      $("#sil-pencere").close();
      bildir(`${ad} silindi: ${j.tasinan.length} öğe Çöp Kutusu'na taşındı.`);
    }),
    ayarlar: () => { $("#ayar-formu").innerHTML = ayarFormu(); $("#ayar-penceresi").showModal(); },
    "ayar-kapat": () => $("#ayar-penceresi").close(),
    "ayar-kaydet": () => yap(async () => {
      await api("/api/ayarlar", { butce: { aylik_usd: Number($("#aylik").value) }, yollar: { capcut_taslak: $("#yol-capcut").value.trim() },
        onbellek_suresi: $("#onbellek").value, saglayici: $("#saglayici").value });
      $("#ayar-penceresi").close(); bildir("Ayarlar kaydedildi.");
    }),
    "anahtar-kaydet": () => yap(async () => { const t = el.dataset.tur; await api("/api/anahtar", { tur: t, anahtar: $("#anahtar-" + t).value }); $("#ayar-penceresi").close(); bildir("Anahtar kaydedildi."); }),
    "anahtar-sil": () => yap(async () => { const t = el.dataset.tur; if (confirm("Anahtar silinsin mi?")) { await api("/api/anahtar", { tur: t, sil: true }); $("#ayar-penceresi").close(); } }),
    "anahtar-test": async () => {
      const t = el.dataset.tur, s = $("#anahtar-sonuc-" + t);
      s.textContent = "Deneniyor…"; el.disabled = true;
      try { const j = await api("/api/anahtar-test", { tur: t, anahtar: $("#anahtar-" + t)?.value || "" }); s.textContent = (j.tamam ? "✓ " : "✗ ") + j.mesaj; s.style.color = j.tamam ? "var(--tamam)" : "var(--hata)"; }
      catch (x) { s.textContent = "✗ " + x.message; s.style.color = "var(--hata)"; }
      finally { el.disabled = false; }
    },
    kayit: () => { const p = $("#kayit-paneli"); p.hidden = !p.hidden; if (!p.hidden) kayitYukle(true); },
    "kayit-kopyala": () => kopyala(kayitGorunen().join("\n")),
    "kayit-son-hata": () => { const h = kayitGorunen().filter((b) => /^\S+ \[hata\]/.test(b)).pop(); h ? kopyala(h) : bildir("Kayıtta hata yok."); },
    "kayit-dosya": () => api("/api/kayit/ac", {}).then(() => bildir("Tüm geçmiş Not Defteri'nde açıldı.")).catch((x) => bildir(x.message)),
    "kayit-buyut": () => { const p = $("#kayit-paneli"); p.classList.toggle("buyuk"); el.textContent = p.classList.contains("buyuk") ? "Küçült" : "Büyüt"; },
    "kayit-en-alt": () => { const p = $("#kayit-icerik"); p.scrollTop = p.scrollHeight; $("#kayit-asagi").hidden = true; },
    kapat: () => { if (confirm("Kanal Stüdyosu kapatılsın mı? Süren bir yazım varsa yarıda kalır; sonra kaldığı yerden devam edebilirsin.")) api("/api/kapat", {}).then(() => { document.body.innerHTML = "<p style='padding:30px'>Uygulama kapatıldı. Bu sekmeyi kapatabilirsin.</p>"; }); },
  };
  (eylemler[el.dataset.eylem] || (() => {}))();
});

function uretimEylemleri(el, k) {
  return {
    "baslat-mod": () => { taslak.mod = el.dataset.mod; imza = ""; yenile(true); },
    baslat: () => yap(async () => {
      const g = baslatGovdesi();
      if (g.hazir && !g.hazir_metin.trim()) throw new Error("Metni yapıştır.");
      await api("/api/uretim/baslat", g);
      bildir(g.hazir ? "Üretim başladı: hazır metin hazırlanıyor (konu kartı, sahne paragrafları, etiketler)." : "Üretim başladı: 1. aşama yazılıyor.");
      delete taslak.hazir_metin;
    }),
    onay: () => yap(async () => {
      if (duzenlenen && !confirm("Kaydedilmemiş bir düzenlemen var; onay kayıtlı hâli kullanır. Yine de onaylansın mı?")) return;
      duzenlenen = null;
      await api("/api/asama/onay", { kimlik: k, not: taslak["onay_" + k] || "" }); delete taslak["onay_" + k];
    }),
    duzeltme: () => yap(async () => {
      if (duzenlenen && !confirm("Kaydedilmemiş bir düzenlemen var; önce 'Kaydet ve kontrol et'e basmazsan model onu görmez. Yine de gönderilsin mi?")) return;
      duzenlenen = null; await api("/api/asama/duzeltme", { kimlik: k, not: taslak["duz_" + k] || "" }); delete taslak["duz_" + k];
    }),
    tekrar: () => yap(() => api("/api/asama/tekrar", { butce_onayli: el.dataset.butce === "1" })),
    devam: () => yap(() => api("/api/asama/devam", {})),
    "flow-kontrol": () => yap(() => api("/api/asama/flow-kontrol", {})),
    "flow-sorun-devam": () => yap(() => api("/api/asama/flow-sorun-devam", {})),
    "flow-a5": () => yap(async () => { await api("/api/asama/flow-a5-duzeltme", { not: taslak.flow_duz || "" }); delete taslak.flow_duz; }),
    partiler: () => partilerGoster(),
    "parti-kopyala": () => partiKopyala(Number(el.dataset.i)),
    kopyala: () => kopyala(el.dataset.metin),
    silme: () => yap(async () => { const j = await api("/api/asama/silme", { tasi: el.dataset.tasi === "1" }); bildir(j.tasinan.length ? `${j.tasinan.length} dosya Silinecekler'e taşındı.` : "Dosyalar yerinde kaldı."); }),
    "muzik-yenile": async () => {
      if (!confirm("Müzik yeni rastgele parçalarla yeniden yapılsın mı?\n\nCapCut kapalı olmalı. Taslaktaki müzik değişir; eski müzik dosyası ve taslak arşive kopyalanır, silinmez. 1–2 dakika sürebilir.")) return;
      el.disabled = true; el.textContent = "Yapılıyor…";
      try { const j = await api("/api/asama/muzik-yenile", {}); bildir("Müzik yenilendi. " + j.secilen); }
      catch (x) { bildir(x.message); }
      finally { imza = ""; yenile(true); }
    },
    "uretim-kapat": () => { if (confirm("Üretim kapatılsın mı? Dosyaların hepsi yerinde kalır.")) yap(async () => { await api("/api/asama/kapat", {}); gorulenAsama = null; secilenDosya = {}; }); },
    durdur: () => yap(async () => { await api("/api/asama/durdur", {}); bildir("Durduruluyor…"); }),
    iptal: () => {
      if (!confirm("Bu üretim iptal edilsin mi?\n\nHiçbir dosya silinmez: bu videonun klasörleri kanalın Arsiv klasörüne (…_iptal_tarih) taşınır, Aktif Video dosyası bu üretimden önceki hâline döner ve aynı kod bir sonraki üretimde yeniden kullanılır.\n\nÇalışan bir adım varsa önce Durdur'a bas.")) return;
      yap(async () => {
        const j = await api("/api/asama/iptal", {});
        let m = `İptal edildi. Dosyalar: ${j.klasor}.`;
        if (j.capcut_taslak) m += " CapCut taslağı yerinde bırakıldı.";
        bildir(m); gorulenAsama = null; secilenDosya = {};
      });
    },
    rapor: async () => { const r = $("#rapor"); r.hidden = !r.hidden; if (!r.hidden) r.textContent = (await api("/api/rapor").catch((x) => ({ icerik: x.message }))).icerik; },
    "kutu-kopyala": () => kopyala(el.closest(".kutu-kap").lastElementChild.innerText),
    "kutu-buyut": () => {
      const hedef = el.closest(".kutu-kap").lastElementChild;
      const bas = hedef.closest("section")?.querySelector("h2, h3");
      $("#buyuk-baslik").textContent = hedef.dataset.ad || (bas ? bas.textContent : "Metin");
      $("#buyuk-icerik").textContent = hedef.innerText;
      $("#buyuk-pencere").showModal();
    },
    "liste-rapor": async () => {
      const kod = el.dataset.kod;
      $("#buyuk-baslik").textContent = `${kod} · Üretim raporu`;
      $("#buyuk-icerik").textContent = "Yükleniyor…";
      $("#buyuk-pencere").showModal();
      $("#buyuk-icerik").textContent = (await api("/api/rapor?kod=" + encodeURIComponent(kod)).catch((x) => ({ icerik: x.message }))).icerik;
    },
    "buyuk-kopyala": () => kopyala($("#buyuk-icerik").textContent),
    "buyuk-kapat": () => $("#buyuk-pencere").close(),
    sekme: () => {
      if (duzenlenen && !confirm("Düzenlemen kaydedilmedi. Başka dosyaya geçilsin mi? (Yazdıkların bu pencerede saklı kalır.)")) return;
      duzenlenen = null; secilenDosya[k] = el.dataset.ad; imza = ""; yenile(true);
    },
    "elle-ac": () => { duzenlenen = { kimlik: k, ad: el.dataset.ad }; imza = ""; yenile(true); },
    "elle-vazgec": () => { if (duzenlenen) delete taslak[`elle_${duzenlenen.kimlik}_${duzenlenen.ad}`]; duzenlenen = null; imza = ""; yenile(true); },
    "elle-kaydet": () => yap(async () => {
      const anahtar = `elle_${k}_${el.dataset.ad}`;
      const j = await api("/api/asama/elle", { kimlik: k, ad: el.dataset.ad, icerik: $("#uretim-duzenle").value });
      delete taslak[anahtar]; duzenlenen = null;
      const h = j.kontrol?.hatalar?.length || 0, u = j.kontrol?.uyarilar?.length || 0;
      bildir(h ? `Kaydedildi. Kontrol ${h} sorun buldu; aşağıda listelendi.` : u ? `Kaydedildi. ${u} uyarı var.` : "Kaydedildi. Kontrollerden geçti.");
    }),
    "elle-geri": () => yap(async () => {
      if (!confirm("Bu dosya modelin yazdığı hâline dönsün mü? Elle yaptığın değişiklikler kaybolur.")) return;
      await api("/api/asama/elle-geri", { kimlik: k, ad: el.dataset.ad });
      delete taslak[`elle_${k}_${el.dataset.ad}`]; duzenlenen = null; bildir("Modelin yazdığı hâle dönüldü.");
    }),
    gor: () => { gorulenAsama = k; yenile(true); },
    geri: () => { gorulenAsama = null; yenile(true); },
    bakiye: () => api("/api/bakiye", {}).then(() => setTimeout(() => yenile(), 1500)),
    "hata-kopyala": () => kopyala(D.uretim?.durum?.asamalar?.[k]?.hata + "\n\n" + (D.uretim?.durum?.asamalar?.[k]?.hata_ayrinti || "")),
  };
}

function dongu() { yenile().finally(() => setTimeout(dongu, D && (D.uretim?.calisiyor || D.onkontrol_suruyor) ? 1500 : 4000)); }
dongu();
document.addEventListener("DOMContentLoaded", () => {
  const p = $("#kayit-icerik");
  if (p) p.addEventListener("scroll", () => { $("#kayit-asagi").hidden = p.scrollHeight - p.scrollTop - p.clientHeight < 40; });
});
```

### `app/kanal_studyosu/web/stil.css`

```css
:root {
  --zemin: #f7f0e1;
  --kart: #fffaf0;
  --kart2: #f1e7d3;
  --cizgi: #e2d5bb;
  --yazi: #2a2520;
  --soluk: #7a6d5f;
  --vurgu: #8e3f37;
  --vurgu-yazi: #fff;
  --amber: #d9a441;
  --adacayi: #5f8a6e;
  --tamam: #3f7d55;
  --uyari: #b07a1a;
  --hata: #a83a32;
  --golge: 0 1px 2px rgba(60, 40, 20, .06), 0 4px 16px rgba(60, 40, 20, .06);
}
@media (prefers-color-scheme: dark) {
  :root {
    --zemin: #1d1915; --kart: #26211c; --kart2: #2f2922; --cizgi: #3d352c;
    --yazi: #f1e9dc; --soluk: #b3a593; --vurgu: #c76a5f; --amber: #e0b35a;
    --adacayi: #87b096; --tamam: #7cc391; --uyari: #e0b35a; --hata: #e37d73;
    --golge: 0 1px 2px rgba(0, 0, 0, .3);
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--zemin); color: var(--yazi);
  font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
button, input, textarea, select { font: inherit; color: inherit; }
.ust { position: sticky; top: 0; z-index: 5; display: flex; justify-content: space-between; align-items: center;
  gap: 12px; padding: 12px 24px; background: color-mix(in srgb, var(--zemin) 92%, transparent);
  backdrop-filter: blur(10px); border-bottom: 1px solid var(--cizgi); flex-wrap: wrap; }
.marka { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 17px; }
.logo { display: inline-grid; place-items: center; width: 32px; height: 32px; border-radius: 9px;
  background: var(--vurgu); color: var(--vurgu-yazi); font-weight: 800; }
.ust-sag { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.maliyet { font-size: 13px; color: var(--soluk); padding: 4px 10px; border: 1px solid var(--cizgi);
  border-radius: 999px; background: var(--kart); white-space: nowrap; }
.maliyet b { color: var(--yazi); }
.ana { max-width: 1100px; margin: 0 auto; padding: 24px 16px 80px; }
.kart { background: var(--kart); border: 1px solid var(--cizgi); border-radius: 14px; padding: 20px;
  margin-bottom: 18px; box-shadow: var(--golge); }
.kart h2 { margin: 0 0 12px; font-size: 18px; }
.kart h3 { margin: 18px 0 8px; font-size: 15px; }
.soluk { color: var(--soluk); }
.kucuk { font-size: 13px; }
.dugme { border: 1px solid var(--cizgi); background: var(--kart2); padding: 9px 16px; border-radius: 10px;
  cursor: pointer; font-weight: 600; }
.dugme:hover { border-color: var(--soluk); }
.dugme.ana-dugme { background: var(--vurgu); color: var(--vurgu-yazi); border-color: var(--vurgu); }
.dugme.ince { padding: 5px 11px; font-size: 13px; }
.dugme.tehlike { color: var(--hata); }
.dugme:disabled { opacity: .45; cursor: not-allowed; }
textarea, input[type=text], input[type=password], input[type=number], select {
  width: 100%; background: var(--zemin); border: 1px solid var(--cizgi); border-radius: 9px; padding: 9px 11px; }
textarea { min-height: 90px; resize: vertical; }
label { display: block; font-weight: 600; margin: 12px 0 5px; font-size: 14px; }
.satir { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.satir > * { flex: 0 0 auto; }
.izgara2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 700px) { .izgara2 { grid-template-columns: 1fr; } .ust { padding: 10px 16px; } }

.kontrol-listesi { list-style: none; margin: 0; padding: 0; }
.kontrol-listesi li { display: flex; gap: 10px; padding: 7px 0; border-bottom: 1px dashed var(--cizgi); }
.kontrol-listesi li:last-child { border-bottom: 0; }
.isaret { flex: 0 0 22px; font-weight: 800; }
.isaret.tamam { color: var(--tamam); } .isaret.yok { color: var(--hata); } .isaret.bilgi { color: var(--uyari); }

table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--cizgi); vertical-align: top; }
td.kod { white-space: nowrap; }
th { color: var(--soluk); font-weight: 600; font-size: 13px; }
.tablo-kap { overflow-x: auto; }

.adimlar { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 18px; }
.adim { padding: 6px 12px; border-radius: 999px; border: 1px solid var(--cizgi); background: var(--kart);
  font-size: 13px; color: var(--soluk); cursor: default; }
.adim.tamam { color: var(--tamam); border-color: color-mix(in srgb, var(--tamam) 45%, var(--cizgi)); cursor: pointer; }
.adim.simdi { background: var(--vurgu); color: var(--vurgu-yazi); border-color: var(--vurgu); }
.adim.yakinda { opacity: .5; }
.adim.atlandi { opacity: .45; text-decoration: line-through; }

.yukleniyor { display: flex; align-items: center; gap: 14px; }
.donen { width: 22px; height: 22px; border-radius: 50%; border: 3px solid var(--cizgi); border-top-color: var(--vurgu);
  animation: don 1s linear infinite; flex: 0 0 auto; }
@keyframes don { to { transform: rotate(360deg); } }

.etiketler { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0; }
.etiket { font-size: 12.5px; padding: 3px 9px; border-radius: 999px; background: var(--kart2); border: 1px solid var(--cizgi); }
.notlar { margin: 8px 0; padding-left: 20px; }
.notlar li { margin: 3px 0; }
.notlar.hata li { color: var(--hata); }
.notlar.uyari li { color: var(--uyari); }
.ozet { white-space: pre-wrap; background: var(--zemin); border: 1px solid var(--cizgi); border-radius: 10px;
  padding: 12px; font-size: 13.5px; max-height: 260px; overflow: auto; }
.sekmeler { display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0 0; }
.sekme { padding: 6px 12px; border-radius: 9px 9px 0 0; border: 1px solid var(--cizgi); border-bottom: 0;
  background: var(--kart2); cursor: pointer; font-size: 13px; }
.sekme.secili { background: var(--zemin); font-weight: 700; }
.dosya { white-space: pre-wrap; background: var(--zemin); border: 1px solid var(--cizgi); border-radius: 0 10px 10px 10px;
  padding: 16px; font: 14px/1.6 ui-serif, Georgia, serif; max-height: 60vh; overflow: auto; margin: 0; }
.onay-alani { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
@media (max-width: 700px) { .onay-alani { grid-template-columns: 1fr; } }
.kutu { border: 1px solid var(--cizgi); border-radius: 12px; padding: 14px; background: var(--zemin); }
.kutu h3 { margin-top: 0; }

.pencere { border: 1px solid var(--cizgi); border-radius: 16px; background: var(--kart); color: var(--yazi);
  width: min(760px, calc(100vw - 32px)); padding: 22px; max-height: 88vh; }
.pencere::backdrop { background: rgba(30, 20, 10, .35); }
.kayit-paneli { position: fixed; left: 0; right: 0; bottom: 0; height: 38vh; background: var(--kart);
  border-top: 1px solid var(--cizgi); z-index: 9; display: flex; flex-direction: column; }
.kayit-paneli[hidden] { display: none; }
.kayit-baslik { display: flex; justify-content: space-between; align-items: center; padding: 8px 16px;
  border-bottom: 1px solid var(--cizgi); }
#kayit-icerik { margin: 0; padding: 10px 16px; overflow: auto; flex: 1; font-size: 12px; white-space: pre-wrap; }
.bildirim { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--yazi);
  color: var(--zemin); padding: 10px 18px; border-radius: 10px; z-index: 20; max-width: calc(100vw - 32px); }

.bakiye { cursor: pointer; background: transparent; font: inherit; font-size: 13px; }
.bakiye:hover { border-color: var(--soluk); }
.bakiye.az { border-color: var(--uyari); }
.bakiye .az-deger, .bakiye .az-deger b { color: var(--uyari); }
.bakiye[hidden] { display: none; }

textarea.dosya.duzenle { width: 100%; min-height: 460px; font: inherit; font-size: 14px; line-height: 1.55; color: var(--yazi);
  padding: 14px; resize: vertical; box-sizing: border-box; }
.acik-noktalar { margin: 4px 0 10px; }
.acik-noktalar.uyari { color: var(--uyari); }
.kayit-paneli.buyuk { height: 80vh; }
.kayit-baslik .satir { flex-wrap: wrap; justify-content: flex-end; }
.kayit-asagi { position: absolute; right: 20px; bottom: 14px; }
.kayit-paneli { position: fixed; }
#kayit-icerik { user-select: text; }
.hata-ayrinti { margin: 8px 0 12px; }
.hata-ayrinti pre { max-height: 320px; overflow: auto; white-space: pre-wrap; font-size: 12px; user-select: text; }

.kutu-kap { position: relative; }
.kutu-kap:has(> [hidden]) { display: none; }
.kutu-arac { position: absolute; top: 6px; right: 8px; display: flex; gap: 4px; z-index: 2; opacity: .55; }
.kutu-kap:hover .kutu-arac { opacity: 1; }
.dugme.mini { padding: 3px 8px; font-size: 12px; }
.kutu-kap > pre, .kutu-kap > div.ozet { user-select: text; }
.buyuk-pencere { width: min(1200px, 96vw); max-height: 92vh; }
#buyuk-icerik { white-space: pre-wrap; max-height: 78vh; overflow: auto; margin: 0; padding: 12px; font-size: 14px; line-height: 1.55;
  background: var(--zemin); border: 1px solid var(--cizgi); border-radius: 10px; user-select: text; }

/* --- Kanal Stüdyosu --- */
.kanal-sec { display: flex; align-items: center; gap: 6px; }
.kanal-sec select { width: auto; min-width: 180px; padding: 5px 10px; font-size: 14px; }
.adim-cubugu { display: flex; gap: 6px; flex-wrap: wrap; margin: 4px 0 14px; }
.adim-cubugu span { font-size: 12.5px; padding: 3px 9px; border-radius: 999px; border: 1px solid var(--cizgi); color: var(--soluk); }
.adim-cubugu span.simdi { background: var(--vurgu); color: var(--vurgu-yazi); border-color: var(--vurgu); }
.adim-cubugu span.gecti { color: var(--tamam); }
.alan-aciklama { margin: 3px 0 0; font-size: 12.5px; color: var(--soluk); }
.alan-cift { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.bolum-baslik { margin: 22px 0 4px; padding-top: 12px; border-top: 1px solid var(--cizgi); }
.bolum-baslik:first-child { border-top: 0; padding-top: 0; margin-top: 0; }
.kanal-karti .bilgi { display: grid; grid-template-columns: max-content 1fr; gap: 4px 14px; font-size: 14px; }
.dosya-listesi li { display: flex; justify-content: space-between; gap: 10px; padding: 6px 0; border-bottom: 1px dashed var(--cizgi); cursor: pointer; }
.dosya-listesi { list-style: none; padding: 0; margin: 0; }
.dosya-listesi li:hover b { text-decoration: underline; }
.rozet { font-size: 12px; padding: 1px 8px; border-radius: 999px; border: 1px solid var(--cizgi); }
.rozet.uyari { color: var(--uyari); border-color: var(--uyari); }
.rozet.tamam { color: var(--tamam); }
textarea.dosya-duzenle { min-height: 55vh; font: 14px/1.55 ui-monospace, Menlo, monospace; }
.tehlike-kutu { border: 1px solid var(--hata); border-radius: 12px; padding: 14px; }
input[type=color] { width: 48px; height: 36px; padding: 2px; border: 1px solid var(--cizgi); border-radius: 8px; background: var(--zemin); }
.alan-cift .alan label.satir { margin-top: 38px; }

/* Kanal ekle: yol seçimi, dosyayla ekleme ve katlanan gelişmiş ayarlar */
.secim-kartlari { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 8px; }
.secim-karti { display: flex; flex-direction: column; gap: 6px; text-align: left; padding: 14px 16px; border: 1px solid var(--cizgi); border-radius: 12px; background: var(--kart); color: inherit; font: inherit; cursor: pointer; }
.secim-karti:hover { border-color: var(--vurgu); }
.secim-karti .oneri { font-size: 11.5px; font-weight: 500; padding: 1px 7px; border-radius: 999px; background: var(--vurgu); color: var(--vurgu-yazi); margin-left: 6px; }
details.gelismis { margin: 12px 0 4px; border: 1px dashed var(--cizgi); border-radius: 10px; padding: 6px 12px; }
details.gelismis > summary { cursor: pointer; font-size: 13px; color: var(--soluk); padding: 4px 0; }
details.gelismis[open] > summary { margin-bottom: 6px; }
.eksik-alan { border-left: 3px solid var(--hata); padding-left: 10px; }
.hata-yazi { color: var(--hata); }
.alan-cift[hidden] { display: none; }
```

### `app/config/kanal_varsayilan.json`

```json
{
  "surum": 1,
  "ad": "",
  "kisaltma": "",
  "kod_oneki": "",
  "kod_hane": 2,
  "dil": {
    "calisma": "tr",
    "hedef": "en"
  },
  "uzunluk": {
    "hedef_dk": 12,
    "kelime_otomatik": true,
    "calisma_kelime": [
      1600,
      1800
    ],
    "hedef_kelime": [
      1950,
      2050
    ],
    "kart_karakter": 3500,
    "hook_esigi": 9,
    "hiz_olcum": {}
  },
  "ses": {
    "voice_id": "",
    "voice_name": "",
    "model_id": "eleven_v3",
    "language_code": "en",
    "output_format": "mp3_44100_128",
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0,
    "speed": 1,
    "use_speaker_boost": true
  },
  "gorsel": {
    "karakter": "",
    "kurallar": "Görselde okunabilir yazı, harf ya da logo olmaz. Metafor ve şema sahnelerinde karakter yoktur; tek sembol ya da ok/şekil dili kullanılır. Her cümlenin birebir resmi olması gerekmez: aynı mekân, duygu ya da nesne cümleyi taşıyorsa uyum vardır.",
    "ifade_notu": "",
    "yasakli": [
      "child",
      "children",
      "kid",
      "girl",
      "boy",
      "little girl",
      "baby",
      "teen",
      "daughter",
      "son",
      "hug",
      "kiss",
      "lap",
      "cuddle",
      "stroke hair",
      "whisper in ear",
      "bath",
      "bed",
      "bedroom",
      "pajamas",
      "cry",
      "tears",
      "tearful",
      "sob",
      "scared",
      "fear",
      "afraid",
      "frightening",
      "alone",
      "lonely",
      "hide",
      "trapped",
      "locked",
      "hurt",
      "pain",
      "hit",
      "shout",
      "angry",
      "punish",
      "abuse",
      "violence",
      "threat",
      "danger",
      "unsafe",
      "safe",
      "protected",
      "dark",
      "darkness",
      "dim",
      "shadowy",
      "gloomy",
      "pitch black",
      "ghost",
      "translucent figure",
      "faint figure",
      "blood",
      "wound",
      "knife",
      "pills",
      "medicine",
      "red"
    ],
    "izinli_olumsuz": [
      "text",
      "letters",
      "numbers",
      "readable words",
      "writing",
      "logo",
      "people",
      "characters"
    ],
    "flow_model": "Nano Banana 2",
    "oran": "16:9"
  },
  "etiketler": {
    "senaryo": {
      "karakter": "KARAKTER",
      "metafor": "METAFOR",
      "sema": "DIAGRAM",
      "ilk30": "★30sn"
    },
    "ses": [
      "calm",
      "softly",
      "warm",
      "serious",
      "hopeful",
      "whispers"
    ],
    "ses_sinir": {
      "whispers": 2
    },
    "tag_orani": 25
  },
  "montaj": {
    "muzik": true,
    "muzik_lufs": -38,
    "son_ekran_sn": 8,
    "maskot": {
      "dosyalar": [],
      "sira": []
    },
    "altyazi": {
      "yazi_tipi": "Nunito",
      "yazi": "#3B2A1E",
      "kutu": "#FFF6E4",
      "kutu_opaklik": 0.88,
      "boyut": 8
    },
    "video": {
      "width": 1920,
      "height": 1080,
      "fps": 30,
      "fit": "blur",
      "pause_seconds": 0.4,
      "tolerance_seconds": 0.3,
      "loudness": "youtube",
      "kenar": {
        "ornek_esigi": 8,
        "blok_ms": 5,
        "blok_db": -50,
        "bosluk_blok": 12,
        "tik_ms": 30,
        "tik_sessizlik_ms": 300,
        "onset_blok_ms": 10,
        "onset_db": -45,
        "onset_pay": 0.025,
        "fade_in": 0.01,
        "fade_in_basta": 0.004,
        "fade_out": 0.03,
        "kontrol_geri_ms": 12,
        "kontrol_tepe": 300,
        "kontrol_taban": 30,
        "sert_db": 25,
        "sert_dbfs": -35,
        "orta_db": 20,
        "orta_dbfs": -45
      }
    }
  },
  "hassas_kelimeler": [],
  "onaylar": {
    "konu": true,
    "arastirma": true,
    "senaryo": true,
    "ceviri": true,
    "paketleme": true
  },
  "isler": {
    "konu": {
      "model": "claude-sonnet-5-5",
      "efor": "medium",
      "web_arama": 6,
      "max_token": 32000
    },
    "arastirma": {
      "model": "claude-sonnet-5-5",
      "efor": "medium",
      "web_arama": 12,
      "max_token": 64000
    },
    "senaryo": {
      "model": "claude-opus-5-5",
      "efor": "medium",
      "max_token": 128000
    },
    "ceviri": {
      "model": "claude-opus-5-5",
      "efor": "medium",
      "max_token": 128000
    },
    "sahne": {
      "model": "claude-sonnet-5-5",
      "efor": "medium",
      "max_token": 128000
    },
    "paketleme": {
      "model": "claude-opus-5-5",
      "efor": "medium",
      "max_token": 64000
    },
    "hazir": {
      "model": "claude-sonnet-5-5",
      "efor": "low",
      "max_token": 32000
    },
    "bolumler": {
      "model": "claude-haiku-4-5",
      "max_token": 8000
    },
    "bolumler_yedek": {
      "model": "claude-sonnet-5-5",
      "efor": "medium",
      "max_token": 16000
    },
    "odak": {
      "model": "claude-haiku-4-5",
      "max_token": 4000
    },
    "odak_yedek": {
      "model": "claude-sonnet-5-5",
      "efor": "medium",
      "max_token": 8000
    },
    "defter": {
      "model": "claude-sonnet-5-5",
      "efor": "medium",
      "max_token": 64000
    },
    "uyum": {
      "model": "claude-sonnet-5-5",
      "efor": "medium",
      "max_token": 16000
    },
    "rapor": {
      "model": "claude-haiku-4-5",
      "max_token": 4000
    }
  },
  "butce": {
    "video_usd": 8
  },
  "kalip_sayaclari": {},
  "imza": ""
}
```

### `app/config/varsayilan.json`

```json
{
  "yollar": {
    "capcut_taslak": "%LOCALAPPDATA%/CapCut/User Data/Projects/com.lveditor.draft"
  },
  "butce": {
    "aylik_usd": 40
  },
  "onbellek_suresi": "5m",
  "saglayici": "claude_code",
  "openrouter": {
    "modeller": {
      "claude-opus-5-5": "anthropic/claude-opus-5.5",
      "claude-sonnet-5-5": "anthropic/claude-sonnet-5.5",
      "claude-haiku-4-5": "anthropic/claude-haiku-4.5"
    }
  },
  "duzeltme_tur_siniri": 2,
  "modeller": {
    "claude-opus-5-5": {
      "ad": "Opus 5.5",
      "giris": 4.0,
      "cikis": 20.0,
      "onbellek_okuma": 0.2,
      "efor": true,
      "yedek_model": true
    },
    "claude-sonnet-5-5": {
      "ad": "Sonnet 5.5",
      "giris": 2.0,
      "cikis": 10.0,
      "onbellek_okuma": 0.2,
      "efor": true,
      "yedek_model": true
    },
    "claude-haiku-4-5": {
      "ad": "Haiku 4.5",
      "giris": 1.0,
      "cikis": 5.0,
      "onbellek_okuma": 0.1,
      "efor": false,
      "yedek_model": false
    },
    "claude-opus-5": {
      "ad": "Opus 5",
      "giris": 5.0,
      "cikis": 25.0,
      "onbellek_okuma": 0.5,
      "efor": true,
      "yedek_model": false
    },
    "claude-opus-4-8": {
      "ad": "Opus 4.8",
      "giris": 5.0,
      "cikis": 25.0,
      "onbellek_okuma": 0.5,
      "efor": true,
      "yedek_model": false
    },
    "claude-sonnet-5": {
      "ad": "Sonnet 5",
      "giris": 2.0,
      "cikis": 10.0,
      "onbellek_okuma": 0.2,
      "efor": true,
      "yedek_model": false
    }
  },
  "web_arama_1000_usd": 10.0
}
```

### `app/sablonlar/kanal/Beceriler/arastirma/SKILL.md`

````markdown
---
name: "arastirma"
description: "{{KANAL_ADI}} 2. aşama: onaylı konu kartı için web araştırması (bilgi kazancı doğrulama, izleyici dili, rakip boşluğu, güvenlik) ve Türkçe outline."
---

# Aşama 2 — Araştırma + Türkçe outline

Esas: `00_Yonetici`, `01_Anayasa` (§4 metot, §5 yapı, §6 tekrar yasağı, §8 güvenlik, §12 metafor bankası),
`02_Defter` (F), onaylı konu kartı (`03_Aktif_Video.md`). Senaryo YAZILMAZ; yalnız araştırma ve plan yapılır.

## Adım 1 — Araştırma (web araması)
Hızlı ve isabetli: 6–12 arama. Her bulgu kısa.
1. **Bilgi kazancı doğrulama:** karttaki her aday için güvenilir kaynak (resmî site, ansiklopedi, üniversite, yasa metni,
   saygın basın). Sonuç: ✓ Doğrulandı (doğru ifade + kaynak, iç not) · ~ Yumuşatılmalı (nasıl söyleneceği) · ✗ Çıkar.
   Videoda künye, sayı ve yüzde olmaz; kaynak listesi yalnız iç doğrulama içindir. Doğrulanan 3'ün altındaysa yeni aday bul.
1b. **İddia sınıflaması:** her mekanizma/neden iddiası: Doğrulanmış · Dikkatli ifade (ihtimal kipi) · Alternatif açıklama
   var · Kullanma (kesinlik, tek nedene indirgeme, korelasyonu nedensellik gibi sunma, teşhis). Tablo: iddia · sınıf ·
   videoda nasıl söylenecek.
2. **İzleyici dili ({{HEDEF_DIL}}):** izleyicilerin bu konuyu nasıl söylediği (forum, yorum, gündelik kalıp); 8–12 gerçek
   ifade. Yapay ya da teknik duyulanları ayrı listele.
3. **Rakip boşluğu:** benzer videolar neyi atlıyor? En fazla 3 madde; kanalın farkı 1 cümle.
4. **Güvenlik:** hassas noktalar (01_Anayasa §8). Gerekiyorsa outline'ın ilgili bölümüne bir cümlelik baskısız çerçeve
   yönü yaz. Kullanıcının ayrıca bakması gereken yer sohbet cevabındaki «Açık noktalar» satırına; dosyada köşeli
   parantezli işaret yok.

## Adım 2 — Türkçe outline (plan, tam metin değil)
Hedef süre ve kelime aralıkları KANAL AYARLARI'nda. Bölüm başına yaklaşık süre ve kelime yaz.
```
OUTLINE · {{KOD_ONEKI}}-0X
Açılış tipi: <harf> (son 3 videodan farklı ✓) · Köprü tipi: … · CTA tipi: …
Kal cümlesi yönü (4. paragraf): …
§1 DOUBLE HOOK (0:00–0:30, ~6 beat)
  B1 (0–8 sn): kapak anı = … (ilk cümle ≤10 kelime, somut)
  B2–B3 (8–15 sn): beklenti kırılması …
  B4–B6 (15–30 sn): vaat + açık döngü …
§2 … (m:ss–m:ss, ~NNN kelime) — amaç · somut sahne · mekanik · bilgi kazancı #N · etiket önerisi
…
§N KAPANIŞ — duygu · aforizma yönü · CTA · köprü · imza
Orta-video açık döngüsü: nerede açılıyor → nerede cevaplanıyor
Metafor: kapalı §… · açıklayan §… · dönüşmüş §…
Bilgi kazancı yerleşimi: #1 ilk 2 dk §… · #2 orta §… · #3 §…
Güvenlik cümlesi (varsa): §…
Duygusal ark: …
```
Her bölümde en az bir somut gündelik sahne. Numaralı belirti listesi yok. İzleyici dili listesinden 4–6 ifade ilgili
bölüme not edilir.

## Çıktı
1. `{{KOD_ONEKI}}-0X_2_arastirma_outline.md`: A) doğrulama tablosu + iddia sınıflaması · B) izleyici dili · C) rakip
   boşluğu · D) güvenlik · E) outline.
2. Sohbet cevabı: en fazla 5 satır özet · kontrol satırları (`Doğrulanan bilgi N (≥3 ✓) · "Kullanma" iddiası yok ✓ ·
   Açılış tipi tekrar yok ✓ · Metafor 3 görünüş ✓ · Tahmini süre ✓`) · durum kartı `Bekleyen: ONAY 2 | Sonraki: senaryo`.

## Düzeltme turu
Yalnızca değişen outline bölümleri ("§4 yeni hali: …").
````

### `app/sablonlar/kanal/Beceriler/ceviri/SKILL.md`

````markdown
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
````

### `app/sablonlar/kanal/Beceriler/konu/SKILL.md`

````markdown
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
````

### `app/sablonlar/kanal/Beceriler/paketleme/SKILL.md`

````markdown
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
````

### `app/sablonlar/kanal/Beceriler/sahne/SKILL.md`

```markdown
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
```

### `app/sablonlar/kanal/Beceriler/senaryo/SKILL.md`

```markdown
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
```

### `app/sablonlar/kanal/Proje_dosyalari/00_Yonetici.md`

````markdown
# 00 · YÖNETİCİ — {{KANAL_ADI}} üretim düzeni

Bu kanalın her videosu ({{KOD_ONEKI}}-0X) Kanal Stüdyosu'nda altı aşamada üretilir. Her aşama kendi **becerisiyle**
yapılır. Kanalın kuralları `01_Anayasa.md`'de, hafızası `02_Defter.md`'de, üzerinde çalışılan video `03_Aktif_Video.md`'dedir.

## 1. Roller
- **Kullanıcı:** Onay verir, CapCut'ta rötuş yapar, yayınlar.
- **Uygulama (Kanal Stüdyosu):** Mesajları gönderir, dosyaları kaydeder, kod kontrollerini yapar; görselleri Flow ajanına,
  sesi ElevenLabs'e devreder; sahne videolarını ve CapCut taslağını üretir; proje dosyalarını günceller.
- **Model (sen):** Aşama becerilerini çalıştırır, kanal metinlerini yazar. Konu, senaryo, sahneler, montaj planı ve
  paketleme yalnızca burada yazılır.
- Kullanıcıyla iletişim ve çalışma metinleri **Türkçedir**. Videonun dili **{{HEDEF_DIL}}**'dir.

## 2. Aşamalar ve onay noktaları
| # | Beceri | Girdi | Çıktı dosyası | Onay |
|---|---|---|---|---|
| 1 | konu | 02_Defter + önceki videonun Studio verisi (varsa) | `{{KOD_ONEKI}}-0X_1_konu_karti.md` + `{{KOD_ONEKI}}-0X_1_defter_degisiklikleri.md` | ONAY 1 |
| 2 | arastirma | konu kartı | `{{KOD_ONEKI}}-0X_2_arastirma_outline.md` | ONAY 2 |
| 3 | senaryo | onaylı outline | `{{KOD_ONEKI}}-0X_3_senaryo_tr.md` | ONAY 3 |
| 4 | ceviri | onaylı Türkçe senaryo | `{{KOD_ONEKI}}-0X_4_senaryo_{{HEDEF_DIL_KODU}}.md` | ONAY 4 |
| 5 | sahne | 03_Aktif_Video (kart + hedef dil final) | `_5A_elevenlabs.txt` · `_5B_gorsel_promptlari.txt` · `_5C_veo3.md` · `_5D_montaj_plani.tsv` | otomatik kontroller |
| 6 | paketleme | 03_Aktif_Video + (montaj sonrası) bölüm zamanları | `{{KOD_ONEKI}}-0X_6_paket.md` · sonra `{{KOD_ONEKI}}-0X_6_aciklama_final.md` | ONAY 5 |

Onay mesajı "ONAY N" diye başlar, varsa düzeltme notu içerir. Onay gelmeden sonraki aşamaya geçilmez.

## 3. İsraf kuralları (her aşamada)
1. Tam metin bir kez, dosya olarak verilir; sohbette tekrar edilmez.
2. Sohbet cevabı kısadır: en fazla 5 satır özet, kontrol satırları, en sonda durum kartı.
3. Düzeltmelerde yalnızca değişen kısım yazılır.
4. Önceki çıktılar ve proje dosyaları sohbete yeniden yapıştırılmaz; adıyla atıf yapılır.

## 4. Durum kartı (her cevabın sonunda)
```
{{KOD_ONEKI}}-0X · Aşama N/6 · <durum>
Bekleyen: … | Sonraki: …
```
````

### `app/sablonlar/kanal/Proje_dosyalari/01_Anayasa.md`

```markdown
# 01 · KANAL ANAYASASI — {{KANAL_ADI}}
Sürüm 1 · kanal açıldı.

Bu dosya kanalın değişmeyen kurallarıdır. Aşama becerileri bu dosyayı esas alır. Çelişki olursa sıra:
**01_Anayasa > aşama becerisi > eski alışkanlık.** 02_Defter'de (C1) "KALICI DERS" olarak işaretlenmiş bir madde bu
dosyayı günceller.

> Nasıl doldurulur: `⟦DOLDUR: …⟧` ile işaretli yerleri kanalına göre yaz, işareti sil. İşaret kaldıkça uygulama
> "kanal dosyalarında doldurulmamış yer var" uyarısı verir. Diğer maddeler genel iyi uygulamalardır; istersen değiştir.

---

## 1. Kimlik
- **Kanal:** {{KANAL_ADI}} · ⟦DOLDUR: YouTube adresi, slogan⟧
- **Dil:** Bütün yayın çıktıları {{HEDEF_DIL}}. Çalışma notları ve kullanıcıyla iletişim Türkçe.
- **Kitle:** ⟦DOLDUR: kim izliyor (yaş, ülke, hayat durumu), neden izliyor⟧
- **Niş ve damarlar:** ⟦DOLDUR: kanalın konu alanı; 1–3 ana damar ve aralarındaki denge⟧
- **Ton:** ⟦DOLDUR: ör. sıcak, sakin, meraklı, esprili… ve kaçınılan tonlar⟧
- **Hitap:** ⟦DOLDUR: izleyiciye nasıl seslenilir (tekil/çoğul, resmî/samimi; hedef dildeki karşılığı)⟧
- **Konumlandırma:** ⟦DOLDUR: rakiplerden farkı tek cümle⟧
- **Süre:** Hedef süre ve kelime aralıkları uygulamadaki KANAL AYARLARI'ndadır.

## 2. Anlatıcı ve karakter
- **Ses:** ⟦DOLDUR: anlatıcının kimliği, yaşı, tavrı; ne yapar, ne yapmaz⟧ · Seslendirme ElevenLabs ile yapılır (ses
  KANAL AYARLARI'nda).
- **Görsel karakter:** ⟦DOLDUR: varsa Flow karakteri (ör. @Ad) ve görünüşü; yoksa "karakter yok" yaz⟧
- Karakterli promptlar karakter etiketiyle başlar. Görünüşü yeniden tarif edilmez; prompt yalnızca poz, duygu, eylem,
  mekân, nesne ve kamerayı anlatır.

## 3. Görsel kimlik
- **Palet:** ⟦DOLDUR: 3–5 renk (hex)⟧
- **Duygu ışıkla taşınır.** Açılış ve mekanizma: yumuşak, okunaklı. Farkındalık: dengeli. Final: sıcak. Hiçbir sahne
  karanlık ya da okunaksız olmaz.
- **Sahne:** Katmanlı gerçek mekân + ikincil arka plan hareketi + en fazla bir sembolik katman. Görselde yazı ve logo yok.
- **Stil çapası (her KARAKTER/METAFOR promptunun sonuna):** ⟦DOLDUR: İngilizce stil cümlesi, ör. "flat 2D cartoon, clean thin black outlines, …, no text, no letters, no logo, 16:9"⟧
- **Şema çapası (DIAGRAM promptlarının sonuna):** ⟦DOLDUR: İngilizce, karaktersiz ve yazısız şema stili⟧
- **İlk 30 sn ≈ 6 sahne** (4–6 sn). Sonrası 4–10 sn. Sahne kelimeye göre değil görsel beat'e göre bölünür.

## 4. Anlatım metodu
**Başarı zinciri:** ⟦DOLDUR: her videonun izlediği duygusal/mantıksal iskelet; ör. somut sahne → soru → yanlış yorum →
mekanizma → metafor → yeniden çerçeveleme → izin → katılım → sonraki soruya köprü⟧
- **Tek ana metafor:** Üç kez görünür: açılışta kapalı, ortada açıklayan, finalde dönüşmüş. Kullanılmış metaforlar
  tekrar edilmez (02_Defter D).
- **Net bilgi kazancı:** Her videoda izleyicinin "bunu bilmiyordum" diyeceği 3–4 doğru bilgi. Uydurma yok; doğrulanamayan
  bilgi çıkarılır ya da yumuşatılır.
- **Otorite dili, künyesiz:** kesinlik iddiası, dergi adı, araştırmacı adı, yıl ve yüzde yok.
- **Olay-zengin anlatım:** Her soyut fikir bir gündelik sahneye bağlanır.
- **Konu testi:** ⟦DOLDUR: bir konunun seçilmesi için taşıması gereken 3–4 unsur⟧

## 5. Yapı
- **Double hook (0–30 sn):** 0–8 sn somut bir tanıma anı (ilk cümle ≤10 kelime; kapaktaki anın ta kendisi). 8–15 sn
  beklenti kırılması. 15–30 sn dürüst vaat ve açık döngü.
- **4. paragraf = "kal" cümlesi:** izleyiciye ne göreceğini ve neden kalmaya değdiğini söyler; her videoda başka biçimde.
- **Gövde:** ⟦DOLDUR: bölümlerin duygusal ilerleme sırası⟧
- **Orta-video açık döngüsü:** ilk vaadi derinleştirir, sonraki bölümde cevaplanır.
- **Kapanış:** teselli/özet duygu → aforizma → CTA → köprü → imza.
  - **İmza (tek sabit satır, {{HEDEF_DIL}}):** ⟦DOLDUR⟧
  - **CTA türleri:** tanıma sorusu, ikili seçim, sonraki videoya köprü sorusu ya da CTA'sız.
  - **Köprü türleri:** soru, sahne, yorumdan köprü ya da köprüsüz. Son iki videoda kullanılan tür tekrar edilmez.

## 6. Tekrar yasağı (YouTube "tekrarlayan içerik" riski)
- Her video farklı açılış tipi, kal cümlesi kalıbı, köprü tipi ve CTA kalıbı kullanır (02_Defter F).
- Açılış tipleri: (a) soru (b) replik (c) sahne (d) duyusal detay (e) şaşırtıcı bilgi (f) itiraf (g) zıtlık.
- Konu, metafor, hook sahnesi ve kapak yazısı 02_Defter D'de kullanılmamış olmalıdır.

## 7. {{HEDEF_DIL}} doğallık
- Çeviri değil yeniden yazım: her cümle, o dili ana dili olarak konuşan biri konuşurken nasıl söylerse öyle kurulur.
- ⟦DOLDUR: hedef dile özgü kurallar; kaçınılacak çeviri kokulu kalıplar, hitap çekimi, kültürel uyarlamalar⟧

## 8. Güvenlik ve kaynak disiplini
- Teşhis konmaz; sağlık, hukuk ve finans konularında kesin tavsiye verilmez.
- Hassas bağlamlar (ör. çocuk, ekonomik bağımlılık, güvenlik) yok sayılmaz; bir cümlelik baskısız çerçeve verilir.
- ⟦DOLDUR: kanala özgü hassas konular ve nasıl ele alınacağı⟧

## 9. Paketleme
- **Başlık:** ≤60 karakter; ilk ~40 karakterde asıl konu ya da kanca. ⟦DOLDUR: başlık kalıp menüsü (K1–K6 gibi)⟧
- **Kapak:** ⟦DOLDUR: sabit kapak stili (zemin, yazı tipi, renkler, karakter yerleşimi)⟧ · A/B kapaklar aynı anda yalnız
  bir hipotezi test eder (02_Defter C2).
- **Vitrin kelimeleri:** ⟦DOLDUR: başlık/kapak/açıklama/hashtag'de kullanılmayacak hassas ya da klinik kelimeler⟧

## 10. Sabit metinler (aynen kullanılır, {{HEDEF_DIL}})
- **Abone satırı:** ⟦DOLDUR⟧
- **Kimlik cümlesi:** ⟦DOLDUR⟧
- **Yasal uyarı:** ⟦DOLDUR⟧

## 11. Kesin yasaklar
⟦DOLDUR: kanalda asla yapılmayacaklar⟧

## 12. Metafor bankası (yön listesi)
⟦DOLDUR: kanalın dünyasına uyan 10–20 metafor nesnesi; kullanılanlar 02_Defter D'ye yazılır⟧

## 13. Konu ve format kaynağı
⟦DOLDUR: konu fikirleri hangi kanallardan/kaynaklardan alınır, format hangi kanallardan; rakip başlık ve metni çevrilmez⟧
```

### `app/sablonlar/kanal/Proje_dosyalari/02_Defter.md`

```markdown
# 02 · KANAL DEFTERİ — {{KANAL_ADI}}
Sürüm 1 · kanal açıldı.
Uygulama bu dosyayı her video sonrası yenisiyle değiştirir. Değişiklik önerileri 1. aşamadan (`defter_degisiklikleri`)
ve 6. aşamadan (`DEFTER KAYDI`) gelir.

---

## A. YAPILAN VİDEOLAR

| Kod | Nihai başlık | Kapak yazısı (A / B) | Ana metafor | Süre / sahne | Motor | Durum |
|---|---|---|---|---|---|---|

## B. PERFORMANS KAYDI (YouTube Studio)

| Kod | Veri | Teşhis / ders |
|---|---|---|

## C. DERSLER VE HİPOTEZLER
### C1. Kalıcı dersler
Kalıcı ders yalnızca tekrar/kalite kurallarından ya da en az 3 videonun veya net bir Test & compare sonucunun desteğiyle çıkar.

### C2. Deney hipotezleri (kural değil)
| # | Hipotez | Kaynak | Test planı | Durum |
|---|---|---|---|---|

## D. KULLANILMIŞLAR (tekrar yok)
- **Metaforlar:**
- **Kapak yazıları (son 6 video kontrol edilir):**
- **Hook sahneleri:**
- **Bilgi kazançları:**

## E. VERİLEN SÖZLER VE SIRADAKİLER
- **Portföy durumu:**

## F. AÇILIŞ–KAPANIŞ KAYDI
Yeni video bu açılışlara ve kapanışlara benzemez.

| Kod | Açılış tipi | İlk cümle | Kal cümlesi | Köprü tipi | CTA kalıbı |
|---|---|---|---|---|---|

## G. FİKİR HAVUZU

## H. ARAŞTIRMA NOTLARI
```

### `app/sablonlar/kanal/Proje_dosyalari/03_Aktif_Video.md`

```markdown
# 03 · AKTİF VİDEO — {{KANAL_ADI}}
Durum: henüz üretimde video yok.

Uygulama bu dosyayı kendisi doldurur: ONAY 1'den sonra konu kartı, ONAY 4'ten sonra {{HEDEF_DIL}} final metin eklenir.
```

### `app/araclar/acilis_kapanis_defteri.py`

```python
# Kullanim: python3 acilis_kapanis_defteri.py
# Kanalin tum Videolar/<KOD>/02 metinlerinden ACILIS-KAPANIS DEFTERI uretir -> <kanal>/Acilis_Kapanis_Defteri.md
# Kalip sayaclari (kalip_sayaclari: {"etiket": "regex"}) ve imza kanal ayarindan gelir.
import re,glob,os
from ortak import AYAR, KANAL, ONEK, TAG
out=f'{KANAL}/Acilis_Kapanis_Defteri.md'
clean=lambda s:TAG.sub('',s).strip()
KALIP=AYAR.get('kalip_sayaclari',{}) or {}
desen=re.compile(rf'^{re.escape(ONEK)}-\d+$')
kod_=lambda f: os.path.basename(os.path.dirname(f))  # Windows'ta yol ayracı \\ olabilir
V=sorted(f for f in glob.glob(f'{KANAL}/Videolar/*/02_ElevenLabs_seslendirme_metni.txt') if desen.match(kod_(f)))
imza=AYAR.get('imza','')
L=[f'# {AYAR.get("ad","")} — Açılış–Kapanış Defteri','', 'Otomatik üretilir (Kanal Stüdyosu). Her videodan sonra yenilenir.',
'Kural: yeni video bu açılışlara ve kapanışlara BENZEMEZ.'+(f' Tek sabit satır imzadır: *"{imza}"*' if imza else ''),'']
say={k:[] for k in KALIP}
for f in V:
    kod=kod_(f); P=[clean(x) for x in re.split(r'\n\s*\n',open(f,encoding='utf-8').read().strip()) if x.strip()]
    L+= [f'## {kod} ({len(P)} paragraf)','','**Açılış (ilk 4 paragraf):**','']+[f'{i+1}. {p}' for i,p in enumerate(P[:4])]
    L+= ['','**Kapanış (son 3 paragraf):**','']+[f'- {p}' for p in P[-3:]]+['']
    t=' '.join(P)
    for k,r in KALIP.items(): say[k].append((kod,len(re.findall(r,t,re.I))))
if KALIP and V:
    L+=['## Tekrar eden kalıplar (video başına adet)','','| Kalıp | '+' | '.join(kod_(x) for x in V)+' |','|---|'+'---|'*len(V)]
    for k,v in say.items(): L.append(f'| {k} | '+' | '.join(str(c) for _,c in v)+' |')
open(out,'w',encoding='utf-8').write('\n'.join(L)+'\n'); print('yazildi',out,len(V),'video')
```

### `app/araclar/capcut_efekt_verisi.json`

```json
{
 "Vignette": {
  "effect_id": "7399463239379209477",
  "resource_id": "7399463239379209477",
  "path": "/Users/kullanici/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect/7399463239379209477/ef7abad9671e2f3da7993b7673ece5fc",
  "category_id": "1111",
  "category_name": "Video effects",
  "source_platform": 1
 },
 "Vintage Grain": {
  "effect_id": "7621305507021737269",
  "resource_id": "7621305507021737269",
  "path": "/Users/kullanici/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect/7621305507021737269/7baf0fcf22c10ff4b07a541a88c2d938",
  "category_id": "1111",
  "category_name": "Video effects",
  "source_platform": 1
 },
 "Dreamy Light": {
  "effect_id": "7615889883109838098",
  "resource_id": "7615889883109838098",
  "path": "/Users/kullanici/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect/7615889883109838098/561c4abb16e674000e6c28799b783096",
  "category_id": "1111",
  "category_name": "Video effects",
  "source_platform": 1
 }
}
```

### `app/araclar/capcut_taslak.py`

```python
# Sahne videoları + montaj planı + odak + SRT  ->  hazır CapCut taslağı
# (hareket/Ken Burns, geçişler, sahne efektleri, kanal stili altyazı: yazı tipi/renk/kutu kanal ayarından).
# İlk sürümün CapCut betiğinden taşındı; iskelet bu klasördedir.
# Kullanım:
#   python3 capcut_taslak.py --video "<.../Uretim/<kod>-...>" --plan 05_Montaj_plani.tsv \
#       --odak odak.json --srt <KOD>_altyazi_<dil>.srt --ad "<KOD>" [--kuru <klasör>]
import json, uuid, copy, os, shutil, sys, time, csv, glob, subprocess, argparse
from ortak import AYAR, CAPCUT, FPS, capcut_kullanici_verisi, win_yolu
ap = argparse.ArgumentParser()
for a in ('--video', '--plan', '--odak', '--srt', '--ad'): ap.add_argument(a, required=True)
ap.add_argument('--kuru', help='CapCut klasörüne yazmadan, bu klasöre üret (deneme)')
A = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = CAPCUT
MAC_ROOT = win_yolu(CAPCUT)  # CapCut'ın kendi kaydına yazılan gerçek yol (Windows'ta C:/Users/... biçiminde)
U = lambda: str(uuid.uuid4()).upper()
TR = {'KARISIM': ('叠化', '6724845717472416269', 600000), 'KARARMA': ('闪黑', '6724239388189921806', 800000),
      'ANI_GIRIS': ('回忆', '6748220149284737550', 800000), 'ANI_CIKIS': ('转场-模糊', '6916426617455645186', 600000),
      'SAYFA': ('翻页', '6747979085894390279', 700000), 'ICERI': ('推近', '6724226861666144779', 500000)}
# EFEKTLER: yalnızca CapCut Global (İngilizce) kimlikleri. Çince/Jianying kimlikleri CapCut Global'de
# çözülmez ve klipte kırmızı hata simgesi çıkar (ilk videolarda yaşandı). Kimlik/yol capcut_efekt_verisi.json'dan gelir;
# yeni efekt gerekirse CapCut'ta bir kez elle ekle, taslaktan verisini bu dosyaya kaydet.
# Efekt ve yazı tipi önbellek yolları şablonun kaydedildiği Mac'in ev klasörüyle yazılı: bu Mac'inkiyle değiştirilir.
_EV_ESKI = '/Users/kullanici'
_MAC_VERI = _EV_ESKI + '/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data'
# Windows: şablondaki Mac CapCut önbellek yolları (efekt, yazı tipi) bu bilgisayarın CapCut\User Data klasörüne çevrilir.
def _ev(t): return t.replace(_MAC_VERI, capcut_kullanici_verisi()).replace(_EV_ESKI, win_yolu(os.path.expanduser('~')))
_EV = json.loads(_ev(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capcut_efekt_verisi.json'), encoding='utf-8').read()))
FX = {'ESKI_FOTO': ('Vintage Grain', [('effects_adjust_speed', 0.0, 1.0, 0.33333333333333), ('effects_adjust_background_animation', 0.0, 1.0, 0.35)]),
      'VINYET': ('Vignette', [('effects_adjust_texture', 0.0, 1.0, 0.45)]),
      'YUMUSAK_ISIK': ('Dreamy Light', [('effects_adjust_intensity', 0.0, 1.0, 0.3)])}
assert all(not any('\u4e00' <= ch <= '\u9fff' for ch in v[0]) and v[0] in _EV for v in FX.values()), 'Efekt adı Global CapCut verisinde yok / Çince'
dur = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
vids = sorted(glob.glob(os.path.join(A.video, 'scene-videos', 'sahne*.mp4')))
plan = {r['sahne']: r for r in csv.DictReader(open(A.plan, encoding='utf-8'), delimiter='\t') if r.get('sahne')}
odak = json.load(open(A.odak))
assert len(vids) == len(plan), f'video {len(vids)} != plan {len(plan)}'
dst = os.path.join(A.kuru or ROOT, A.ad); assert not os.path.exists(dst), 'hedef zaten var: ' + dst
shutil.copytree(os.path.join(HERE, 'capcut_iskelet'), dst)
os.makedirs(os.path.join(dst, 'media'), exist_ok=True)
d = json.load(open(os.path.join(dst, 'draft_info.json'))); tid = d['id']
vt = [t for t in d['tracks'] if t['type'] == 'video'][0]; seg0 = vt['segments'][0]
mats = d['materials']; vm0 = [m for m in mats['videos'] if m['id'] == seg0['material_id']][0]
ph = vm0['path'].split('/media/')[0]
aux0 = {}  # yardımcı malzemeler (hız, tuval, ...)
for k, v in mats.items():
    if isinstance(v, list):
        for x in v:
            if isinstance(x, dict) and x.get('id') in seg0['extra_material_refs']: aux0[k] = x
for k in list(mats.keys()):
    if isinstance(mats[k], list): mats[k] = []
segs = []; t = 0
for i, v in enumerate(vids):
    name = os.path.basename(v); shutil.copy(v, os.path.join(dst, 'media', name))
    nf = int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_packets','-show_entries','stream=nb_read_packets','-of','csv=p=0',v]).decode().strip().strip(','))
    du = nf * 1_000_000 // FPS   # video kare sayısına göre
    vm = copy.deepcopy(vm0); vm.update(id=U(), duration=du, path=f'{ph}/media/{name}', material_name=name); mats['videos'].append(vm)
    s = copy.deepcopy(seg0); s.update(id=U(), material_id=vm['id'], extra_material_refs=[], common_keyframes=[])
    s['source_timerange'] = {'start': 0, 'duration': du}; s['target_timerange'] = {'start': t, 'duration': du}
    for k, x in aux0.items():
        y = copy.deepcopy(x); y['id'] = U(); mats[k].append(y); s['extra_material_refs'].append(y['id'])
    segs.append(s); t += du
vt['segments'] = segs; d['tracks'] = [vt]; d['duration'] = t
clamp = lambda v, a, b: max(a, min(b, v))
def kfl(prop, pts):
    return {"id": U(), "keyframe_list": [{"curveType": "Line", "graphID": "", "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "id": U(), "time_offset": tt, "values": [vv]} for tt, vv in pts], "material_id": "", "property_type": prop}
stats = {}
for i, s in enumerate(segs):
    n = f'{i+1:04d}'; p = plan[n]; D = s['target_timerange']['duration']; sec = D / 1e6
    fx_, fy_ = odak.get(n, [0.5, 0.5]); u, v = 2*fx_ - 1, 1 - 2*fy_
    mv = p['hareket'].strip().upper(); stats[mv] = stats.get(mv, 0) + 1
    z = clamp(0.03 + 0.004*sec, 0.04, 0.12); zp = clamp(0.05 + 0.003*sec, 0.06, 0.12)
    if mv in ('YAKINLAS', 'UZAKLAS', 'NEFES'):
        zz = 0.02 if mv == 'NEFES' else z
        s0, s1 = (1+zz, 1.0) if mv == 'UZAKLAS' else (1.0, 1+zz)
        k = [kfl('KFTypeScaleX', [(0, s0), (D, s1)]), kfl('KFTypePositionX', [(0, u*(1-s0)), (D, u*(1-s1))]), kfl('KFTypePositionY', [(0, v*(1-s0)), (D, v*(1-s1))])]
    elif mv in ('SAGA', 'SOLA', 'ASAGI', 'YUKARI'):
        sc = 1 + zp; a = zp*0.85; ty = clamp(v*(1-sc), -zp, zp); tx = clamp(u*(1-sc), -zp, zp)
        if mv in ('SAGA', 'SOLA'):
            x0, x1 = (a, -a) if mv == 'SAGA' else (-a, a)
            k = [kfl('KFTypeScaleX', [(0, sc), (D, sc)]), kfl('KFTypePositionX', [(0, x0), (D, x1)]), kfl('KFTypePositionY', [(0, ty), (D, ty)])]
        else:
            y0, y1 = (-a, a) if mv == 'ASAGI' else (a, -a)
            k = [kfl('KFTypeScaleX', [(0, sc), (D, sc)]), kfl('KFTypePositionX', [(0, tx), (D, tx)]), kfl('KFTypePositionY', [(0, y0), (D, y1)])]
    else: k = []
    s['uniform_scale'] = {"on": True, "value": 1.0}; s['common_keyframes'] = k
    ef = p['efekt'].strip().upper()
    if ef in FX:
        nm, prm = FX[ef]; ev = _EV[nm]; eid = ev['effect_id']
        m = {"adjust_params": [{"default_value": dv, "max_value": mx, "min_value": mn, "name": pn, "parameterIndex": j, "portIndex": 0, "value": dv} for j, (pn, mn, mx, dv) in enumerate(prm)],
             "apply_target_type": 0, "apply_time_range": None, "category_id": ev["category_id"], "category_name": ev["category_name"], "path": ev["path"], "common_keyframes": [], "disable_effect_faces": [],
             "effect_id": eid, "formula_id": "", "id": U(), "name": nm, "platform": "all", "render_index": 11000, "resource_id": ev["resource_id"],
             "source_platform": ev["source_platform"], "time_range": None, "track_render_index": 0, "type": "video_effect", "value": 1.0, "version": ""}
        mats.setdefault('video_effects', []).append(m); s['extra_material_refs'].append(m['id']); stats['efekt:'+ef] = stats.get('efekt:'+ef, 0) + 1
    g = p['sonraki_gecis'].strip().upper(); stats['gecis:'+g] = stats.get('gecis:'+g, 0) + 1
    if g in TR and i < len(segs) - 1:
        nm, eid, td = TR[g]; td = min(td, int(D*0.4), int(segs[i+1]['target_timerange']['duration']*0.4))
        tr = {"category_id": "", "category_name": "", "duration": td, "effect_id": eid, "id": U(), "is_overlap": True, "name": nm, "platform": "all", "resource_id": eid, "type": "transition"}
        mats.setdefault('transitions', []).append(tr); s['extra_material_refs'].append(tr['id'])
# altyazı (normal metin; Pro istemez) — kanal stili şablondan
S = json.loads(_ev(open(os.path.join(HERE, 'sablon_altyazi.json'), encoding='utf-8').read()))
_AY = AYAR.get('montaj', {}).get('altyazi', {})
def _rgb(h): return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
if _AY:  # kanal stili: yazı rengi, kutu rengi/opaklığı, boyut, yazı tipi
    _m = S['material']; _c = json.loads(_m['content']); _st = _c['styles'][0]
    _m['text_color'] = _AY.get('yazi', _m['text_color']); _st['fill']['content']['solid']['color'] = _rgb(_m['text_color'])
    _m['background_color'] = _AY.get('kutu', _m['background_color']); _m['background_alpha'] = float(_AY.get('kutu_opaklik', _m['background_alpha']))
    _m['font_size'] = _st['size'] = float(_AY.get('boyut', _m['font_size']))
    if _AY.get('yazi_tipi') and _AY['yazi_tipi'] != _m['font_name']:  # CapCut kaynak kimliği yalnız şablondaki yazı tipi için bilinir
        _m['font_name'] = _m['font_title'] = _AY['yazi_tipi']; _m['font_resource_id'] = ''; _st['font'] = {'id': '', 'path': ''}
    _m['content'] = json.dumps(_c, ensure_ascii=False)
def t2us(x):
    h, m_, r = x.split(':'); s_, ms = r.split(','); return ((int(h)*60+int(m_))*60+int(s_))*1_000_000+int(ms)*1000
tsegs = []
for blk in open(A.srt, encoding='utf-8').read().strip().split('\n\n'):
    L = blk.split('\n'); a, b = L[1].split(' --> '); st, en = t2us(a), min(t2us(b), t); txt = '\n'.join(L[2:])
    if en - st < 100000: continue
    m = copy.deepcopy(S['material']); m['id'] = U(); c = json.loads(m['content']); c['text'] = txt; c['styles'][0]['range'] = [0, len(txt)]
    m['content'] = json.dumps(c, ensure_ascii=False)
    an = copy.deepcopy(S['animation']); an['id'] = U()
    sg = copy.deepcopy(S['segment']); sg.update(id=U(), material_id=m['id'], extra_material_refs=[an['id']]); sg['target_timerange'] = {"start": st, "duration": en - st}
    mats.setdefault('texts', []).append(m); mats.setdefault('material_animations', []).append(an); tsegs.append(sg)
tt = copy.deepcopy(S['track']); tt['id'] = U(); tt['segments'] = tsegs; d['tracks'].append(tt)
out = json.dumps(d, ensure_ascii=False)
for f in ['draft_info.json', 'draft_info.json.bak', 'template-2.tmp', f'Timelines/{tid}/draft_info.json', f'Timelines/{tid}/draft_info.json.bak', f'Timelines/{tid}/template-2.tmp']:
    pth = os.path.join(dst, f)
    if os.path.exists(pth): open(pth, 'w', encoding='utf-8').write(out)
# Windows CapCut'ı için aynı içerik draft_content.json adıyla da yazılır (kök ve Timelines/<id>, .bak'larıyla).
for f in ['draft_content.json', 'draft_content.json.bak', f'Timelines/{tid}/draft_content.json', f'Timelines/{tid}/draft_content.json.bak']:
    if os.path.isdir(os.path.dirname(os.path.join(dst, f)) or dst): open(os.path.join(dst, f), 'w', encoding='utf-8').write(out)
# kapak, meta, kayıt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.5', '-i', vids[0], '-frames:v', '1', os.path.join(dst, 'draft_cover.jpg')])
for c_ in glob.glob(os.path.join(dst, 'Timelines', tid, 'draft_cover.jpg')): shutil.copy(os.path.join(dst, 'draft_cover.jpg'), c_)
new_id = U(); now = int(time.time()*1_000_000)
mp = os.path.join(dst, 'draft_meta_info.json'); meta = json.load(open(mp))
dm = [x for x in meta['draft_materials'] if x['type'] == 0][0]; it0 = dm['value'][0]; dm['value'] = []
for v, vm in zip(vids, mats['videos']):
    it = copy.deepcopy(it0); nm = os.path.basename(v)
    it.update(id=str(uuid.uuid4()), duration=vm['duration'], extra_info=nm, file_Path=f'./media/{nm}', create_time=int(time.time()), import_time=int(time.time()), import_time_ms=now)
    it['roughcut_time_range'] = {"duration": vm['duration'], "start": 0}; dm['value'].append(it)
meta.update(draft_id=new_id, draft_name=A.ad, draft_fold_path=f'{MAC_ROOT}/{A.ad}', draft_root_path=MAC_ROOT, tm_duration=t, tm_draft_create=now, tm_draft_modified=now,
            draft_timeline_materials_size_=sum(os.path.getsize(v) for v in vids))
json.dump(meta, open(mp, 'w'), ensure_ascii=False)
pj = os.path.join(dst, 'Timelines/project.json'); pr = json.load(open(pj)); pr['id'] = U(); json.dump(pr, open(pj, 'w'))
if not A.kuru:
    rp = os.path.join(ROOT, 'root_meta_info.json'); shutil.copy(rp, rp + '.claude-yedek')   # tek yedek, her seferinde yenilenir
    r = json.load(open(rp)); e = copy.deepcopy(r['all_draft_store'][0])
    old = e['draft_name']
    for kk, vv in list(e.items()):
        if isinstance(vv, str) and old and old in vv: e[kk] = vv.replace(old, A.ad)
    e.update(draft_id=new_id, draft_name=A.ad, draft_fold_path=f'{MAC_ROOT}/{A.ad}', draft_json_file=f'{MAC_ROOT}/{A.ad}/draft_content.json',
             draft_cover=f'{MAC_ROOT}/{A.ad}/draft_cover.jpg', draft_root_path=MAC_ROOT, tm_duration=t, tm_draft_create=now, tm_draft_modified=now)
    r['all_draft_store'].insert(0, e)
    if isinstance(r.get('draft_ids'), int): r['draft_ids'] += 1
    json.dump(r, open(rp, 'w'), ensure_ascii=False)
print('ok', A.ad, f'{t/1e6:.1f} sn', 'sahne', len(segs), 'altyazi', len(tsegs)); print(json.dumps(stats, ensure_ascii=False))
```

### `app/araclar/hassas_kelime_kontrol.py`

```python
# Kullanim: python3 hassas_kelime_kontrol.py <KOD>   (ör. BK-04; eski kullanim: 04)
# Paketleme (04_Paketleme_ve_Veo3.md: baslik, kapak yazisi, aciklama, etiketler) ve metnin ilk 30 sn'sinde (ilk 6 paragraf)
# kanal ayarindaki hassas/klinik kelimeleri (hassas_kelimeler; kok yazilabilir) arar. Liste bossa TEMIZ.
import re,sys,os
from ortak import AYAR, kod_al, video
kod=kod_al(sys.argv[1]); D=video(kod)
L=[k.strip() for k in AYAR.get('hassas_kelimeler',[]) if k.strip()]
K='|'.join(L)
bul=[]
if K:
    pk=open(f'{D}/04_Paketleme_ve_Veo3.md',encoding='utf-8').read().split('\n')
    kes=next((i for i,l in enumerate(pk) if re.search(r'Veo3|VEO3|Veo 3',l) and l.startswith('#') and i>5),len(pk))
    for i,l in enumerate(pk[:kes]):
        if re.search(K,l,re.I) and not l.strip().startswith('>'): bul.append(f'paketleme satir {i+1}: {l.strip()[:140]}')
    P=[x.strip() for x in re.split(r'\n\s*\n',open(f'{D}/02_ElevenLabs_seslendirme_metni.txt',encoding='utf-8').read().strip()) if x.strip()]
    for i,p in enumerate(P[:6]):
        if re.search(K,p,re.I): bul.append(f'metin ilk 30 sn, paragraf {i+1}: {p[:140]}')
print(f'{kod} hassas kelime: '+('TEMIZ' if not bul else f'{len(bul)} bulgu')); print('\n'.join(bul))
```

### `app/araclar/maskot_gom.py`

```python
#!/usr/bin/env python3
"""Sahne videosuna CapCut hareketini (olcek/konum anahtar kareleri) ve maskotu gomer.
Kullanim: maskot_gom.py sahne.mp4 maskot_seffaf.mov cikis.mp4 --basla 1.0 --kf "t0,s0,x0,y0;t1,s1,x1,y1"
kf: CapCut degerleri (olcek, konum x/y yarim-tuval birimi, y yukari +). Sonuc tasta hareketsiz kullanilir."""
import sys, subprocess, argparse
from PIL import Image
p=argparse.ArgumentParser(); p.add_argument('sahne'); p.add_argument('maskot'); p.add_argument('cikis')
p.add_argument('--basla',type=float,default=1.0); p.add_argument('--kf',required=True)
p.add_argument('--olcek',type=float,default=0.42); p.add_argument('--mx',type=float,default=-0.836); p.add_argument('--my',type=float,default=-0.58)
p.add_argument('--fade',type=float,default=0.3)
a=p.parse_args()
W,H,F=1920,1080,30
kf=[tuple(map(float,x.split(','))) for x in a.kf.split(';')]
def lerp(t,i):
    if t<=kf[0][0]: return kf[0][i]
    if t>=kf[-1][0]: return kf[-1][i]
    for (t0,*v0),(t1,*v1) in zip(kf,kf[1:]):
        if t0<=t<=t1: r=(t-t0)/(t1-t0); return v0[i-1]+(v1[i-1]-v0[i-1])*r
# maskot kareleri
mw,mh=720,1280
raw=subprocess.run(['ffmpeg','-v','error','-i',a.maskot,'-f','rawvideo','-pix_fmt','rgba','-'],capture_output=True).stdout
n=len(raw)//(mw*mh*4); mfps=24.0; mdur=n/mfps
th=H*a.olcek; tw=th*mw/mh; cx=W/2+a.mx*W/2; cy=H/2-a.my*H/2
mk=[Image.frombytes('RGBA',(mw,mh),raw[i*mw*mh*4:(i+1)*mw*mh*4]).resize((round(tw),round(th)),Image.LANCZOS) for i in range(n)]
ox,oy=round(cx-tw/2),round(cy-th/2)
dec=subprocess.Popen(['ffmpeg','-v','error','-i',a.sahne,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(F),'-i','-','-i',a.sahne,'-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-shortest',a.cikis],stdin=subprocess.PIPE)
fb=W*H*3; k=0
while True:
    b=dec.stdout.read(fb)
    if len(b)<fb: break
    t=k/F; im=Image.frombytes('RGB',(W,H),b)
    s=lerp(t,1); tx=lerp(t,2)*W/2; ty=-lerp(t,3)*H/2
    c=W/2; d=H/2
    # cikis=S*(giris-merkez)+merkez+T  => giris=(cikis-merkez-T)/S+merkez
    im=im.transform((W,H),Image.AFFINE,(1/s,0,c-(c+tx)/s,0,1/s,d-(d+ty)/s),resample=Image.BICUBIC)
    mt=t-a.basla
    if 0<=mt<mdur:
        m=mk[min(int(mt*mfps),n-1)]
        al=min(1,mt/a.fade,(mdur-mt)/a.fade)
        if al<1:
            r,g,bb,aa=m.split(); aa=aa.point(lambda v:int(v*al)); m=Image.merge('RGBA',(r,g,bb,aa))
        im.paste(m,(ox,oy),m)
    enc.stdin.write(im.tobytes()); k+=1
enc.stdin.close(); enc.wait(); print('kare',k)
```

### `app/araclar/maskot_seffaf.py`

```python
#!/usr/bin/env python3
"""Yesil ekranli maskot videosunu seffaf ProRes 4444 .mov yapar (elle kullanilan arac).
Kullanim: maskot_seffaf.py giris.mp4 cikis.mov [0xRRGGBB]   (Mac surumundeki maskot_seffaf.sh'in karsiligi)"""
import subprocess, sys
giris, cikis = sys.argv[1], sys.argv[2]
C = sys.argv[3] if len(sys.argv) > 3 else '0x22E421'
fc = (f"[0]format=gbrap,chromakey={C}:0.14:0.04,split=3[k][m][s];[m]alphaextract,erosion,erosion,boxblur=1:1[al];"
      "[k][al]alphamerge,split[ke][ko];[ke]despill=type=green:mix=0.5:expand=0,format=gbrap[d];"
      "[s]alphaextract,erosion,erosion,erosion,erosion,erosion,erosion,format=gray,scale=flags=neighbor,format=gbrap[mask0];"
      "[ko]format=gbrap[o];[d][o][mask0]maskedmerge=planes=7,format=yuva444p10le")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', giris, '-an', '-filter_complex', fc, '-c:v', 'prores_ks', '-profile:v', '4444',
                '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0', cikis], check=True)
```

### `app/araclar/muzik_otomatik.py`

```python
#!/usr/bin/env python3
"""Kanalin Varliklar/Muzik klasorunden RASTGELE ve BIRBIRINDEN FARKLI parcalari, videonun tamamini dolduracak
kadar secip muzik yatagi uretir (22 Eki 2026; onceki surum yalniz 2 parca seciyordu).
 - Parcalar arka arkaya, kendi uzunluklarinca calar; gecislerde 3 sn capraz gecis (muzik_yatagi.py).
 - Ayni parca ancak klasordeki butun parcalar kullanildiktan sonra tekrar eder (art arda ayni parca gelmez).
 - Son parca videonun sonunda kesilir ve kisilarak biter; son ekranda muzik hafifce yukselir.
Kullanim: muzik_otomatik.py <KOD> [--cikis dosya.m4a] [--tohum 7] [--son-sn 8] [--ekle]
 Varsayilan cikis: CapCut taslaginin media/muzik_<KOD>.m4a dosyasi. Seviye kanal ayarindan (montaj.muzik_lufs). Secilen parcalari yazdirir.
 --ekle: yayin_hazirla.py'si zaten calismis (son ekranli) bir taslaga muzigi ekler ya da eski muzik kanalini
         yenisiyle degistirir (CapCut KAPALI olmali; kok + Timelines + .bak birlikte yazilir, eski hali Arsiv'e)."""
import argparse, json, os, random, subprocess, shutil, tempfile
from ortak import AYAR, ARACLAR, PY, kod_al, taslak, arsiv, muzik_parcalari, muzik_olc, taslak_oku, taslak_yolu, taslak_yaz
GECIS = 3.0
p = argparse.ArgumentParser(); p.add_argument('x'); p.add_argument('--cikis'); p.add_argument('--tohum', type=int)
p.add_argument('--son-sn', type=float, default=8.0); p.add_argument('--ekle', action='store_true')
a = p.parse_args()
KOD = kod_al(a.x); DR = taslak(KOD)
cikis = a.cikis or f'{DR}/media/muzik_{KOD}.m4a'

d = taslak_oku(DR)
V = [t for t in d['tracks'] if t['type'] == 'video'][0]['segments']
basl = [s['target_timerange']['start'] / 1e6 for s in V]
# anlatim sonu: son ekran zaten eklenmisse onu anlatima sayma
ses_sonu = d['duration'] / 1e6
mats = {m['id']: m for m in d['materials']['videos']}
if V and mats.get(V[-1]['material_id'], {}).get('path', '').endswith('_son.mp4'):
    ses_sonu = basl[-1]; basl = basl[:-1]
toplam = ses_sonu + a.son_sn
if a.ekle: toplam = d['duration'] / 1e6

parcalar = muzik_parcalari()
assert len(parcalar) >= 1, 'Varliklar/Muzik klasorunde parca yok'
rnd = random.Random(a.tohum)
uzunluk = {}


def kullanilir(f):
    if f not in uzunluk:
        _, b, e = muzik_olc(f)
        uzunluk[f] = e - b
    return uzunluk[f]


def sira():
    """Karisik sira; bitince yeniden karistirilir, art arda ayni parca gelmez."""
    onceki = None
    while True:
        k = parcalar[:]
        rnd.shuffle(k)
        if len(k) > 1 and k[0] == onceki:
            k.append(k.pop(0))
        for f in k:
            onceki = f
            yield f


seg, t, atlanan = [], 0.0, 0
for f in sira():
    pay = max(kullanilir(f) - GECIS - 0.5, 1.0)  # parcanin kendi uzunlugu (gecis payi dusulur)
    if pay < 10 and seg and atlanan < len(parcalar):  # cok kisa parca (ses efekti gibi) dolgu olarak kullanilmaz
        atlanan += 1
        continue
    atlanan = 0
    if t + max(pay, 10) >= toplam or len(seg) > 60:
        seg.append((f, t, toplam))
        break
    seg.append((f, t, t + pay))
    t += pay
dk = lambda x: f'{int(x // 60)}:{int(x % 60):02d}'
print('secilen: ' + ' · '.join(f'{i}) {os.path.basename(f)} ({dk(b)}-{dk(e)})' for i, (f, b, e) in enumerate(seg, 1)))

tmpd = tempfile.mkdtemp(); gecici = os.path.join(tmpd, 'muzik.m4a')
subprocess.run([PY, f'{ARACLAR}/muzik_yatagi.py', gecici, '--toplam', f'{toplam:.2f}', '--son', f'{ses_sonu:.2f}',
                '--hedef', str(AYAR.get('montaj', {}).get('muzik_lufs', -38)),
                *[x for f, b, e in seg for x in ('--parca', f'{f}@{b:.2f}-{e:.2f}')]], check=True)
if os.path.exists(cikis):  # ustune yazmadan once yedek
    os.makedirs(arsiv(KOD), exist_ok=True); shutil.copy(cikis, f'{arsiv(KOD)}/eski_' + os.path.basename(cikis))
shutil.move(gecici, cikis); shutil.rmtree(tmpd, ignore_errors=True)
print('tamam', cikis, f'toplam {toplam:.1f} sn')

if a.ekle:
    import uuid, glob
    U = lambda: str(uuid.uuid4()).upper()
    M = d['materials']
    PH = [m['path'] for m in M['videos'] if '/media/' in m['path']][0].rsplit('/media/', 1)[0] + '/media/'
    eski = [t for t in d['tracks'] if t['type'] == 'audio' and t.get('name') == 'muzik']
    for t in eski:
        ids = {sg['material_id'] for sg in t['segments']}; M['audios'] = [m for m in M['audios'] if m['id'] not in ids]
    d['tracks'] = [t for t in d['tracks'] if t not in eski]
    md = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', cikis], capture_output=True, text=True).stdout)
    aid = U(); sid = U(); spid = U(); AD = min(int(md * 1e6) - 1000, d['duration'])
    M['audios'].append({"app_id": 0, "category_id": "", "category_name": "local", "check_flag": 3, "copyright_limit_type": "none", "duration": int(md * 1e6), "effect_id": "", "formula_id": "", "id": aid, "local_material_id": aid, "music_id": aid, "name": os.path.basename(cikis), "path": PH + os.path.basename(cikis), "source_platform": 0, "type": "extract_music", "wave_points": []})
    M.setdefault('speeds', []).append({"curve_speed": None, "id": spid, "mode": 0, "speed": 1.0, "type": "speed"})
    seg = {"enable_adjust": True, "enable_color_correct_adjust": False, "enable_color_curves": True, "enable_color_match_adjust": False, "enable_color_wheels": True, "enable_lut": True, "enable_smart_color_adjust": False, "last_nonzero_volume": 1.0, "reverse": False, "track_attribute": 0, "track_render_index": 0, "visible": True, "id": sid, "material_id": aid, "target_timerange": {"start": 0, "duration": AD}, "common_keyframes": [], "keyframe_refs": [], "source_timerange": {"start": 0, "duration": AD}, "speed": 1.0, "volume": 1.0, "extra_material_refs": [spid], "clip": None, "hdr_settings": None, "render_index": 0}
    d['tracks'].append({"attribute": 0, "flag": 0, "id": U(), "is_default_name": False, "name": "muzik", "type": "audio", "segments": [seg]})
    X = arsiv(KOD); os.makedirs(X, exist_ok=True)
    shutil.copy(taslak_yolu(DR), f'{X}/draft_info_muzik_oncesi.json')
    taslak_yaz(DR, d)  # draft_info.json ve draft_content.json, kök + Timelines, .bak'larıyla
    print('taslaga eklendi:', 'eski muzik degistirildi' if eski else 'yeni muzik kanali')
```

### `app/araclar/muzik_yatagi.py`

```python
#!/usr/bin/env python3
"""Videoya arka plan muzigi yatagi uretir (seviye, gerekirse dongu, parca gecisleri, son ekran, fade).
Her --parca kendi araliginda calar; gecislerde 3 sn capraz gecis. Parca araligindan kisaysa dongulu tekrarlanir
(22 Eki 2026 duzeltmesi: dongu ayni dosyanin ayri girdileriyle kurulur; asplit + zincirli acrossfade dongu
yerine kisa ses uretiyordu, muzik videonun sonuna yetmiyordu).
Kullanim: muzik_yatagi.py cikis.m4a --toplam 669.2 --son 661.2 --parca "dosya.mp3@0-172" --parca "dosya2.mp3@172-390" ...
 --hedef -38 (konusma altindaki LUFS), --son-kat 1.67 (son ekranda yukseltme), gecis 3 sn."""
import argparse, subprocess, json, re, os, tempfile, math
from ortak import muzik_olc
p=argparse.ArgumentParser(); p.add_argument('cikis'); p.add_argument('--toplam',type=float,required=True)
p.add_argument('--son',type=float,required=True); p.add_argument('--parca',action='append',required=True)
p.add_argument('--hedef',type=float,default=-38.0); p.add_argument('--son-kat',type=float,default=1.67); p.add_argument('--gecis',type=float,default=3.0)
a=p.parse_args()
olc = muzik_olc
tmp=tempfile.mkdtemp(); G=a.gecis
seg=[]
for x in a.parca:
    f,r=x.rsplit('@',1); s,e=map(float,r.split('-')); seg.append((f,s,e))
seg[-1]=(seg[-1][0],seg[-1][1],a.toplam)
# Her dosyanin en uzun kullanildigi sure (gecis paylari dahil): dongu en az bu kadar olmali.
gerek={}
for i,(f,s,e) in enumerate(seg):
    bas_=max(0,s-G/2); son_=min(a.toplam,e+G/2) if i<len(seg)-1 else a.toplam
    gerek[f]=max(gerek.get(f,0),son_-bas_)
dongu={}
for f,_,_ in seg:
    if f in dongu: continue
    L,b,e=olc(f); g=a.hedef-L; uz=max(e-b,4.0)
    n=max(1,math.ceil((gerek[f]+2)/(uz-2)))  # her ek tekrar capraz geciste 2 sn kisalir
    out=os.path.join(tmp,f'd{len(dongu)}.wav')
    ins_=[]; fc=''
    for i in range(n):
        ins_+=['-i',f]; fc+=f"[{i}]atrim={b}:{e},asetpts=PTS-STARTPTS,volume={g}dB[a{i}];"
    prev='a0'
    for i in range(1,n):
        fc+=f"[{prev}][a{i}]acrossfade=d=2[b{i}];"; prev=f'b{i}'
    fc=fc.rstrip(';').rsplit(f'[{prev}]',1)[0]
    subprocess.run(['ffmpeg','-v','error','-y',*ins_,'-filter_complex',fc,'-ar','44100','-ac','2',out],check=True)
    dongu[f]=out; print(os.path.basename(f),f'{L} LUFS -> {g:+.1f} dB, parca {uz:.1f}s'+(f', {n} kez' if n>1 else ''))
# Parcalar arka arkaya capraz gecisle birlestirilir (acrossfade zinciri). Onceki surumdeki adelay + amix,
# yeni FFmpeg surumlerinde (9.x) ikinci parcadan sonrasini sessiz birakiyordu (Windows testinde goruldu, 22 Eki 2026).
parca=[]
for i,(f,s,e) in enumerate(seg):
    bas=max(0,s-G/2); son=min(a.toplam,e+G/2) if i<len(seg)-1 else a.toplam
    parca.append((f,max(son-bas,0.2)))
ins=[];fc=''
for i,(f,L) in enumerate(parca):
    ins+=['-i',dongu[f]]; fc+=f"[{i}]atrim=0:{L:.3f},asetpts=PTS-STARTPTS[p{i}];"
prev='p0'
for i in range(1,len(parca)):
    d=max(0.05,min(G,parca[i-1][1]-0.1,parca[i][1]-0.1))
    fc+=f"[{prev}][p{i}]acrossfade=d={d:.3f}[x{i}];"; prev=f'x{i}'
E_=a.son
fc+=f"[{prev}]apad=whole_dur={a.toplam},atrim=0:{a.toplam},volume='1+{a.son_kat-1}*min(max((t-({E_}-0.5))/1.5,0),1)':eval=frame,afade=t=in:d=2,afade=t=out:st={a.toplam-3}:d=3"
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',fc,'-c:a','aac','-b:a','256k','-ar','44100',a.cikis],check=True)
print('tamam',a.cikis)
```

### `app/araclar/odak_izgara.py`

```python
#!/usr/bin/env python3
"""Kullanim: odak_izgara.py "<video klasoru>" "<cikti klasoru>"
Her gorsele 3x3 izgara + sahne numarasi cizer, 12'lik kontak sayfalari (sayfa0.jpg ...) uretir.
(Mac surumundeki odak_izgara.sh'in Windows karsiligi; ImageMagick 7'de komut 'magick', 6'da convert/montage.)"""
import glob, os, shutil, subprocess, sys


def im(alt):
    """ImageMagick komutu: 'magick' varsa onunla (Windows), yoksa eski adlar (convert/montage)."""
    m = shutil.which('magick')
    if m:
        return [m] if alt == 'convert' else [m, alt]
    if sys.platform == 'win32':  # Windows'un kendi convert.exe'si (disk dönüştürücü) asla çağrılmaz
        sys.exit("ImageMagick (magick) bulunamadı. '1 - Ilk kurulum.cmd' dosyasını çalıştır.")
    return [shutil.which(alt) or alt]


GIZLI = {'creationflags': 0x08000000} if sys.platform == 'win32' else {}
V, O = sys.argv[1], sys.argv[2]
os.makedirs(O, exist_ok=True)
gorseller = sorted(glob.glob(os.path.join(V, 'visuals', 'sahne*.jpg')))
if not gorseller:
    sys.exit(f'{V}/visuals icinde sahne*.jpg yok')
for f in gorseller:
    n = os.path.basename(f)[5:9]
    subprocess.run(im('convert') + [f, '-resize', '480x268', '-stroke', '#ff3366', '-strokewidth', '1', '-fill', 'none',
                                    '-draw', 'line 160,0 160,268', '-draw', 'line 320,0 320,268',
                                    '-draw', 'line 0,89 480,89', '-draw', 'line 0,178 480,178',
                                    '-gravity', 'south', '-fill', 'yellow', '-undercolor', '#000a', '-pointsize', '22',
                                    '-annotate', '+0+4', n, os.path.join(O, f't{n}.jpg')], check=True, **GIZLI)
kucukler = sorted(glob.glob(os.path.join(O, 't*.jpg')))
for k, i in enumerate(range(0, len(kucukler), 12)):
    subprocess.run(im('montage') + kucukler[i:i + 12] + ['-tile', '3x', '-geometry', '+3+3', os.path.join(O, f'sayfa{k}.jpg')],
                   check=True, **GIZLI)
for s in sorted(glob.glob(os.path.join(O, 'sayfa*.jpg'))):
    print(s)
```

### `app/araclar/ortak.py`

```python
"""Montaj araçlarının ortak yardımcısı: kanal bilgileri Kanal Stüdyosu'nun verdiği ortam değişkenlerinden okunur.

KS_KANAL (kanal klasörü), KS_AYAR (kanal.json), KS_ONEK, KS_URETIM (sahne videolarının kökü), KS_CAPCUT (CapCut
taslak klasörü), KS_ARACLAR (bu klasör), KS_PYTHON. İlk sürümdeki sabit yolların yerine.
"""
import glob
import json
import os
import re

KANAL = os.environ.get('KS_KANAL', '')
ONEK = os.environ.get('KS_ONEK', '')
URETIM = os.environ.get('KS_URETIM', '')
CAPCUT = os.environ.get('KS_CAPCUT', '')
ARACLAR = os.environ.get('KS_ARACLAR', os.path.dirname(os.path.abspath(__file__)))
PY = os.environ.get('KS_PYTHON', 'python3')
AYAR = json.load(open(os.environ['KS_AYAR'], encoding='utf-8')) if os.environ.get('KS_AYAR') else {}
DIL = AYAR.get('dil', {}).get('hedef', 'it')
VIDEO = AYAR.get('montaj', {}).get('video', {})
GEN, YUK, FPS = int(VIDEO.get('width', 1920)), int(VIDEO.get('height', 1080)), int(VIDEO.get('fps', 30))


def kod_al(x):
    """'05' ya da 'BK-05' → 'BK-05' (eski kullanım: yalnız numara)."""
    return x if '-' in x else f'{ONEK}-{x.zfill(int(AYAR.get("kod_hane", 2)))}'


def video(kod):
    return f'{KANAL}/Videolar/{kod}'


def arsiv(kod):
    return f'{KANAL}/Arsiv/{kod}'


def taslak(kod):
    return f'{CAPCUT}/{kod}'


def uretim(kod):
    """Sahne videolarının klasörü: Uretim/<kod>-…-<id8>/ (en yenisi)."""
    adaylar = [p for p in glob.glob(f'{URETIM}/*/video.json') if os.path.basename(os.path.dirname(p)).startswith(kod.lower() + '-')]
    if not adaylar:
        raise SystemExit(f'{kod} için üretim klasörü bulunamadı ({URETIM})')
    return os.path.dirname(max(adaylar, key=os.path.getmtime))


def altyazi(kod):
    return f'{video(kod)}/{kod}_altyazi_{DIL}.srt'


def maskot_dosyasi(no):
    """Maskot numarası (1, 2, …) → Varliklar/Maskot içindeki dosya (kanal ayarındaki sırayla)."""
    d = AYAR.get('montaj', {}).get('maskot', {}).get('dosyalar', [])
    return f'{KANAL}/Varliklar/Maskot/{d[int(no) - 1]}'


TAG = re.compile(r'\[[a-z ]+\]\s*')


MUZIK_UZANTI = ('.mp3', '.m4a', '.wav', '.aac', '.flac')


def muzik_parcalari():
    """Kanalın Varliklar/Muzik klasöründeki parçalar (gizli dosyalar hariç)."""
    k = f'{KANAL}/Varliklar/Muzik'
    if not os.path.isdir(k):
        return []
    return sorted(f'{k}/{f}' for f in os.listdir(k) if f.lower().endswith(MUZIK_UZANTI) and not f.startswith('.'))


def muzik_olc(f):
    """→ (LUFS, kullanılan başlangıç, kullanılan bitiş): baştaki sessizlik ve son 15 sn'deki sessizlik atlanır."""
    import subprocess
    o = subprocess.run(['ffmpeg', '-nostats', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    L = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1])
    s = subprocess.run(['ffmpeg', '-i', f, '-af', 'silencedetect=n=-45dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', s)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', s)]
    bas = en[0] if st and st[0] < 0.05 and en else 0.0
    son = d
    for x in st:
        if x > d - 15:
            son = min(son, x)
            break
    return L, bas, son


# --- CapCut taslak dosyaları (Windows) ---------------------------------------------------------
# Mac'te CapCut taslağı draft_info.json'dan açar; Windows CapCut'ının sürüme göre draft_content.json'u da okuduğu
# bildiriliyor. İkisi birlikte (kök + Timelines/<id> + .bak) aynı içerikle yazılır; okurken hangisi varsa o.
TASLAK_ADLARI = ('draft_info.json', 'draft_content.json')


def taslak_yolu(dr):
    for ad in TASLAK_ADLARI:
        if os.path.exists(f'{dr}/{ad}'):
            return f'{dr}/{ad}'
    return f'{dr}/{TASLAK_ADLARI[0]}'


def taslak_oku(dr):
    return json.load(open(taslak_yolu(dr), encoding='utf-8'))


def taslak_dosyalari(dr):
    """Yazılacak bütün kopyalar: kök ve her Timelines/<id> için iki ad ve .bak'ları."""
    klasorler = [dr] + [p for p in glob.glob(f'{dr}/Timelines/*') if os.path.isdir(p)]
    return [f'{k}/{ad}{ek}' for k in klasorler for ad in TASLAK_ADLARI for ek in ('', '.bak')]


def taslak_yaz(dr, d):
    metin = json.dumps(d, ensure_ascii=False)
    for f in taslak_dosyalari(dr):
        with open(f, 'w', encoding='utf-8') as h:
            h.write(metin)


def capcut_kullanici_verisi():
    """CAPCUT = .../CapCut/User Data/Projects/com.lveditor.draft → .../CapCut/User Data (ileri eğik çizgiyle)."""
    k = os.path.realpath(CAPCUT).replace('\\', '/')
    return k.rsplit('/Projects/', 1)[0] if '/Projects/' in k else k


def win_yolu(p):
    return os.path.realpath(p).replace('\\', '/')
```

### `app/araclar/plan_kontrol.py`

```python
# Kullanim: python3 plan_kontrol.py 05_Montaj_plani.tsv <sahne_sayisi>
# Montaj planinin kurallarini denetler (maskot sirasi kanal ayarindan; KES %65-75, KARARMA sadece bolum degisiminde, KES ile zit hareket yok, ayni hareket 3x yok, kodlar sozlukte).
import sys,csv
from ortak import AYAR
SIRA=[x.strip().upper() for x in AYAR.get('montaj',{}).get('maskot',{}).get('sira',[])]
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8'),delimiter='\t'))
n=int(sys.argv[2]); err=[]
if len(rows)!=n: err.append(f"satir {len(rows)}!={n}")
H={'YAKINLAS','UZAKLAS','SAGA','SOLA','ASAGI','YUKARI','NEFES','SABIT'}
G={'KES','KARISIM','KARARMA','ANI_GIRIS','ANI_CIKIS','SAYFA','ICERI','-'}
E={'-','ESKI_FOTO','VINYET','YUMUSAK_ISIK'}
opp={('YAKINLAS','UZAKLAS'),('SAGA','SOLA'),('ASAGI','YUKARI')}
g=[r['sonraki_gecis'] for r in rows[:-1]]
print('KES %',round(100*g.count('KES')/len(g),1))
for i,r in enumerate(rows):
    if r['hareket'] not in H: err.append(f"{r['sahne']} hareket {r['hareket']}")
    if r['sonraki_gecis'] not in G: err.append(f"{r['sahne']} gecis {r['sonraki_gecis']}")
    if r['efekt'] not in E: err.append(f"{r['sahne']} efekt {r['efekt']}")
    if int(r['sahne'])!=i+1: err.append(f"sira {r['sahne']}")
    if i+1<len(rows):
        s=rows[i+1]
        if r['sonraki_gecis']=='KARARMA' and r['bolum']==s['bolum']: err.append(f"{r['sahne']} KARARMA bolum icinde")
        if r['sonraki_gecis']=='KES' and ((r['hareket'],s['hareket']) in opp or (s['hareket'],r['hareket']) in opp): err.append(f"{r['sahne']}->{s['sahne']} zit hareket KES")
    if i>=2 and rows[i-2]['hareket']==rows[i-1]['hareket']==r['hareket']: err.append(f"{r['sahne']} 3x {r['hareket']}")
if rows and 'maskot' in rows[0]:
    M=[(r['sahne'],r['maskot'].strip().upper()) for r in rows if r.get('maskot','-').strip() not in ('-','')]
    if [m for _,m in M]!=SIRA: err.append(f"maskot sirasi {M} (beklenen {','.join(SIRA) or 'maskot yok'})")
    for sh,m in M:
        r=rows[int(sh)-1]
        if r['hareket'] not in ('NEFES','YAKINLAS'): err.append(f"{sh} maskot sahnesi hareketi {r['hareket']}")
        if r['rol'] in ('guvenlik','cta'): err.append(f"{sh} maskot sahnesi rolu {r['rol']}")
    print('yayin_hazirla maskot:',' '.join(f"--maskot {int(sh)}:{m[1]}:2" for sh,m in M))
print('HATA' if err else 'TEMIZ', err)
```

### `app/araclar/sablon_altyazi.json`

```json
{"track": {"id": "971195FA-1A69-4D34-B6F8-F976EA2CA44E", "type": "text", "segments": [], "flag": 0, "attribute": 0, "name": "", "is_default_name": true}, "segment": {"id": "B4C48D88-205B-4BFE-A264-4DAC82C5FBE7", "source_timerange": null, "target_timerange": {"start": 0, "duration": 2616000}, "render_timerange": {"start": 0, "duration": 0}, "desc": "", "state": 0, "speed": 1.0, "is_loop": false, "is_tone_modify": false, "reverse": false, "intensifies_audio": false, "cartoon": false, "volume": 1.0, "last_nonzero_volume": 1.0, "clip": {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0, "transform": {"x": 0.0, "y": -0.78}, "flip": {"vertical": false, "horizontal": false}, "alpha": 1.0}, "uniform_scale": {"on": true, "value": 1.0}, "material_id": "9903E3DE-CA2C-4D3F-8341-69DB0BA4D55C", "extra_material_refs": ["C1C7263E-59DC-4E08-A617-5B2FBDE7BAE3"], "render_index": 14000, "keyframe_refs": [], "enable_lut": false, "enable_adjust": false, "enable_hsl": false, "visible": true, "group_id": "", "enable_color_curves": true, "enable_hsl_curves": true, "track_render_index": 1, "hdr_settings": null, "enable_color_wheels": true, "track_attribute": 0, "is_placeholder": false, "template_id": "", "enable_smart_color_adjust": false, "template_scene": "default", "common_keyframes": [], "caption_info": null, "responsive_layout": {"enable": false, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0}, "enable_color_match_adjust": false, "enable_color_correct_adjust": false, "enable_adjust_mask": false, "raw_segment_id": "", "lyric_keyframes": null, "enable_video_mask": true, "digital_human_template_group_id": "", "color_correct_alg_result": "", "source": "segmentsourcenormal", "enable_mask_stroke": false, "enable_mask_shadow": false, "enable_color_adjust_pro": false}, "material": {"recognize_task_id": "", "id": "9903E3DE-CA2C-4D3F-8341-69DB0BA4D55C", "name": "", "recognize_text": "", "recognize_model": "", "punc_model": "", "type": "text", "content": "{\"styles\":[{\"bold\":false,\"fill\":{\"alpha\":1.0,\"content\":{\"render_type\":\"solid\",\"solid\":{\"alpha\":1.0,\"color\":[0.23137254901960785,0.16470588235294117,0.11764705882352941]}}},\"font\":{\"id\":\"6807743644842332685\",\"path\":\"/Users/kullanici/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect/666022/f4de001546581298135b09b301b1253f/Nunito-ExtraBoldItalic.ttf\"},\"italic\":false,\"range\":[0,45],\"size\":8.0,\"strokes\":[],\"underline\":false}],\"text\":\"«Mamma, per il tuo\\ncompleanno cosa vorresti?»\"}", "base_content": "", "words": {"start_time": [], "end_time": [], "text": []}, "current_words": {"start_time": [], "end_time": [], "text": []}, "global_alpha": 1.0, "combo_info": {"text_templates": []}, "caption_template_info": {"resource_id": "", "third_resource_id": "", "resource_name": "", "category_id": "", "category_name": "", "effect_id": "", "request_id": "", "path": "", "is_new": false, "source_platform": 0}, "layer_weight": 1, "letter_spacing": 0.0, "text_curve": null, "text_loop_on_path": false, "offset_on_path": 0.0, "enable_path_typesetting": false, "text_exceeds_path_process_type": 0, "text_typesetting_paths": null, "text_typesetting_paths_file": "", "text_typesetting_path_index": 0, "line_spacing": 0.08, "has_shadow": false, "shadow_color": "", "shadow_alpha": 0.9, "shadow_smoothing": 0.45, "shadow_distance": 5.0, "shadow_point": {"x": 0.6363961030678928, "y": -0.6363961030678927}, "shadow_angle": -45.0, "shadow_thickness_projection_enable": false, "shadow_thickness_projection_angle": 0.0, "shadow_thickness_projection_distance": 0.0, "border_alpha": 1.0, "border_color": "", "border_width": 0.08, "border_mode": 0, "style_name": "", "text_color": "#3B2A1E", "text_alpha": 1.0, "font_name": "Nunito", "font_title": "Nunito", "font_size": 8.0, "font_path": "", "font_id": "", "font_resource_id": "6807743644842332685", "initial_scale": 1.0, "font_url": "", "typesetting": 0, "alignment": 1, "line_feed": 1, "use_effect_default_color": true, "is_rich_text": false, "shape_clip_x": false, "shape_clip_y": false, "ktv_color": "", "text_to_audio_ids": [], "bold_width": 0.0, "italic_degree": 0, "underline": false, "underline_width": 0.05, "underline_offset": 0.22, "sub_type": 0, "check_flag": 23, "text_size": 30, "font_category_name": "", "font_source_platform": 0, "font_third_resource_id": "", "font_category_id": "", "add_type": 0, "operation_type": 0, "recognize_type": 0, "fonts": [], "background_color": "#FFF6E4", "background_alpha": 0.88, "background_style": 1, "background_round_radius": 0.35, "background_width": 0.14, "background_height": 0.14, "background_vertical_offset": 0.0, "background_horizontal_offset": 0.0, "background_fill": "", "single_char_bg_enable": false, "single_char_bg_color": "", "single_char_bg_alpha": 1.0, "single_char_bg_round_radius": 0.3, "single_char_bg_width": 0.0, "single_char_bg_height": 0.0, "single_char_bg_vertical_offset": 0.0, "single_char_bg_horizontal_offset": 0.0, "font_team_id": "", "tts_auto_update": false, "text_preset_resource_id": "", "group_id": "it-IT_1790323336167", "preset_id": "", "preset_name": "", "preset_category": "", "preset_category_id": "", "preset_index": 0, "preset_has_set_alignment": false, "force_apply_line_max_width": false, "language": "", "relevance_segment": [], "original_size": [], "fixed_width": -1.0, "fixed_height": -1.0, "line_max_width": 0.82, "oneline_cutoff": false, "cutoff_postfix": "", "subtitle_template_original_fontsize": 0.0, "subtitle_keywords": {"range": []}, "inner_padding": -1.0, "multi_language_current": "none", "source_from": "", "is_lyric_effect": false, "lyric_group_id": "", "lyrics_template": {"resource_id": "", "resource_name": "", "panel": "", "effect_id": "", "path": "", "category_id": "", "category_name": "", "request_id": ""}, "is_batch_replace": false, "is_words_linear": false, "ssml_content": "", "subtitle_keywords_config": null, "sub_template_id": -1, "translate_original_text": ""}, "animation": {"id": "C1C7263E-59DC-4E08-A617-5B2FBDE7BAE3", "type": "sticker_animation", "animations": [], "multi_language_current": "none"}}
```

### `app/araclar/senk_kontrol.py`

```python
# Kullanim: python3 senk_kontrol.py <KOD>        (ör. BK-04)
#           python3 senk_kontrol.py <KOD> --metin  (ayrica paragraflari listeler: gorsel-cumle kontrolu icin)
# Salt okunur. Kontrol eder: senaryo paragrafi = Pipeline'in seslendirdigi metin; gorsel/ses/sahne videosu
# dosya sirasi; sahne videosu = ses + ~0.35 sn; kanal video olcusu + ses; CapCut taslagi (<KOD>) sira ve sure;
# her altyazi kendi sahnesinin icinde ve o sahnenin cumlesinden; konusma hizi sapmalari; ses seviyesi/uzun sessizlik.
import json,re,sys,subprocess,os,glob
from ortak import kod_al, uretim, video, taslak, altyazi, GEN, YUK, taslak_yolu
kod=kod_al(sys.argv[1]); V=uretim(kod)
D=video(kod); DR=taslak_yolu(taslak(kod))
par=lambda f:[x.strip() for x in re.split(r'\n\s*\n',open(f,encoding='utf-8').read().strip()) if x.strip()]
P=par(f'{D}/02_ElevenLabs_seslendirme_metni.txt'); Q=par(f'{D}/03_Gorsel_promptlari.txt')
vj=json.load(open(f'{V}/video.json'))['scenes']; dr=json.load(open(DR))
clean=lambda s:re.sub(r'\[[a-z ]+\]\s*','',s).strip(); norm=lambda s:re.sub(r'[^\w]','',s.lower())
def probe(f): return json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',f],capture_output=True,text=True).stdout)
iss=[]; print(f'{kod}: paragraf {len(P)} · prompt {len(Q)} · Pipeline sahne {len(vj)}')
if not len(P)==len(Q)==len(vj): iss.append('SAYILAR ESIT DEGIL')
vt=[t for t in dr['tracks'] if t['type']=='video'][0]['segments']; mats={m['id']:m for m in dr['materials']['videos']}

if len(vt)==len(vj)+1 and '_son.mp4' in {m['id']:m for m in dr['materials']['videos']}[vt[-1]['material_id']]['path']: print('son ekran var: %.1f sn' % (vt[-1]['target_timerange']['duration']/1e6))
elif len(vt)!=len(vj): iss.append(f'taslakta {len(vt)} sahne var')
t0=0; rows=[]
for i,s in enumerate(vj):
    num=f'{i+1:04d}'
    if clean(s['text'])!=clean(P[i]): iss.append(f'{num} METIN FARKLI: Pipeline="{s["text"][:60]}" / dosya="{P[i][:60]}"')
    for k,exp in (('media_file',f'visuals/sahne{num}.jpg'),('audio_file',f'audio/sahne{num}.mp3'),('video_file',f'scene-videos/sahne{num}.mp4')):
        if s[k]!=exp: iss.append(f'{num} {k}={s[k]}')
    a=float(probe(f'{V}/audio/sahne{num}.mp3')['format']['duration']); v=probe(f'{V}/scene-videos/sahne{num}.mp4'); vd=float(v['format']['duration'])
    st=[x for x in v['streams'] if x['codec_type']=='video'][0]
    if not (0.2<vd-a<0.5): iss.append(f'{num} ses {a:.2f} sn / sahne videosu {vd:.2f} sn')
    if (st['width'],st['height'])!=(GEN,YUK): iss.append(f'{num} boyut {st["width"]}x{st["height"]}')
    if not any(x['codec_type']=='audio' for x in v['streams']): iss.append(f'{num} sahne videosunda ses yok')
    seg=vt[i]; m=mats[seg['material_id']]
    if not (m['path'].endswith(f'sahne{num}.mp4') or m['path'].endswith(f'sahne{num}_maskot.mp4')): iss.append(f'{num} taslakta yanlis dosya {m["path"][-20:]}')
    st0=seg['target_timerange']['start']/1e6; du=seg['target_timerange']['duration']/1e6
    if abs(st0-t0)>0.05: iss.append(f'{num} taslakta bosluk/ust uste: {st0:.2f} (beklenen {t0:.2f})')
    rows.append((num,st0,du,a,len(clean(P[i]).split()))); t0+=du
rates=sorted(r[4]/r[3] for r in rows); med=rates[len(rates)//2]
for r in rows:
    if r[4]/r[3]<med*0.6 or r[4]/r[3]>med*1.5: iss.append(f'{r[0]} konusma hizi farkli: {r[4]} kelime / {r[3]:.1f} sn (orta {med:.2f} k/sn) - dinle')
def ts(x):h,m,s=x.split(':');return int(h)*3600+int(m)*60+float(s.replace(',','.'))
srt=open(altyazi(kod),encoding='utf-8').read().strip().split('\n\n'); B=[(r[1],r[1]+r[2]) for r in rows]
for b in srt:
    L=b.split('\n'); a,e=[ts(x) for x in L[1].split(' --> ')]; txt=' '.join(L[2:]); mid=(a+e)/2
    k=next((j for j,(x,y) in enumerate(B) if x<=mid<y+0.001),len(B)-1)
    if norm(txt) not in norm(clean(P[k])):
        w=[j+1 for j in range(max(0,k-2),min(len(P),k+3)) if norm(txt) in norm(clean(P[j]))]; iss.append(f'ALTYAZI {L[1]} "{txt[:50]}" sahne {k+1} zamaninda ama metni sahne {w}')
    if a<B[k][0]-0.05 or e>B[k][1]+0.05: iss.append(f'ALTYAZI {L[1]} sahne {k+1} sinirini asiyor')
tt=[t for t in dr['tracks'] if t['type']=='text'][0]['segments']
if len(tt)!=len(srt): iss.append(f'SRT {len(srt)} satir, taslakta {len(tt)} altyazi')
for r in rows:
    o=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f'{V}/audio/sahne{r[0]}.mp3','-af','silencedetect=n=-40dB:d=1.5,volumedetect','-f','null','-'],capture_output=True,text=True).stderr
    mv=float(re.search(r'mean_volume: ([-\d.]+)',o).group(1)); mx=float(re.search(r'max_volume: ([-\d.]+)',o).group(1)); sl=re.findall(r'silence_duration: ([\d.]+)',o)
    if mv<-26 or mv>-13: iss.append(f'{r[0]} ses seviyesi {mv} dB (normal ~-18)')
    if mx>=0: iss.append(f'{r[0]} ses tepesi {mx} dB (cizirti riski)')
    if sl: iss.append(f'{r[0]} {", ".join(sl)} sn sessizlik (metinde [pause] yoksa dinle)')
print(f'toplam {t0:.1f} sn · SRT {len(srt)} · taslak altyazi {len(tt)}')
print('SONUC: TEMIZ' if not iss else f'SONUC: {len(iss)} not'); print('\n'.join(iss))
if '--metin' in sys.argv:
    for i,p in enumerate(P): print(f'{i+1:04d}',clean(p)[:170])
```

### `app/araclar/srt_uret.py`

```python
# Sahne metni + ses süreleri + ses içindeki duraklamalardan senkron SRT üretir.
import re, subprocess, sys, glob, os
VID, TXT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MAXC = 84  # iki satır x 42 karakter
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
def pauses(f):
    o = subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','silencedetect=n=-40dB:d=0.18','-f','null','-'],capture_output=True,text=True).stderr
    s=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; e=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
    return [((a+b)/2,a,b) for a,b in zip(s,e)]
def wrap(t):
    if len(t)<=42: return t
    if len(t)>92:
        w=t.split(); n=len(w); a=' '.join(w[:n//3]); b=' '.join(w[n//3:2*n//3]); c=' '.join(w[2*n//3:]); return a+'\n'+b+'\n'+c
    w=t.split(); best=None
    for i in range(1,len(w)):
        a,b=' '.join(w[:i]),' '.join(w[i:]); m=max(len(a),len(b))
        if best is None or m<best[0]: best=(m,a+'\n'+b)
    return best[1]
def chunks(sent):
    if len(sent)<=MAXC: return [sent]
    # önce virgül/iki nokta, sonra kelime
    parts=re.split(r'(?<=[,:;])\s+',sent); out=[]; cur=''
    for p in parts:
        if len(cur)+len(p)+1<=MAXC: cur=(cur+' '+p).strip()
        else:
            if cur: out.append(cur)
            while len(p)>MAXC:
                w=p.split(); c=''
                while w and len(c)+len(w[0])+1<=MAXC: c=(c+' '+w.pop(0)).strip()
                out.append(c); p=' '.join(w)
            cur=p
    if cur: out.append(cur)
    return out
paras=[p.strip() for p in open(TXT,encoding='utf-8').read().split('\n\n') if p.strip()]
vids=sorted(glob.glob(os.path.join(VID,'scene-videos','sahne*.mp4')))
auds=sorted(glob.glob(os.path.join(VID,'audio','sahne*.mp3')))
assert len(paras)==len(vids)==len(auds), (len(paras),len(vids),len(auds))
def ts(x):
    ms=int(round(x*1000)); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000); return f'{h:02}:{m:02}:{s:02},{ms:03}'
cues=[]; t0=0.0
for para,v,a in zip(paras,vids,auds):
    text=re.sub(r'\[[a-z ]+\]\s*','',para).strip()
    ad=dur(a); vd=dur(v); ps=[p for p in pauses(a) if 0.15<p[0]<ad-0.15]
    # konuşmanın gerçek bitişi (sondaki sessizlik hariç)
    tail=[p for p in pauses(a) if p[2]>=ad-0.05]; end=tail[0][1] if tail else ad
    sents=[s for s in re.split(r'(?<=[.!?…»])\s+(?=[«A-ZÀ-ÝÀ-ſ])',text) if s]
    pieces=[]; 
    for s in sents:
        for c in chunks(s): pieces.append(c)
    L=sum(len(p) for p in pieces); acc=0; bounds=[0.0]
    for p in pieces[:-1]:
        acc+=len(p); est=end*acc/L
        # en yakın duraklamaya yapıştır (±0.8 sn)
        near=[q for q in ps if abs(q[0]-est)<0.8 and q[0]>bounds[-1]+0.4]
        bounds.append(min(near,key=lambda q:abs(q[0]-est))[0] if near else est)
    bounds.append(end)
    # çok kısa kalan satırları (<0,9 sn) komşusuyla birleştir
    segs=[[bounds[i],bounds[i+1],p] for i,p in enumerate(pieces)]
    changed=True
    while changed and len(segs)>1:
        changed=False
        for i,(a_,b_,p) in enumerate(segs):
            if b_-a_<0.9:
                j=i-1 if i>0 else i+1
                if i>0 and i+1<len(segs) and len(segs[i+1][2])<len(segs[i-1][2]): j=i+1
                lo,hi=min(i,j),max(i,j)
                segs[lo]=[segs[lo][0],segs[hi][1],segs[lo][2]+' '+segs[hi][2]]; del segs[hi]; changed=True; break
    for i,(a_,b_,p) in enumerate(segs):
        st=t0+a_; en=t0+b_
        if i+1<len(segs): en-=0.05
        cues.append((st,en,wrap(p) if len(p)<=MAXC+10 else wrap(p)))
    t0+=vd
with open(OUT,'w',encoding='utf-8') as f:
    for i,(s,e,t) in enumerate(cues,1): f.write(f'{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n')
print('cues',len(cues),'toplam',ts(t0))
```

### `app/araclar/yayin_hazirla.py`

```python
#!/usr/bin/env python3
"""CapCut taslagina yayin oncesi son dokunuslar (CapCut KAPALI olmali):
 - secilen sahnelere maskot gomer (maskot_gom.py), o sahnelerin anahtar karelerini siler
 - son sahnenin son karesiyle 8 sn son ekran (hafif yakinlasma, altyazisiz)
 - altyazilari y=-0.68'e alir
 - muzik yatagini (media/muzik_<KOD>.m4a) ses kanalina ekler. Dosya yoksa muzik_otomatik.py
   Varliklar/Muzik'ten RASTGELE 2 parca secip uretir. --muziksiz ile muzik eklenmez.
Kullanim: yayin_hazirla.py <KOD> --maskot 7:1:2 --maskot 20:2:2 ...   (sahne:maskotNo:baslangicSn)"""
import json, uuid, copy, sys, os, subprocess, argparse, tempfile
from ortak import kod_al, taslak, arsiv, maskot_dosyasi, ARACLAR, CAPCUT, PY, taslak_oku, taslak_yolu, taslak_yaz
p=argparse.ArgumentParser(); p.add_argument('x'); p.add_argument('--maskot',action='append',default=[]); p.add_argument('--son-sn',type=float,default=8.0); p.add_argument('--muziksiz',action='store_true'); p.add_argument('--tohum')
a=p.parse_args()
KOD=kod_al(a.x); DR=taslak(KOD); MD=f'{DR}/media'
U=lambda: str(uuid.uuid4()).upper()
d=taslak_oku(DR); M=d['materials']
PH=[m['path'] for m in M['videos'] if 'placeholder' in m['path']][0].rsplit('/media/',1)[0]+'/media/'
idx={x.get('id'):k for k,v in M.items() if isinstance(v,list) for x in v}
getm=lambda i:[x for x in M[idx[i]] if x['id']==i][0]
V=[t for t in d['tracks'] if t['type']=='video'][0]; S=V['segments']
T=[t for t in d['tracks'] if t['type']=='text'][0]
assert not any(t['type']=='audio' for t in d['tracks']), 'zaten muzik var'
voice_end=d['duration']
def vmat(tmpl,name,dur):
    m=copy.deepcopy(tmpl); m['id']=U(); m['path']=PH+name; m['material_name']=name; m['duration']=dur; m['local_material_id']=str(uuid.uuid4()); M['videos'].append(m); return m
def kfval(seg,prop,t,default):
    for k in seg['common_keyframes']:
        if k['property_type']==prop:
            L=sorted((x['time_offset']/1e6,x['values'][0]) for x in k['keyframe_list'])
            if t<=L[0][0]: return L[0][1]
            if t>=L[-1][0]: return L[-1][1]
            for (t0,v0),(t1,v1) in zip(L,L[1:]):
                if t0<=t<=t1: return v0+(v1-v0)*(t-t0)/(t1-t0)
    return default
# 1) maskot
for spec in a.maskot:
    n,mk,bas=spec.split(':'); n=int(n); s=S[n-1]; m=getm(s['material_id'])
    src=f"{MD}/{os.path.basename(m['path'])}"; out=f"{MD}/sahne{n:04d}_maskot.mp4"
    dur=s['target_timerange']['duration']/1e6
    ts=sorted({0.0,dur}|{x['time_offset']/1e6 for k in s['common_keyframes'] for x in k['keyframe_list']})
    c=s['clip']; kf=';'.join(f"{t:.6f},{kfval(s,'KFTypeScaleX',t,c['scale']['x']):.6f},{kfval(s,'KFTypePositionX',t,c['transform']['x']):.6f},{kfval(s,'KFTypePositionY',t,c['transform']['y']):.6f}" for t in ts)
    dur_=lambda f: float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout or 0)
    if not (os.path.exists(out) and abs(dur_(out)-dur_(src))<0.05):  # onceden tam uretildiyse atla
        subprocess.run([PY,f'{ARACLAR}/maskot_gom.py',src,maskot_dosyasi(mk),out,'--basla',bas,'--kf',kf],check=True)
    fd=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout)
    nm=vmat(m,os.path.basename(out),int(round(fd*1e6)))
    s['material_id']=nm['id']; s['common_keyframes']=[]
    s['clip']['scale']={'x':1.0,'y':1.0}; s['clip']['transform']={'x':0.0,'y':0.0}; s['uniform_scale']={'on':True,'value':1.0}
    print('maskot', n, 'kf', kf)
# 2) son ekran
last=S[-1]; lm=getm(last['material_id']); lsrc=f"{MD}/{os.path.basename(lm['path'])}"
son=f"{MD}/{os.path.splitext(os.path.basename(lm['path']))[0]}_son.mp4"
TMP=tempfile.mkdtemp(); SP=os.path.join(TMP,'son.png')  # oturuma ozel gecici klasor (ortak /tmp cakismasi olmaz)
subprocess.run(f'ffmpeg -v error -y -sseof -0.1 -i "{lsrc}" -frames:v 1 -update 1 "{SP}" && ffmpeg -v error -y -loop 1 -framerate 30 -i "{SP}" -f lavfi -i anullsrc=r=44100:cl=stereo -t {a.son_sn} -c:v libx264 -pix_fmt yuv420p -crf 16 -r 30 -c:a aac -shortest "{son}"',shell=True,check=True)
e=copy.deepcopy(last); e['id']=U(); SD=int(a.son_sn*1e6)
em=vmat(lm,os.path.basename(son),SD)
e['material_id']=em['id']; e['target_timerange']={'start':voice_end,'duration':SD}; e['source_timerange']={'start':0,'duration':SD}
refs=[]
for r in last['extra_material_refs']:
    k=idx[r]
    if k in ('video_effects','transitions','material_animations'): continue
    mm=copy.deepcopy(getm(r)); mm['id']=U(); M[k].append(mm); refs.append(mm['id'])
e['extra_material_refs']=refs
# son ekran, son sahnenin bittigi olcekten baslar
es=kfval(last,'KFTypeScaleX',last['target_timerange']['duration']/1e6,last['clip']['scale']['x'])
ex=kfval(last,'KFTypePositionX',9e9,last['clip']['transform']['x']); ey=kfval(last,'KFTypePositionY',9e9,last['clip']['transform']['y'])
def kf(pt,pts): return {"id":U(),"material_id":"","property_type":pt,"keyframe_list":[{"id":U(),"curveType":"Line","time_offset":t,"left_control":{"x":0.0,"y":0.0},"right_control":{"x":0.0,"y":0.0},"values":[v],"string_value":"","graphID":""} for t,v in pts]}
e['clip']['scale']={'x':es,'y':es}; e['clip']['transform']={'x':ex,'y':ey}; e['uniform_scale']={'on':True,'value':1.0}
e['common_keyframes']=[kf('KFTypeScaleX',[(0,es),(SD,es*1.02)]),kf('KFTypePositionX',[(0,ex),(SD,ex)]),kf('KFTypePositionY',[(0,ey),(SD,ey)])]
S.append(e)
# 3) altyazi
for s in T['segments']: s['clip']['transform']['y']=-0.68
# 4) muzik
mf=f'{MD}/muzik_{KOD}.m4a'
if not a.muziksiz and not os.path.exists(mf):
    subprocess.run([PY,f'{ARACLAR}/muzik_otomatik.py',KOD]+(['--tohum',a.tohum] if a.tohum else [])+['--son-sn',str(a.son_sn)],check=True)
MUZIK=(not a.muziksiz) and os.path.exists(mf)
if MUZIK:
  md=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',mf],capture_output=True,text=True).stdout)
  aid=U(); sid=U(); spid=U(); AD=min(int(md*1e6)-1000, voice_end+SD)
  M['audios'].append({"app_id":0,"category_id":"","category_name":"local","check_flag":3,"copyright_limit_type":"none","duration":int(md*1e6),"effect_id":"","formula_id":"","id":aid,"local_material_id":aid,"music_id":aid,"name":os.path.basename(mf),"path":PH+os.path.basename(mf),"source_platform":0,"type":"extract_music","wave_points":[]})
  M['speeds'].append({"curve_speed":None,"id":spid,"mode":0,"speed":1.0,"type":"speed"})
  seg={"enable_adjust":True,"enable_color_correct_adjust":False,"enable_color_curves":True,"enable_color_match_adjust":False,"enable_color_wheels":True,"enable_lut":True,"enable_smart_color_adjust":False,"last_nonzero_volume":1.0,"reverse":False,"track_attribute":0,"track_render_index":0,"visible":True,"id":sid,"material_id":aid,"target_timerange":{"start":0,"duration":AD},"common_keyframes":[],"keyframe_refs":[],"source_timerange":{"start":0,"duration":AD},"speed":1.0,"volume":1.0,"extra_material_refs":[spid],"clip":None,"hdr_settings":None,"render_index":0}
  d['tracks'].append({"attribute":0,"flag":0,"id":U(),"is_default_name":False,"name":"muzik","type":"audio","segments":[seg]})
d['duration']=voice_end+SD
os.makedirs(arsiv(KOD),exist_ok=True)
import shutil; shutil.copy(taslak_yolu(DR),f'{arsiv(KOD)}/draft_info_yayin_oncesi.json')
import glob as _g  # CapCut taslağı Timelines/<id>/draft_info.json'dan açar: hepsini birlikte yaz
taslak_yaz(DR, d)  # draft_info.json ve draft_content.json, kök + Timelines, .bak'larıyla
for f in (f'{DR}/draft_meta_info.json',):
    m=json.load(open(f)); m['tm_duration']=d['duration']; json.dump(m,open(f,'w'),ensure_ascii=False)
r=json.load(open(f'{CAPCUT}/root_meta_info.json'))
for x in r['all_draft_store']:
    if x.get('draft_name')==KOD: x['tm_duration']=d['duration']
json.dump(r,open(f'{CAPCUT}/root_meta_info.json','w'),ensure_ascii=False)
print('tamam', len(S), 'sahne, sure', d['duration']/1e6, '| muzik:', 'var' if MUZIK else 'YOK')
```

### `app/skills/kanal-studyosu-flow/SKILL.md`

```markdown
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
```

### `app/requirements.txt`

```text
anthropic>=1.11,<2
keyring>=25
send2trash>=1.8
pillow>=10
```

### `app/windows/baslat.ps1`

```powershell
# Kanal Stüdyosu (Windows) başlatıcı. "Kanal Stüdyosu.vbs" bunu gizli pencerede çalıştırır.
# Kurulum klasörü = bu dosyanın iki üstü (app\windows → app → kurulum). Uygulamanın bütün verisi Sistem\ ve Kanallar\'dadır.
# İlk açılışta (ya da ortam bozulduysa) uygulamanın kendi Python ortamını Sistem\.venv'e kurar; sistem Python'una paket kurmaz.
$ErrorActionPreference = 'Continue'
$App = Split-Path -Parent $PSScriptRoot
$Kok = Split-Path -Parent $App
$env:KANAL_STUDYOSU_KOK = $Kok
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$Sistem = Join-Path $Kok 'Sistem'
New-Item -ItemType Directory -Force -Path $Sistem | Out-Null
$Log = Join-Path $Sistem 'kayit.log'
$Venv = Join-Path $Sistem '.venv'
$VPy = Join-Path $Venv 'Scripts\python.exe'
$VPyw = Join-Path $Venv 'Scripts\pythonw.exe'
$Req = Join-Path $App 'requirements.txt'

function Yaz([string]$m, [string]$tur = 'bilgi') {
    Add-Content -Path $Log -Value ("{0} [{1}] {2}" -f (Get-Date -Format 'HH:mm:ss'), $tur, $m) -Encoding UTF8
}
function Uyari([string]$baslik, [string]$mesaj) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show($mesaj, $baslik, 'OK', 'Error') | Out-Null
}
function SonHata {
    if (Test-Path $Log) { (Get-Content $Log -Encoding UTF8 | Where-Object { $_.Trim() } | Select-Object -Last 1) } else { '' }
}
function Calistir([string]$exe, [string]$argumanlar) {
    # Çıktısı kayda eklenir; dönüş: çıkış kodu
    $o = [System.IO.Path]::GetTempFileName(); $e = [System.IO.Path]::GetTempFileName()
    $p = Start-Process -FilePath $exe -ArgumentList $argumanlar -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $o -RedirectStandardError $e
    foreach ($f in @($o, $e)) { Get-Content $f -Encoding UTF8 | Add-Content -Path $Log -Encoding UTF8; Remove-Item $f -ErrorAction SilentlyContinue }
    return $p.ExitCode
}
function PythonBul {
    # Önce py başlatıcısı, sonra PATH'teki python (Microsoft Store kısayolu değil), sonra bilinen klasörler. En az 3.10.
    $kontrol = 'import sys; print(sys.executable) if sys.version_info >= (3, 10) else sys.exit(1)'
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) { $y = & $py.Source -3 -c $kontrol 2>$null; if ($LASTEXITCODE -eq 0 -and $y) { return $y.Trim() } }
    $adaylar = @(Get-Command python.exe -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | ForEach-Object { $_.Source })
    $adaylar += @(Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe", "$env:ProgramFiles\Python3*\python.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | ForEach-Object { $_.FullName })
    foreach ($a in $adaylar) { $y = & $a -c $kontrol 2>$null; if ($LASTEXITCODE -eq 0 -and $y) { return $y.Trim() } }
    return $null
}
function OrtamCalisiyor {
    if (-not (Test-Path $VPy)) { return $false }
    & $VPy -c 'import sys' 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}
function KutuphanelerVar {
    & $VPy -c 'import anthropic, keyring, send2trash, PIL' 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

$Python = PythonBul
if (-not $Python) {
    Uyari 'Python bulunamadı' "Kanal Stüdyosu için Python 3.10 veya üstü gerekir. Kurulum klasöründeki '1 - Ilk kurulum.cmd' dosyasını çalıştır."
    exit 1
}
$imza = (Get-FileHash $Req -Algorithm SHA256).Hash.Substring(0, 16)
$imzaDosyasi = Join-Path $Venv '.gereksinim'
$hazir = (OrtamCalisiyor) -and (Test-Path $imzaDosyasi) -and ((Get-Content $imzaDosyasi -Raw).Trim() -eq $imza) -and (KutuphanelerVar)
if (-not $hazir) {
    Yaz 'Uygulama ortamı kuruluyor (ilk açılış, güncelleme ya da bozulan ortamın onarımı)…'
    if (-not (OrtamCalisiyor)) {
        # Bozuk ya da eski ortam temizlenip yeniden kurulur (--clear: yalnız uygulamanın kendi ortamı)
        if ((Calistir $Python "-m venv --clear `"$Venv`"") -ne 0 -or -not (OrtamCalisiyor)) {
            Uyari 'Kurulum yapılamadı' ("Uygulamanın Python ortamı kurulamadı. Son hata: " + (SonHata) + " — Ayrıntı: Sistem\kayit.log")
            exit 1
        }
    }
    Calistir $VPy '-m pip install --quiet --upgrade pip' | Out-Null
    if ((Calistir $VPy "-m pip install --quiet -r `"$Req`"") -ne 0) {
        Yaz 'Kütüphaneler kurulamadı; uygulama yine açılıyor (Claude Code ile çalışır). Sonraki açılışta yeniden denenecek.' 'uyari'
    } else {
        Set-Content -Path $imzaDosyasi -Value $imza -Encoding ASCII
    }
}
# Sunucu konsolsuz (pythonw) başlar, tarayıcı açılır; uygulama zaten açıksa yeni kopya başlamaz (tek_kopya.py).
Start-Process -FilePath $VPyw -ArgumentList '-m', 'kanal_studyosu' -WorkingDirectory $App
exit 0
```

### `app/windows/ilk_kurulum.ps1`

```powershell
# Kanal Stüdyosu (Windows) · ilk kurulum. Bir kez çalıştırman yeterli. Hiçbir dosyayı silmez.
$App = Split-Path -Parent $PSScriptRoot
$Kok = Split-Path -Parent $App
Write-Host '== Kanal Stüdyosu · ilk kurulum ==' -ForegroundColor Cyan
Write-Host ''
# İnternetten indirilen dosyaların "engellendi" işaretini kaldır (yoksa Windows açarken uyarır)
Get-ChildItem -Path $Kok -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue
Write-Host '✓ Dosyaların indirme engeli kaldırıldı.'

$winget = Get-Command winget.exe -ErrorAction SilentlyContinue
function Kur([string]$kimlik, [string]$ad) {
    if (-not $winget) { Write-Host "  ! winget yok: $ad'ı elle kur." -ForegroundColor Yellow; return }
    Write-Host "  $ad kuruluyor…"
    winget install -e --id $kimlik --accept-source-agreements --accept-package-agreements --silent
}
$pyVar = $false
$py = Get-Command py.exe -ErrorAction SilentlyContinue
if ($py) { & $py.Source -3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>$null; $pyVar = ($LASTEXITCODE -eq 0) }
if (-not $pyVar) { Kur 'Python.Python.3.12' 'Python 3.12' } else { Write-Host '✓ Python kurulu.' }
if (-not (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue)) { Kur 'Gyan.FFmpeg' 'FFmpeg' } else { Write-Host '✓ FFmpeg kurulu.' }
if (-not (Get-Command magick.exe -ErrorAction SilentlyContinue)) { Kur 'ImageMagick.ImageMagick' 'ImageMagick' } else { Write-Host '✓ ImageMagick kurulu.' }

Write-Host ''
if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-Host '✓ Claude Code kurulu. Aboneliğinle giriş yaptığından emin ol: PowerShell''de  claude  yaz, /login.'
} else {
    Write-Host 'Claude Code kurulu değil. Yazım işleri Claude Code aboneliğinle yapılır.' -ForegroundColor Yellow
    $c = Read-Host 'Claude Code şimdi kurulsun mu? (e/h)'
    if ($c -eq 'e' -or $c -eq 'E') {
        Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
        Write-Host 'Kurulduysa yeni bir PowerShell penceresinde  claude  yazıp /login ile aboneliğinle giriş yap.'
    } else {
        Write-Host 'Sonra kurmak için: https://claude.com/claude-code'
    }
}

# Masaüstüne kısayol
try {
    $sh = New-Object -ComObject WScript.Shell
    $lnk = $sh.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Kanal Stüdyosu.lnk'))
    $lnk.TargetPath = 'wscript.exe'
    $lnk.Arguments = '"' + (Join-Path $Kok 'Kanal Stüdyosu.vbs') + '"'
    $lnk.WorkingDirectory = $Kok
    $lnk.Description = 'Kanal Stüdyosu'
    $lnk.Save()
    Write-Host '✓ Masaüstüne "Kanal Stüdyosu" kısayolu kondu.'
} catch { Write-Host '  ! Masaüstü kısayolu oluşturulamadı; kurulum klasöründeki "Kanal Stüdyosu.vbs" ile aç.' -ForegroundColor Yellow }

Write-Host ''
Write-Host 'CapCut: capcut.com adresinden CapCut''ın (İngilizce, uluslararası) masaüstü sürümünü kur ve bir kez açıp kapat.'
Write-Host 'Çin sürümü JianYing (剪映) kullanma: taslak dosyalarını şifreliyor.'
Write-Host ''
Write-Host 'Bitti. Yeni kurulan programların görünmesi için bu pencereyi kapat, sonra masaüstündeki "Kanal Stüdyosu"na çift tıkla.' -ForegroundColor Green
Write-Host 'İlk açılışta uygulama bu klasörde Sistem\ ve Kanallar\ klasörlerini kurar ve kendi kütüphanesini indirir (~1 dk).'
Read-Host 'Kapatmak için Enter'
```

### `paket/1 - Ilk kurulum.cmd`

```bat
@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0app\windows\ilk_kurulum.ps1"
```

### `paket/KURULUM.txt`

```text
KANAL STÜDYOSU (WINDOWS) · KURULUM

0. Zip'i açmadan önce: zip dosyasına sağ tık › Özellikler › alttaki "Engellemeyi kaldır" kutusunu işaretle › Tamam.
   (İnternetten inen dosyalarda Windows her açılışta uyarı gösterir; bu adım onu önler.)
1. Zip'i istediğin yere aç (ör. Belgeler\Kanal Stüdyosu). Uygulamanın bütün verisi bu klasörde durur:
   Sistem\ (ayarlar, maliyet, kayıt) ve Kanallar\ (her kanalın klasörü).
2. "1 - Ilk kurulum.cmd" dosyasına çift tıkla (bir kez). Eksik programları (Python, FFmpeg, ImageMagick) winget ile
   kurar, istersen Claude Code'u kurar ve masaüstüne "Kanal Stüdyosu" kısayolu koyar.
3. Claude Code'a aboneliğinle giriş yap: PowerShell'i aç, "claude" yaz, /login.
4. CapCut: capcut.com adresinden CapCut'ın uluslararası (İngilizce) masaüstü sürümünü kur ve bir kez açıp kapat.
   Çin sürümü JianYing kullanma (taslak dosyalarını şifreliyor).
5. Masaüstündeki "Kanal Stüdyosu"na çift tıkla. İlk açılış ~1 dakika sürer (uygulama kendi kütüphanesini kurar).
6. Ayarlar'da "Claude Code'u kontrol et", AI84 (seslendirme) anahtarını gir, sonra "+ Kanal ekle".
7. Görseller için "kanal-studyosu-flow.zip" becerisini Claude masaüstü uygulamasına bir kez yükle
   (Ayarlar › Beceriler › yükle).

Klasörü taşımak istersen uygulamayı kapatıp klasörün tamamını taşı; masaüstü kısayolunu "1 - Ilk kurulum.cmd" ile yenile.
Bu sürüm Mac sürümü 1.2.3'ten uyarlandı; Mac sürümündeki sonraki değişiklikler buraya kendiliğinden gelmez.
```

### `paket/Kanal Stüdyosu.vbs`

```vb
Set sh = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
k = fs.GetParentFolderName(WScript.ScriptFullName)
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & k & "\app\windows\baslat.ps1""", 0, False
```

### `build_paket.py`

````python
#!/usr/bin/env python3
"""Windows dağıtım paketi: windows/dist/Kanal Stüdyosu (Windows).zip

İçinde: Kanal Stüdyosu.vbs (başlatıcı), 1 - Ilk kurulum.cmd, KURULUM.txt, KULLANIM.md, SPECS.md,
kanal-studyosu-flow.zip, app/ (program) ve geliştirme için CLAUDE.md, Gelistirme.txt, .gitignore, tests/.
tests/ yalnız Örnek içeriği gerektirmeyen test dosyalarıdır; örnek kanal ve defter uydurma veridir
(tests/ornek_veri). Linux ya da Mac'te de çalışır. SPECS.md'yi de üretir.
"""
from __future__ import annotations

import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

W = Path(__file__).resolve().parent
DIST = W / "dist"
AD = "Kanal Stüdyosu"
DIL = {".py": "python", ".js": "javascript", ".html": "html", ".css": "css", ".json": "json", ".ps1": "powershell",
       ".vbs": "vb", ".cmd": "bat", ".md": "markdown", ".txt": "text"}


# Pakete giren testler: Örnek'nin gerçek metinlerine (tests/veri) ihtiyaç duymayanlar.
PAKET_TESTLERI = ("parite_yardim.py", "test_claude_code.py", "test_genel_kanal.py", "test_hazir_metin.py",
                  "test_kanal_sablonu.py", "test_kanallar.py", "test_muzik.py", "test_parite_openrouter.py",
                  "test_parite_ses.py", "test_parite_ses_kenar.py", "test_parite_tek_kopya.py", "test_windows.py")


def _gec(p: Path) -> bool:
    return "__pycache__" in p.parts or p.suffix == ".pyc" or p.name == ".DS_Store"


def specs() -> Path:
    app = W / "app"
    liste = sorted((app / "kanal_studyosu").glob("*.py"))
    liste += [app / "kanal_studyosu/web" / a for a in ("index.html", "app.js", "stil.css")]
    liste += sorted((app / "config").glob("*.json")) + sorted((app / "sablonlar").rglob("*.md"))
    liste += sorted(p for p in (app / "araclar").glob("*") if p.is_file() and p.suffix in (".py", ".json"))
    liste += sorted((app / "skills").rglob("SKILL.md")) + [app / "requirements.txt"]
    liste += sorted((app / "windows").glob("*.ps1")) + sorted(p for p in (W / "paket").iterdir() if p.is_file())
    liste += [W / "build_paket.py"]
    try:
        surum = subprocess.run(["git", "-C", str(W), "log", "-1", "--format=%h %ad", "--date=short"],
                               capture_output=True, text=True).stdout.strip()
    except OSError:
        surum = ""
    parca = ["# Kanal Stüdyosu (Windows) · Teknik şartname (SPECS)\n",
             (W / "README.md").read_text(encoding="utf-8").split("\n", 1)[1],
             "\n---\n\n> Aşağıdaki ortak tarif Mac sürümü 1.2.3'ün şartnamesidir; Windows farkları yukarıdadır.\n",
             (W / "docs/SPECS_GIRIS.md").read_text(encoding="utf-8").split("\n", 1)[1],
             f"## Ek A · Kaynak kodu (Windows)\n\nÜretildi: {datetime.now():%d.%m.%Y %H:%M} · kod sürümü: {surum}\n",
             "\n".join(f"- `{p.relative_to(W)}`" for p in liste) + "\n"]
    for p in liste:
        icerik = p.read_text(encoding="utf-8-sig")
        cit = "````" if "```" in icerik else "```"
        parca.append(f"### `{p.relative_to(W)}`\n\n{cit}{DIL.get(p.suffix, '')}\n{icerik.rstrip()}\n{cit}\n")
    hedef = W / "SPECS.md"
    hedef.write_text("\n".join(parca), encoding="utf-8")
    return hedef


def main() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    kok = DIST / AD
    shutil.copytree(W / "app", kok / "app", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    for f in (W / "paket").iterdir():
        shutil.copy(f, kok / f.name)
    shutil.copy(W / "KULLANIM.md", kok / "KULLANIM.md")
    for f in (W / "gelistirme").iterdir():
        shutil.copy(f, kok / f.name)
    (kok / "tests" / "veri").mkdir(parents=True)
    for ad in PAKET_TESTLERI:
        shutil.copy(W / "tests" / ad, kok / "tests" / ad)
    shutil.copy(W / "tests" / "veri" / "sahte_claude.py", kok / "tests" / "veri" / "sahte_claude.py")
    for f in (W / "tests" / "ornek_veri").iterdir():
        shutil.copy(f, kok / "tests" / "veri" / f.name)
    shutil.copy(specs(), kok / "SPECS.md")
    with zipfile.ZipFile(kok / "kanal-studyosu-flow.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted((W / "app/skills/kanal-studyosu-flow").rglob("*")):
            if p.is_file() and not _gec(p):
                z.write(p, p.relative_to(W / "app/skills"))
    zipad = DIST / f"{AD} (Windows).zip"
    with zipfile.ZipFile(zipad, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(kok.rglob("*")):
            if p.is_file() and not _gec(p):
                z.write(p, p.relative_to(DIST))
    print("Paket:", zipad)


if __name__ == "__main__":
    main()
````
