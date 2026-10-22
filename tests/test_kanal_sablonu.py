"""Yeni kanal dosyası (şablon → kanal ayarı + anayasa) ve kelime sayısının süreden hesaplanması."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import kanal_sablonu as KS  # noqa: E402
from kanal_studyosu import kanallar as K  # noqa: E402
from kanal_studyosu import yollar  # noqa: E402


def ortam(test) -> Path:
    kok = Path(tempfile.mkdtemp(prefix="kanal_sablon_"))
    test.addCleanup(shutil.rmtree, kok, True)
    eski = {k: os.environ.get(k) for k in ("KANAL_STUDYOSU_KOK", "KANAL_STUDYOSU_COP")}
    os.environ.update(KANAL_STUDYOSU_KOK=str(kok / "Kurulum"), KANAL_STUDYOSU_COP=str(kok / "Cop"))
    test.addCleanup(lambda: [os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
                             for k, v in eski.items()])
    yollar.kur()
    return kok


def doldur(sablon: str, degerler: dict[str, str]) -> str:
    for etiket, deger in degerler.items():
        assert f"\n{etiket}: \n" in sablon, etiket
        sablon = sablon.replace(f"\n{etiket}: \n", f"\n{etiket}: {deger}\n")
    return sablon


class SablonTest(unittest.TestCase):
    def setUp(self):
        ortam(self)

    def test_sablon_dosyasi_ve_bolumler(self):
        KS.sablon_dosyasi_yaz()
        yol = yollar.kok() / KS.DOSYA_ADI
        metin = yol.read_text(encoding="utf-8")
        self.assertIn(KS.A_BASLIK, metin)
        self.assertIn(KS.B_BASLIK, metin)
        for etiket, *_ in KS.ALANLAR:
            self.assertIn(f"\n{etiket}: \n", metin)
        self.assertIn("## 1. Kimlik", metin)
        self.assertIn("## 13. Konu ve format kaynağı", metin)
        self.assertNotIn("Nasıl doldurulur", metin.split(KS.B_BASLIK)[1])
        yol.write_text("kullanıcının notu", encoding="utf-8")
        KS.sablon_dosyasi_yaz()  # var olan dosyaya dokunulmaz
        self.assertEqual(yol.read_text(encoding="utf-8"), "kullanıcının notu")

    def test_bos_sablon_zorunlulari_ister(self):
        r = KS.oku(KS.sablon_metni())
        self.assertEqual({e["yol"] for e in r["eksik"]}, {"ad", "dil.hedef", "uzunluk.hedef_dk"})
        self.assertFalse(any("Kısaltma" in h or "öneki" in h for h in r["hatalar"]))  # ad yokken tekrar edilmez
        with self.assertRaises(ValueError):
            KS.oku("   ")
        with self.assertRaises(ValueError):
            KS.oku("Merhaba, bu bir kanal dosyası değil.")

    def test_doldurulmus_dosya_okunur_ve_kanal_eklenir(self):
        K.ekle({"ad": "Bilim Kahvesi", "kisaltma": "bilim-kahvesi", "kod_oneki": "BK", "dil": {"hedef": "en"}})
        metin = doldur(KS.sablon_metni(), {
            "Kanal adı": "Bilim Kahvesi", "Video dili": "İtalyanca (it)", "Video süresi (dakika)": "10 dakika",
            "Görsel oranı": "dikey 9:16", "Flow karakter etiketi": "@Mira (kısa saçlı kadın)",
            "Karakter sahnesi etiketi": "[mira]", "Görsel kurallar": "Yazı yok.",
            "Ek yasaklı görsel kelimeler": "Gun, smoke", "Hassas kelimeler": "ansia, depress",
            "Seslendirme tonu tag'leri": "Calm, Warm", "Altyazı yazı rengi": "#1a2b3c",
            "Altyazı kutu rengi": "beyaz", "Kapanış imzası": "—"})
        metin = metin.replace("Görsel kurallar: Yazı yok.\n", "**Görsel kurallar:** Yazı yok.\nÇocuk figürü yok.\n")
        metin = metin.replace("⟦DOLDUR: YouTube adresi, slogan⟧", "youtube.com/@bk · Ogni giorno un perché")
        metin = "```markdown\n" + metin + "\n```"  # yapay zeka kod bloğuna sarmış olabilir
        r = KS.oku(metin)
        k = r["kanal"]
        self.assertEqual((k["ad"], k["dil"]["hedef"], k["uzunluk"]["hedef_dk"], k["gorsel"]["oran"]),
                         ("Bilim Kahvesi", "it", 10, "9:16"))
        self.assertEqual((k["kisaltma"], k["kod_oneki"]), ("bilim-kahvesi-2", "BK2"))  # var olanla çakışmaz
        self.assertEqual(k["gorsel"]["karakter"], "@Mira")
        self.assertEqual(k["etiketler"]["senaryo"]["karakter"], "MIRA")
        self.assertEqual(k["gorsel"]["kurallar"], "Yazı yok.\nÇocuk figürü yok.")
        self.assertIn("child", k["gorsel"]["yasakli"])  # genel liste korunur
        self.assertEqual(k["gorsel"]["yasakli"][-2:], ["gun", "smoke"])
        self.assertEqual(k["hassas_kelimeler"], ["ansia", "depress"])
        self.assertEqual(k["etiketler"]["ses"], ["calm", "warm"])
        self.assertEqual(k["montaj"]["altyazi"]["yazi"], "#1A2B3C")
        self.assertEqual(k["montaj"]["altyazi"]["kutu"], K.varsayilan()["montaj"]["altyazi"]["kutu"])
        self.assertEqual(k["imza"], "")
        self.assertEqual(k["ses"]["language_code"], "it")
        self.assertEqual([e["yol"] for e in r["eksik"]], ["montaj.altyazi.kutu"])
        self.assertEqual(r["hatalar"], [])
        self.assertTrue(r["anayasa"].startswith("## 1. Kimlik"))
        self.assertGreater(r["doldur"], 0)
        self.assertTrue(any("doldurulmamış" in u for u in r["uyarilar"]))
        sonuc = K.ekle(k, "sablon", "", r["anayasa"])
        self.assertIn("Anayasa: yeni kanal dosyasından", sonuc["ice_aktarma"])
        anayasa = (K.klasor("bilim-kahvesi-2") / "Proje_dosyalari" / "01_Anayasa.md").read_text(encoding="utf-8")
        self.assertTrue(anayasa.startswith("# 01 · KANAL ANAYASASI — Bilim Kahvesi\n"))
        self.assertIn("- **Kanal:** Bilim Kahvesi · youtube.com/@bk · Ogni giorno un perché", anayasa)
        self.assertIn("Bütün yayın çıktıları İtalyanca", anayasa)
        self.assertNotIn("{{", anayasa)
        self.assertNotIn("Nasıl doldurulur", anayasa)
        self.assertTrue(K.oku("bilim-kahvesi-2")["uzunluk"]["kelime_otomatik"])

    def test_basliklar_kalin_ya_da_madde_isaretli(self):
        metin = ("## A · Kanal bilgileri\n- **Kanal adı:** Deniz Feneri\n* Video dili: English\n"
                 "VIDEO SÜRESİ (DAKİKA): 8\n\n## B · Kanal anayasası\n## 1. Kimlik\n- Kitle: denizciler\n")
        r = KS.oku(metin)
        self.assertEqual(r["eksik"], [])
        self.assertEqual((r["kanal"]["ad"], r["kanal"]["dil"]["hedef"], r["kanal"]["uzunluk"]["hedef_dk"]),
                         ("Deniz Feneri", "en", 8))
        self.assertEqual((r["kanal"]["kisaltma"], r["kanal"]["kod_oneki"]), ("deniz-feneri", "DF"))
        self.assertEqual(r["anayasa"], "## 1. Kimlik\n- Kitle: denizciler")
        r = KS.oku("Kanal adı: X Kanal\nVideo dili: klingon\nVideo süresi (dakika): on iki\nFlow karakter etiketi: "
                   "karakter yok")
        self.assertEqual({e["yol"]: e["neden"].split(":")[0] for e in r["eksik"]},
                         {"dil.hedef": "dil tanınmadı", "uzunluk.hedef_dk": "sayı yok"})
        self.assertEqual(r["kanal"]["gorsel"]["karakter"], "")
        self.assertTrue(any("anayasa bölümü" in u for u in r["uyarilar"]))


class KelimeTest(unittest.TestCase):
    def setUp(self):
        ortam(self)

    def test_sureden_hesaplanir(self):
        k = K.ekle({"ad": "Yeni", "kisaltma": "yeni", "kod_oneki": "YN", "dil": {"hedef": "it"}})["kanal"]
        self.assertTrue(k["uzunluk"]["kelime_otomatik"])
        u = K.oku("yeni")["uzunluk"]
        self.assertEqual((u["calisma_kelime"], u["hedef_kelime"]), ([1620, 1790], [1900, 2100]))  # 12 dk
        K.guncelle("yeni", {"uzunluk": {"hedef_dk": 8}, "ses": {"speed": 1.1}})
        u = K.oku("yeni")["uzunluk"]
        self.assertEqual(u["hedef_kelime"], [1400, 1540])  # 167 × 8 × 1,1 = 1469,6 → ±%5 (hızlı ses: daha çok kelime)
        K.guncelle("yeni", {"uzunluk": {"kelime_otomatik": False, "hedef_kelime": [1000, 1100]}})
        self.assertEqual(K.oku("yeni")["uzunluk"]["hedef_kelime"], [1000, 1100])

    def test_eski_kanal_elle_kalir(self):
        K.ekle({"ad": "Eski", "kisaltma": "eski", "kod_oneki": "ES", "dil": {"hedef": "it"}})
        yol = K.klasor("eski") / "kanal.json"
        ham = json.loads(yol.read_text(encoding="utf-8"))
        del ham["uzunluk"]["kelime_otomatik"]  # bu sürümden önce açılmış kanal
        ham["uzunluk"].update(calisma_kelime=[1600, 1800], hedef_kelime=[1950, 2050])
        yol.write_text(json.dumps(ham), encoding="utf-8")
        u = K.oku("eski")["uzunluk"]
        self.assertFalse(u["kelime_otomatik"])
        self.assertEqual((u["calisma_kelime"], u["hedef_kelime"]), ([1600, 1800], [1950, 2050]))
        K.guncelle("eski", {"ad": "Eski Kanal"})
        self.assertEqual(K.oku("eski")["uzunluk"]["hedef_kelime"], [1950, 2050])

    def test_gercek_ses_suresinden_ogrenir(self):
        K.ekle({"ad": "Ders", "kisaltma": "ders", "kod_oneki": "DR", "dil": {"hedef": "en"}, "uzunluk": {"hedef_dk": 10}})
        self.assertEqual(K.oku("ders")["uzunluk"]["hedef_kelime"], [1470, 1630])  # 155 kelime/dk
        self.assertEqual(round(K.hiz_kaydet("ders", "DR-01", "en", 1300, 600)), 130)
        self.assertEqual(round(K.hiz_kaydet("ders", "DR-02", "en", 1500, 600, 1.25)), 120)  # hız 1,25'e göre düzeltilir
        self.assertIsNone(K.hiz_kaydet("ders", "DR-03", "en", 3000, 600))  # dakikada 300: akla yatkın değil
        self.assertIsNone(K.hiz_kaydet("ders", "DR-03", "en", 30, 10))
        K.hiz_kaydet("ders", "DR-01", "en", 1400, 600)  # aynı video yeniden ölçülünce eskisinin yerine
        olcum = K.oku("ders")["uzunluk"]["hiz_olcum"]["en"]
        self.assertEqual([x["kod"] for x in olcum], ["DR-02", "DR-01"])
        self.assertEqual(K.konusma_hizi(K.oku("ders"), "en"), (130, 2))  # ortanca (120, 140)
        self.assertEqual(K.oku("ders")["uzunluk"]["hedef_kelime"], [1240, 1370])
        self.assertEqual(K.oku("ders")["uzunluk"]["calisma_kelime"], [1350, 1490])  # Türkçe ölçüm yok: ortalama
        for i in range(10):
            K.hiz_kaydet("ders", f"DR-{10 + i}", "en", 1500, 600)
        self.assertEqual(len(K.oku("ders")["uzunluk"]["hiz_olcum"]["en"]), K.HIZ_OLCUM_SAYISI)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg gerekli")
class SesOlcumuTest(unittest.TestCase):
    def test_sahne_sesleri_ve_duraklar(self):
        from parite_yardim import gecici_ortam
        from test_parite_ses import _SahteAPI, _ses
        from kanal_studyosu import studio_baglanti as ST
        r = gecici_ortam(self)
        cp = r.parent / "Creator Projects"
        cp.mkdir()
        A.ayar_kaydet({"yollar": {"creator_projects": str(cp)}})
        cid, vid = ST.video_bul_ya_da_olustur("ORN-VID-06", "ORN-VID-06 Prova", None)
        ST.metin_ver(cid, vid, "[calm] Uno due tre quattro.\n\nCinque sei sette.\n\nOtto, nove: dieci!", 3)
        self.assertIsNone(ST.ses_olcumu(vid))  # ses yokken ölçüm yok
        ST.seslendir(vid, lambda m: None, api=_SahteAPI(_ses(r.parent / "a.mp3", 2.0)))
        kelime, sure = ST.ses_olcumu(vid)
        self.assertEqual(kelime, 10)  # [calm] sayılmaz
        self.assertAlmostEqual(sure, 3 * (2.0 + 0.4), delta=0.3)


if __name__ == "__main__":
    unittest.main()
