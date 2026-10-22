"""Kurulum klasörü, kanal ekle/doğrula/güncelle/sil, Çöp Kutusu, taslak koruması, içe aktarma, kanal dosyaları, sunucu."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import kanallar as K  # noqa: E402
from kanal_studyosu import yollar  # noqa: E402


class Ortam(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="kanal_studyosu_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.kok, self.cop, self.capcut = self.tmp / "Kurulum", self.tmp / "Cop", self.tmp / "CapCut"
        self.kok.mkdir()
        self.capcut.mkdir()
        eski = {k: os.environ.get(k) for k in ("KANAL_STUDYOSU_KOK", "KANAL_STUDYOSU_COP")}
        os.environ.update(KANAL_STUDYOSU_KOK=str(self.kok), KANAL_STUDYOSU_COP=str(self.cop))
        self.addCleanup(lambda: [os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
                                 for k, v in eski.items()])
        yollar.kur()
        A.ayar_kaydet({"yollar": {"capcut_taslak": str(self.capcut)}})

    def kanal(self, **ek) -> dict:
        veri = {"ad": "Bilim Kahvesi", "kisaltma": "bilim-kahvesi", "kod_oneki": "BK", "dil": {"hedef": "en"}}
        veri.update(ek)
        return K.ekle(veri)["kanal"]


class KurulumTest(Ortam):
    def test_klasorler(self):
        self.assertTrue((self.kok / "Sistem").is_dir())
        self.assertTrue((self.kok / "Kanallar").is_dir())
        self.assertEqual(yollar.kur(), [])  # ikinci açılışta bir şey değişmez
        self.assertEqual(A.ayarlar()["yollar"]["capcut_taslak"], str(self.capcut))
        self.assertTrue((self.kok / "Sistem" / "ayarlar.json").exists())


class EkleTest(Ortam):
    def test_sablondan(self):
        k = self.kanal()
        kl = self.kok / "Kanallar" / "bilim-kahvesi"
        for alt in K.ALT_KLASORLER:
            self.assertTrue((kl / alt).is_dir(), alt)
        j = json.loads((kl / "kanal.json").read_text(encoding="utf-8"))
        self.assertEqual((j["ad"], j["kod_oneki"], j["dil"]["hedef"], j["ses"]["language_code"]), ("Bilim Kahvesi", "BK", "en", "en"))
        self.assertEqual(len(j["kimlik"]), 32)
        for ad in K.PROJE_DOSYALARI:
            metin = (kl / "Proje_dosyalari" / ad).read_text(encoding="utf-8")
            self.assertNotIn("{{", metin)
            self.assertIn("Bilim Kahvesi", metin)
        for a, _ in K.ASAMALAR:
            metin = (kl / "Beceriler" / a / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("{{", metin, a)
            self.assertIn("BK-0X", metin)
        self.assertIn("BK-0X_4_senaryo_en.md", (kl / "Beceriler/ceviri/SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("İngilizce", (kl / "Proje_dosyalari/00_Yonetici.md").read_text(encoding="utf-8"))
        self.assertGreater(sum(d["doldur"] for d in K.dosyalar("bilim-kahvesi")), 0)
        self.assertEqual(K.aktif(), "bilim-kahvesi")  # ilk kanal kendiliğinden seçilir
        self.assertEqual(K.liste()[0]["kod_oneki"], "BK")
        self.assertEqual(json.loads((kl / "taslaklar.json").read_text()), [])
        self.assertTrue(k["onaylar"]["konu"])

    def test_dogrulama(self):
        self.kanal()
        with self.assertRaises(ValueError) as h:
            K.ekle({"ad": "İkinci", "kisaltma": "bilim-kahvesi", "kod_oneki": "bk", "dil": {"hedef": "en"}})
        self.assertIn("kısaltması başka bir kanalda", str(h.exception))
        self.assertIn("öneki", str(h.exception))  # büyük/küçük harf farkı önemsiz
        for veri, parca in (({"kod_oneki": "B K"}, "öneki"), ({"kisaltma": "Büyük Harf"}, "Kısaltma"),
                            ({"dil": {"hedef": "xx"}}, "Hedef dil"), ({"uzunluk": {"kelime_otomatik": False, "hedef_kelime": [2000, 1500]}}, "alt sınır"),
                            ({"montaj": {"maskot": {"dosyalar": ["a.mov"], "sira": ["M1", "M2"]}}}, "Maskot sırası"),
                            ({"montaj": {"altyazi": {"kutu": "beyaz"}}}, "kutu rengi"),
                            ({"gorsel": {"karakter": "Mira"}}, "@ ile"),
                            ({"etiketler": {"senaryo": {"karakter": "A", "metafor": "A", "sema": "B", "ilk30": "C"}}}, "farklı")):
            veri = {"ad": "Yeni", "kisaltma": "yeni", "kod_oneki": "YN", "dil": {"hedef": "de"}, **veri}
            with self.assertRaises(ValueError, msg=veri) as h:
                K.ekle(veri)
            self.assertIn(parca, str(h.exception))
        self.assertFalse((self.kok / "Kanallar" / "yeni").exists())  # yarım klasör kalmaz

    def test_eksikler(self):
        self.kanal()
        e = K.eksikler("bilim-kahvesi")
        self.assertTrue(any(x["zorunlu"] and "voice_id" in x["mesaj"] for x in e))
        self.assertTrue(any("doldurulmamış" in x["mesaj"] for x in e))
        K.guncelle("bilim-kahvesi", {"ses": {"voice_id": "abc123"}, "montaj": {"muzik": False}})
        self.assertFalse(any(x["zorunlu"] for x in K.eksikler("bilim-kahvesi")))


class GuncelleTest(Ortam):
    def test_listeler_ve_kilitler(self):
        self.kanal()
        k, _ = K.guncelle("bilim-kahvesi", {"gorsel": {"yasakli": ["fire"]}, "kisaltma": "baska", "ad": "Bilim K."})
        self.assertEqual(k["gorsel"]["yasakli"], ["fire"])  # liste birleştirilmez, değiştirilir
        self.assertEqual((k["kisaltma"], k["ad"]), ("bilim-kahvesi", "Bilim K."))  # kısaltma değişmez
        K.guncelle("bilim-kahvesi", {"kod_oneki": "bkx"})
        self.assertEqual(K.oku("bilim-kahvesi")["kod_oneki"], "BKX")
        (self.kok / "Kanallar/bilim-kahvesi/Videolar/BKX-01").mkdir()
        for deg in ({"kod_oneki": "ZZ"}, {"dil": {"hedef": "de"}}):
            with self.assertRaises(ValueError):
                K.guncelle("bilim-kahvesi", deg)
        with self.assertRaises(ValueError):
            K.guncelle("bilim-kahvesi", {"ses": {"speed": 3}})


class SilTest(Ortam):
    def test_cop_ve_taslak_korumasi(self):
        k = self.kanal()
        diger = K.ekle({"ad": "Diğer", "kisaltma": "diger", "kod_oneki": "DG", "dil": {"hedef": "it"}})["kanal"]
        for ad in ("BK-01", "BK-02", "BK-03", "ORN-VID-01", "DG-01"):
            (self.capcut / ad).mkdir()
            (self.capcut / ad / "draft_info.json").write_text("{}")
        K.taslak_kaydet("bilim-kahvesi", self.capcut / "BK-01")           # iki iz → gider
        K.taslak_kaydet("bilim-kahvesi", self.capcut / "BK-02")
        (self.capcut / "BK-02" / K.ISARET).unlink()                       # işaret yok → kalır
        A.json_yaz(self.capcut / "BK-03" / K.ISARET, {"kanal_kimlik": k["kimlik"]})  # kayıtta yok → kalır
        K.taslak_kaydet("diger", self.capcut / "DG-01")
        kayit = json.loads((self.kok / "Kanallar/bilim-kahvesi/taslaklar.json").read_text())
        A.json_yaz(self.kok / "Kanallar/bilim-kahvesi/taslaklar.json", kayit + ["DG-01", "ORN-VID-01", "../x"])
        with self.assertRaises(ValueError):
            K.sil("bilim-kahvesi", "yanlış ad")
        s = K.sil("bilim-kahvesi", "  bilim kahvesi ")
        self.assertFalse((self.kok / "Kanallar/bilim-kahvesi").exists())
        self.assertTrue((self.cop / "bilim-kahvesi" / "kanal.json").exists())
        self.assertTrue((self.cop / "BK-01").exists())
        for kalan in ("BK-02", "BK-03", "ORN-VID-01", "DG-01"):
            self.assertTrue((self.capcut / kalan).exists(), kalan)
        self.assertEqual(len(s["tasinan"]), 2)
        self.assertEqual(K.aktif(), "diger")  # silinen seçiliyse başka kanala geçilir
        self.assertEqual(diger["kod_oneki"], "DG")

    def test_suren_uretim(self):
        self.kanal()
        A.json_yaz(yollar.aktif_dosyasi(), {"kanal": "bilim-kahvesi", "uretim": {"kanal": "bilim-kahvesi", "kod": "BK-01"}})
        with self.assertRaises(ValueError):
            K.sil("bilim-kahvesi", "Bilim Kahvesi")
        self.assertTrue((self.kok / "Kanallar/bilim-kahvesi").exists())


class IceAktarTest(Ortam):
    def test_ornek_benzeri(self):
        r = self.tmp / "Örnek"
        for b in ("ornek-konu", "ornek-arastirma", "ornek-senaryo-tr", "ornek-italyanca",
                  "ornek-sahne", "ornek-paketleme", "ornek-video-uretimi"):
            (r / "Kanal/Skill_yedegi" / b).mkdir(parents=True)
            (r / "Kanal/Skill_yedegi" / b / "SKILL.md").write_text(f"# {b}", encoding="utf-8")
        (r / "Kanal/Skill_eski_2ekim/ornek-konu").mkdir(parents=True)
        (r / "Kanal/Skill_eski_2ekim/ornek-konu/SKILL.md").write_text("ESKİ", encoding="utf-8")
        p = r / "Kanal/Proje_dosyalari/ORNEK"
        p.mkdir(parents=True)
        for ad in ("ORN_00_Yonetici.md", "ORN_01_Kanal_Anayasasi.md", "ORN_02_Kanal_Defteri_CURRENT.md", "ORN_03_Aktif_Video.md"):
            (p / ad).write_text(ad, encoding="utf-8")
        (r / "Arsiv/ORN-VID-06").mkdir(parents=True)
        (r / "Arsiv/ORN-VID-06/ORN_02_oncesi_20261001.md").write_text("ESKİ DEFTER", encoding="utf-8")
        (r / "Kanal/Muzik").mkdir()
        (r / "Kanal/Muzik/parca.mp3").write_bytes(b"x")
        (r / "Kanal/Maskot").mkdir()
        (r / "Kanal/Maskot/Maskot_1_seffaf.mov").write_bytes(b"x")
        once = sorted(str(x.relative_to(r)) for x in r.rglob("*"))
        sonuc = K.ekle({"ad": "Örnek (test)", "kisaltma": "ornek-test", "kod_oneki": "TEST-ORN",
                        "dil": {"hedef": "it"}, "test": True}, "klasor", str(r))
        kl = self.kok / "Kanallar/ornek-test"
        self.assertEqual((kl / "Beceriler/konu/SKILL.md").read_text(encoding="utf-8"), "# ornek-konu")
        self.assertEqual((kl / "Beceriler/ceviri/SKILL.md").read_text(encoding="utf-8"), "# ornek-italyanca")
        self.assertEqual((kl / "Beceriler/senaryo/SKILL.md").read_text(encoding="utf-8"), "# ornek-senaryo-tr")
        self.assertEqual((kl / "Proje_dosyalari/02_Defter.md").read_text(encoding="utf-8"), "ORN_02_Kanal_Defteri_CURRENT.md")
        self.assertTrue((kl / "Varliklar/Muzik/parca.mp3").exists())
        self.assertTrue((kl / "Varliklar/Maskot/Maskot_1_seffaf.mov").exists())
        self.assertEqual(len([x for x in sonuc["ice_aktarma"] if x.startswith("Beceri")]), 6)
        self.assertEqual(sorted(str(x.relative_to(r)) for x in r.rglob("*")), once)  # kaynak değişmedi
        self.assertTrue(K.liste()[0]["test"])


class DosyaTest(Ortam):
    def test_duzenle_ve_yedek(self):
        self.kanal()
        K.dosya_yaz("bilim-kahvesi", "01_Anayasa.md", "yeni anayasa")
        self.assertEqual(K.dosya_oku("bilim-kahvesi", "01_Anayasa.md"), "yeni anayasa")
        self.assertEqual(len(list((self.kok / "Kanallar/bilim-kahvesi/.yedek").iterdir())), 1)
        K.dosya_yaz("bilim-kahvesi", "Beceriler/sahne/SKILL.md", "x")
        for kotu in ("../kanal.json", "kanal.json", "Beceriler/../kanal.json", "Beceriler/yok/SKILL.md"):
            with self.assertRaises(ValueError):
                K.dosya_yaz("bilim-kahvesi", kotu, "x")
        with self.assertRaises(ValueError):
            K.klasor("../disari")


class SunucuTest(Ortam):
    def test_uc_noktalar(self):
        from kanal_studyosu import sunucu
        s = sunucu.baslat(0)
        threading.Thread(target=s.serve_forever, daemon=True).start()
        self.addCleanup(s.server_close)
        self.addCleanup(s.shutdown)
        taban = f"http://127.0.0.1:{sunucu.PORT[0]}"

        def istek(yol, govde=None, token=True):
            r = urllib.request.Request(taban + yol, data=None if govde is None else json.dumps(govde).encode(),
                                       headers={"X-App-Token": sunucu.TOKEN if token else "x", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(r) as c:
                    return c.status, json.loads(c.read())
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read())

        self.assertEqual(istek("/api/durum", token=False)[0], 403)
        kod, d = istek("/api/durum")
        self.assertEqual((kod, d["kanallar"], d["aktif"]), (200, [], None))
        kod, j = istek("/api/kanal/ekle", {"kanal": {"ad": "Deneme", "kisaltma": "deneme", "kod_oneki": "DN", "dil": {"hedef": "en"}}})
        self.assertEqual((kod, j["kisaltma"]), (200, "deneme"))
        kod, d = istek("/api/durum")
        self.assertEqual((d["aktif"], d["kanal"]["ayar"]["kod_oneki"]), ("deneme", "DN"))
        kod, j = istek("/api/kanal/dogrula", {"kanal": {"ad": "", "kisaltma": "deneme", "kod_oneki": "DN"}})
        self.assertTrue(any("Kanal adı" in x for x in j["hatalar"]))
        self.assertEqual(istek("/api/kanal/guncelle", {"kisaltma": "deneme", "kanal": {"ad": "Deneme 2"}})[0], 200)
        kod, j = istek("/api/kanal/dosya?kanal=deneme&ad=00_Yonetici.md")
        self.assertIn("Deneme", j["icerik"])
        self.assertEqual(istek("/api/kanal/dosya?kanal=deneme&ad=../kanal.json")[0], 400)
        kod, j = istek("/api/kanal/silinecekler?kanal=deneme")
        self.assertEqual(j["taslaklar"], [])
        self.assertEqual(istek("/api/kanal/sil", {"kisaltma": "deneme", "onay_adi": "Deneme 2"})[0], 200)
        self.assertEqual(istek("/api/durum")[1]["kanallar"], [])


class TekKopyaTest(Ortam):
    def test_acik_kopya(self):
        from kanal_studyosu import sunucu, tek_kopya
        s = sunucu.baslat(0)
        threading.Thread(target=s.serve_forever, daemon=True).start()
        self.addCleanup(s.server_close)
        self.addCleanup(s.shutdown)
        tek_kopya.kaydet(yollar.calisan_dosyasi(), sunucu.PORT[0], sunucu.TOKEN)
        self.assertIsNone(tek_kopya.calisan(yollar.calisan_dosyasi()))  # kendisini saymaz
        d = json.loads(yollar.calisan_dosyasi().read_text())
        d["pid"] = os.getppid()  # yaşayan başka bir süreç (Windows'ta 1 numaralı süreç yok)
        yollar.calisan_dosyasi().write_text(json.dumps(d))
        self.assertIn(f":{sunucu.PORT[0]}/?token=", tek_kopya.calisan(yollar.calisan_dosyasi()))
        yollar.calisan_dosyasi().write_text(json.dumps({"pid": 99999999, "port": 1, "token": "x"}))
        self.assertIsNone(tek_kopya.calisan(yollar.calisan_dosyasi()))


if __name__ == "__main__":
    unittest.main()
