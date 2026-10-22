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
