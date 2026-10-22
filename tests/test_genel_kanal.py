"""Örnek dışındaki kanallar: hedef dil Türkçe (4. aşama yok), İngilizce, maskotsuz/karaktersiz, onayı kapalı aşama."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parite_yardim import SahteIstemci, mesaj  # noqa: E402

from kanal_studyosu import araclar  # noqa: E402
from kanal_studyosu import asamalar as S  # noqa: E402
from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import kanal, kanallar, yollar  # noqa: E402
from kanal_studyosu import kontroller as K  # noqa: E402
from kanal_studyosu.llm import LLM  # noqa: E402
from kanal_studyosu.uretim import Uretim  # noqa: E402


def ortam(test, **kanal_ayari) -> Path:
    kok = Path(tempfile.mkdtemp(prefix="kanal_genel_"))
    test.addCleanup(shutil.rmtree, kok, True)
    eski = {k: os.environ.get(k) for k in ("KANAL_STUDYOSU_KOK", "KANAL_STUDYOSU_COP")}
    os.environ.update(KANAL_STUDYOSU_KOK=str(kok / "Kurulum"), KANAL_STUDYOSU_COP=str(kok / "Cop"))
    test.addCleanup(lambda: [os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
                             for k, v in eski.items()])
    yollar.kur()
    (kok / "CapCut").mkdir()
    A.ayar_kaydet({"yollar": {"capcut_taslak": str(kok / "CapCut")}})
    veri = {"ad": "Bilim Kahvesi", "kisaltma": "bilim", "kod_oneki": "BK", "dil": {"hedef": "en"},
            "ses": {"voice_id": "v1", "voice_name": "Anna"}, "uzunluk": {"kelime_otomatik": False},
            "etiketler": {"senaryo": {"karakter": "MILA", "metafor": "SEMBOL", "sema": "SEMA", "ilk30": "ILK30"},
                          "ses": ["calm", "excited"], "ses_sinir": {"excited": 1}, "tag_orani": 30}}
    veri = A.birlestir(veri, kanal_ayari)
    kanallar.ekle(veri)
    return kanallar.klasor(veri["kisaltma"])


def metin(n: int, k: int, on: str) -> str:
    """n paragraf, her biri k kelime; birbirine benzemeyen kelimeler (çift paragraf kontrolüne takılmaz)."""
    import random
    hece = ["ka", "lo", "mi", "ter", "su", "na", "vel", "do", "ri", "pa", "zen", "ul", "ko", "fi", "bar", "es"]
    return "\n\n".join("[MILA] " + " ".join("".join(random.Random(f"{on}{i}-{j}").choices(hece, k=3)) for j in range(k))
                       for i in range(n))


def bekle(u, sure=20):
    son = time.time() + sure
    time.sleep(0.1)
    while u.calisiyor() and time.time() < son:
        time.sleep(0.05)


class IngilizceKanalTest(unittest.TestCase):
    def setUp(self):
        self.k = ortam(self, gorsel={"karakter": "@Mila"})

    def test_kod_ve_ayarlar_blogu(self):
        self.assertEqual(kanal.siradaki_kod(), "BK-01")
        self.assertTrue(kanal.KOD.match("BK-07"))
        self.assertFalse(kanal.KOD.match("ORN-VID-07"))
        self.assertEqual(S.sira()[:5], ["A1", "A2", "A3", "A4", "A5"])
        self.assertEqual(S.ASAMALAR["A4"].ciktilar("BK-01"), ["BK-01_4_senaryo_en.md"])
        self.assertEqual(S.adim_adlari()["A4"], "4 · İngilizce")
        blok = kanal.ayarlar_blogu()
        for parca in ("BK-0X", "İngilizce", "[MILA]", "[SEMBOL]", "[excited] en fazla 1", "%30", "@Mila", "maskot yok"):
            self.assertIn(parca, blok)
        self.assertIn("Metinde geçerli etiketler yalnız [MILA] [SEMBOL] [SEMA] [ILK30]", S.cerceve())

    def test_kontroller_kanal_ayarindan(self):
        tr = metin(80, 21, "tr") + "\n\nKelime: 1680"
        self.assertTrue(K.senaryo_tr(tr).temiz, K.senaryo_tr(tr).hatalar)
        en = metin(80, 25, "en")
        s = K.senaryo_it(tr, en + "\n\nWords: 2000 · Paragraphs: 80\nHook puanı: 9/10")
        self.assertTrue(s.temiz, s.hatalar)
        s = K.senaryo_it(tr, en)
        self.assertTrue(any("Teslim satırları" in h for h in s.hatalar))
        self.assertTrue(any("[MIRA]" in u for u in K.senaryo_tr("[MIRA] x\n\nKelime: 1").uyarilar))
        # seslendirme tag'leri kanal ayarından
        self.assertEqual(K.elevenlabs_metni("[calm] a\n\n[excited] b"), [])
        self.assertTrue(K.elevenlabs_metni("[excited] a\n\n[excited] b"))
        self.assertTrue(K.elevenlabs_metni("[warm] a"))  # Örnek tag'i bu kanalda izinsiz

    def test_sahne_paketi_karakter_ve_kanal_etiketi(self):
        a = "[calm] Hello there.\n\nSecond line.\n\nThird line.\n\nFourth line."
        b = "@Mila sits by the window, calm, flat 2D, no text\n\nA cup on a table, @Mila nearby, no text\n\n" \
            "A lamp, no text\n\nA door, no text"
        tsv = "sahne\tbolum\trol\tduygu\thareket\todak\tefekt\tsonraki_gecis\tmaskot\tgerekce\n" + "\n".join(
            f"000{i}\t§1\tanlatim\tsakin\tNEFES\tx\t-\tKES\t-\tx" for i in range(1, 5))
        s = K.sahne_paketi(a, b, "", tsv, "[MILA] Hello there.\n\n[MILA] Second line.\n\n[MILA] Third line.\n\n[MILA] Fourth line.")
        self.assertTrue(s.temiz, s.hatalar)
        self.assertTrue(any("@Mila promptun başında değil: 0002" in x for x in s.uyarilar))
        s = K.paket("DEFTER KAYDI · BK-01\n#BilimKahvesi #a #b #c #d")
        self.assertEqual(s.uyarilar, [])
        self.assertTrue(any("#BilimKahvesi" in x for x in K.paket("DEFTER KAYDI\n#a #b #c #d #e").uyarilar))

    def test_plan_kontrol_maskotsuz_ve_hassas_bos(self):
        satirlar = ["sahne\tbolum\trol\tduygu\thareket\todak\tefekt\tsonraki_gecis\tmaskot\tgerekce"]
        satirlar += [f"{i:04d}\t§1\tanlatim\tx\t{'NEFES' if i % 2 else 'YAKINLAS'}\tx\t-\t{'KES' if i < 10 else '-'}\t-\tx"
                     for i in range(1, 11)]
        p = self.k / "plan.tsv"
        p.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
        pk = araclar.plan_kontrol(str(p), 10)
        self.assertTrue(pk["temiz"])
        self.assertEqual(pk["maskot"], "")  # maskotsuz kanal: alt satırdaki "TEMIZ []" maskot sanılmaz
        from kanal_studyosu.capcut_zinciri import maskot_argumanlari
        self.assertEqual(maskot_argumanlari("TEMIZ []"), [])  # eski sürümün hatalı kaydı da betiğe gitmez
        self.assertEqual(maskot_argumanlari("--maskot 10:1:2 --maskot 30:2:2"), ["--maskot", "10:1:2", "--maskot", "30:2:2"])
        satirlar[3] = satirlar[3].replace("\t-\tx", "\tM1\tx")
        p.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
        pk = araclar.plan_kontrol(str(p), 10)
        self.assertFalse(pk["temiz"])
        self.assertTrue(any("maskot yok" in h for h in pk["hatalar"]))
        v = kanal.video_klasoru("BK-01")
        v.mkdir(parents=True)
        (v / "04_Paketleme_ve_Veo3.md").write_text("# BK-01\n\nTrauma and depression\n", encoding="utf-8")
        (v / "02_ElevenLabs_seslendirme_metni.txt").write_text("Trauma.\n", encoding="utf-8")
        self.assertTrue(araclar.hassas_kelime("BK-01")["temiz"])  # liste boş: kanalda hassas kelime tanımlı değil


class TurkceKanalTest(unittest.TestCase):
    """Hedef dil Türkçe: 4. aşama yok, Türkçe senaryo finaldir."""

    def setUp(self):
        self.k = ortam(self, dil={"hedef": "tr"}, ses={"language_code": "tr"})

    def test_a4_atlanir_ve_final_tr(self):
        self.assertNotIn("A4", S.sira())
        self.assertEqual(S.final_dosya("BK-01"), "BK-01_3_senaryo_tr.md")
        self.assertIn("4. aşama yoktur", kanal.ayarlar_blogu())
        u = Uretim.yeni("BK-01", "", "", LLM(SahteIstemci([])))
        self.assertNotIn("A4", u.d["asamalar"])
        u.d["adim"] = "A3"
        for k in ("A1", "A2"):
            u.d["asamalar"][k]["durum"] = "tamam"
        tr = metin(80, 21, "tr") + "\n\nKelime: 1680"
        u._yaz("BK-01_3_senaryo_tr.md", tr)
        kanal.rit03_yenile("BK-01", S.rit03_kart_ile("BK-01", "KONU KARTI · BK-01 · x", "02.10.2026"))
        u.d["asamalar"]["A3"]["durum"] = "onay_bekliyor"
        u.kaydet()
        sonraki = u._tamamla("A3")
        self.assertEqual(sonraki, "A5")
        aktif = kanal.rit(kanal.AKTIF)
        self.assertIn("## ONAYLI FİNAL METİN · Türkçe", aktif)
        self.assertIn("ONAY 1 ve ONAY 3 verildi", aktif)
        mesaj_ = S.ilk_mesaj(S.ASAMALAR["A5"], "BK-01", u.oku, {"onay_notlari": {}})
        self.assertTrue(mesaj_.startswith("ONAY 3."))


class OnayKapaliTest(unittest.TestCase):
    def setUp(self):
        self.k = ortam(self, onaylar={"konu": False, "arastirma": False})

    def test_kontroller_temizse_onaysiz_gecer(self):
        self.assertTrue(S.onay_gerekli(S.ASAMALAR["A1"]))  # ONAY 1 kapatılamaz (kanal ayarında kapalı olsa da)
        self.assertFalse(S.onay_gerekli(S.ASAMALAR["A2"]))
        self.assertTrue(S.onay_gerekli(S.ASAMALAR["A2"], {"onaylar": {"A2": True}}))  # üretim seçimi üstün
        kart = "KONU KARTI · BK-01 · deneme\nBaşlık: Why we wait (13 kr)"
        ist = SahteIstemci([
            mesaj(f'<dosya ad="BK-01_1_konu_karti.md">{kart}</dosya><dosya ad="BK-01_1_defter_degisiklikleri.md">A: '
                  f'yeni</dosya><ozet>tamam</ozet>'),
            mesaj('<dosya ad="BK-01_2_arastirma_outline.md">OUTLINE\n§1</dosya><ozet>araştırma</ozet>')]
            + [mesaj("<ozet>x</ozet>")] * 3)
        u = Uretim.yeni("BK-01", "", "", LLM(ist))
        u.baslat("A1")
        bekle(u)
        self.assertEqual(u.asama_durumu("A1")["durum"], "onay_bekliyor")
        u.onayla("A1")
        bekle(u)
        self.assertEqual(u.asama_durumu("A2")["durum"], "tamam")
        self.assertEqual(u.d["adim"], "A3")
        self.assertIn("ONAY 2.", ist.istekler[2]["messages"][0]["content"])


class SunucuUretimTest(unittest.TestCase):
    def setUp(self):
        self.k = ortam(self)

    def test_durum_kanala_gore(self):
        from kanal_studyosu import sunucu
        d = sunucu.genel_durum()
        self.assertEqual(d["kanal"]["siradaki"], "BK-01")
        self.assertEqual([a["kimlik"] for a in d["kanal"]["asamalar"]][:4], ["A1", "A2", "A3", "A4"])
        self.assertEqual(d["kanal"]["asamalar"][3]["ad"], "4 · İngilizce")
        self.assertIsNone(d["uretim"])
        self.assertEqual(A.ayarlar()["ses"]["voice_id"], "v1")  # üretim kodu kanal sesini görür
        self.assertEqual(A.ayarlar()["isler"]["A3"]["model"], kanal.ayar()["isler"]["senaryo"]["model"])


if __name__ == "__main__":
    unittest.main()
