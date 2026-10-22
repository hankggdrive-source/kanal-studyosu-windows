"""Hazır metinle başlama ve üretim başına onay seçimi (Kanal Stüdyosu; gerçek API çağrısı yok)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parite_yardim import SahteIstemci, mesaj  # noqa: E402
from test_genel_kanal import bekle, metin, ortam  # noqa: E402

from kanal_studyosu import asamalar as S  # noqa: E402
from kanal_studyosu import kanal  # noqa: E402
from kanal_studyosu import kontroller as K  # noqa: E402
from kanal_studyosu import metin as M  # noqa: E402
from kanal_studyosu.llm import LLM  # noqa: E402
from kanal_studyosu.uretim import Uretim  # noqa: E402


def duz(t: str) -> str:
    return " ".join(M.govde(p) for p in M.ayir(t).paragraflar)


def cevap(metin_adi: str, govde: str) -> str:
    return ('<dosya ad="BK-01_1_konu_karti.md">KONU KARTI · BK-01 · hazır\nBaşlık: Why we wait</dosya>'
            '<dosya ad="BK-01_1_defter_degisiklikleri.md">A: yeni</dosya>'
            f'<dosya ad="{metin_adi}">{govde}</dosya><ozet>Çakışma kontrolü: yok.</ozet>')


class IngilizceHazirTest(unittest.TestCase):
    def setUp(self):
        ortam(self)

    def test_hedef_dilde_metin_dogrudan_5_asamaya(self):
        en = metin(80, 25, "en")
        ad = "BK-01_4_senaryo_en.md"
        self.assertEqual(S.hazir_diller(), {"tr": "Türkçe", "en": "İngilizce"})
        ist = SahteIstemci([mesaj(cevap(ad, en))] + [mesaj("<ozet>a5</ozet>")] * 3)
        u = Uretim.yeni("BK-01", "", "", LLM(ist), hazir_metin=duz(en), hazir_dil="en", onaylar={"A6": False})
        self.assertEqual(u.sira[:2] if hasattr(u, "sira") else S.sira(u.d)[:2], ["HI", "A5"])
        self.assertEqual(S.gorunum_sirasi(u.d)[:5], ["HI", "A2", "A3", "A4", "A5"])
        self.assertEqual(u.d["onaylar"], {"A2": True, "A4": True, "A6": False})
        u.baslat()
        bekle(u)
        s = u.asama_durumu("HI")
        self.assertEqual(s["durum"], "onay_bekliyor", s.get("hata"))
        self.assertEqual(s["kontrol"]["hatalar"], [])
        sistem = "".join(b["text"] for b in ist.istekler[0]["system"])
        self.assertIn("AŞAMA: HAZIR METİN", sistem)
        self.assertIn("KANAL AYARLARI", sistem)
        self.assertTrue(u.oku(ad).rstrip().endswith("Words: 2000 · Paragraphs: 80"))
        u.onayla("HI")
        aktif = kanal.rit(kanal.AKTIF)
        self.assertIn("KONU KARTI · BK-01", aktif)
        self.assertIn("## ONAYLI FİNAL METİN · İngilizce", aktif)
        self.assertEqual(u.d["adim"], "A5")
        bekle(u)
        self.assertTrue(ist.istekler[1]["messages"][0]["content"].startswith("ONAY 4."))

    def test_degisen_kelime_otomatik_duzeltilir(self):
        tr = metin(80, 21, "tr")
        ad = "BK-01_3_senaryo_tr.md"
        bozuk = tr.replace(M.govde(M.ayir(tr).paragraflar[5]).split()[3], "DEGISTI", 1)
        ist = SahteIstemci([mesaj(cevap(ad, bozuk)), mesaj(f'<dosya ad="{ad}">{tr}</dosya><ozet>ok</ozet>')]
                           + [mesaj("<ozet>a4</ozet>")] * 3)
        u = Uretim.yeni("BK-01", "", "", LLM(ist), hazir_metin=duz(tr), hazir_dil="tr")
        self.assertEqual(S.sira(u.d)[:2], ["HT", "A4"])
        u.baslat()
        bekle(u)
        self.assertIn("Metin değişmiş", ist.istekler[1]["messages"][-1]["content"])
        self.assertEqual(u.asama_durumu("HT")["kontrol"]["hatalar"], [])
        self.assertTrue(u.oku(ad).rstrip().endswith("Kelime: 1680"))
        u.onayla("HT")
        self.assertEqual(u.d["adim"], "A4")

    def test_kontrol(self):
        en = metin(10, 25, "x")
        self.assertEqual(K.hazir_metin(duz(en), en, "en").hatalar, [])
        self.assertTrue(K.hazir_metin(duz(en) + " extra", en, "en").hatalar)
        self.assertTrue(any("hedef 1.950–2.050" in x for x in K.hazir_metin(duz(en), en, "en").uyarilar))
        with self.assertRaises(ValueError):
            Uretim.yeni("BK-01", "", "", LLM(SahteIstemci([])), hazir_metin="x", hazir_dil="it")


class TurkceKanalHazirTest(unittest.TestCase):
    def setUp(self):
        ortam(self, dil={"hedef": "tr"}, ses={"language_code": "tr"})

    def test_turkce_kanalda_tek_dil_ve_final(self):
        self.assertEqual(S.hazir_diller(), {"tr": "Türkçe"})
        tr = metin(80, 21, "tr")
        ist = SahteIstemci([mesaj(cevap("BK-01_3_senaryo_tr.md", tr))] + [mesaj("<ozet>a5</ozet>")] * 3)
        u = Uretim.yeni("BK-01", "", "", LLM(ist), hazir_metin=duz(tr), hazir_dil="tr")
        self.assertEqual(S.sira(u.d)[:2], ["HT", "A5"])
        self.assertEqual(S.gorunum_sirasi(u.d)[:4], ["HT", "A2", "A3", "A5"])
        u.baslat()
        bekle(u)
        u.onayla("HT")
        self.assertIn("## ONAYLI FİNAL METİN · Türkçe", kanal.rit(kanal.AKTIF))
        self.assertEqual(u.d["adim"], "A5")


class SunucuHazirTest(unittest.TestCase):
    def setUp(self):
        ortam(self)

    def test_durum_alanlari_ve_test_kanali_yok(self):
        from kanal_studyosu import sunucu
        d = sunucu.genel_durum()["kanal"]
        self.assertEqual([o["kimlik"] for o in d["onay_secilebilir"]], ["A2", "A4", "A6"])
        self.assertEqual(d["onaylar"], {"A2": True, "A4": True, "A6": True})
        self.assertIn("en", d["hazir_diller"])
        from kanal_studyosu import kanallar
        self.assertFalse(hasattr(kanallar, "ornek_test_ekle"))


if __name__ == "__main__":
    unittest.main()
