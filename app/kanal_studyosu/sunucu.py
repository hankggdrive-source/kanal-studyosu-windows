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
