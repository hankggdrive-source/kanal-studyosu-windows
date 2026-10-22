"""Claude Code (abonelik) yazım servisi: sahte `claude` komutuyla (gerçek çağrı yok)."""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parite_yardim import VERI, gecici_ortam  # noqa: E402

from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import claude_code as CC  # noqa: E402
from kanal_studyosu import maliyet  # noqa: E402
from kanal_studyosu.llm import LLM, Durduruldu, LLMHatasi  # noqa: E402

KOD = "ORN-VID-06"


class SahteClaude:
    def __init__(self, test, cevaplar, senaryo="normal"):
        d = Path(os.environ["KANAL_STUDYOSU_KOK"]).parent
        self.kayit, self.sayac, self.cevaplar = d / "claude_kayit.jsonl", d / "claude_sayac", d / "claude_cevap.json"
        for f in (self.kayit, self.sayac):
            f.unlink(missing_ok=True)
        self.cevaplar.write_text(json.dumps(cevaplar, ensure_ascii=False), encoding="utf-8")
        komut = VERI / "sahte_claude.py"
        if sys.platform == "win32":  # Windows'ta .py doğrudan çalışmaz: npm kurulumundaki gibi bir claude.cmd sarmalayıcı
            komut = d / "claude.cmd"
            # cmd.exe .cmd dosyasını konsolun eski kod sayfasıyla okur; yolda ü gibi harf varsa (ör. "Kanal Stüdyosu"
            # klasörü) dosya o kod sayfasıyla yazılmalı. (npm'in gerçek claude.cmd'si yol yazmaz, %~dp0 kullanır.)
            import ctypes
            komut.write_text(f'@"{sys.executable}" "{VERI / "sahte_claude.py"}" %*\r\n',
                             encoding=f"cp{ctypes.windll.kernel32.GetOEMCP()}")
        yeni = {"KANAL_STUDYOSU_CLAUDE": str(komut), "SAHTE_KAYIT": str(self.kayit),
                "SAHTE_SAYAC": str(self.sayac), "SAHTE_CEVAPLAR": str(self.cevaplar), "SAHTE_SENARYO": senaryo,
                "ANTHROPIC_API_KEY": "sk-ant-gizli"}
        eski = {k: os.environ.get(k) for k in yeni}
        os.environ.update(yeni)
        test.addCleanup(lambda: [os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
                                 for k, v in eski.items()])
        CC._ATILAN_BAYRAKLAR.clear()
        test.addCleanup(CC._ATILAN_BAYRAKLAR.clear)

    def cagrilar(self) -> list[dict]:
        return [json.loads(s) for s in self.kayit.read_text(encoding="utf-8").splitlines()] if self.kayit.exists() else []


def deger(argv, bayrak):
    return argv[argv.index(bayrak) + 1]


class ClaudeCodeTest(unittest.TestCase):
    def setUp(self):
        gecici_ortam(self)
        self.assertEqual(A.ayarlar()["saglayici"], "claude_code")  # varsayılan servis

    def test_istek_bayraklar_ve_maliyet(self):
        s = SahteClaude(self, ["<ozet>tamam</ozet>"])
        sayilan = []
        c = LLM().istek("A1", KOD, ["SISTEM METNI"], [{"role": "user", "content": "Konu kartını yaz."}],
                        ilerleme=sayilan.append)
        self.assertEqual(c.metin, "<ozet>tamam</ozet>")
        self.assertEqual(c.usd, 0.0)
        self.assertEqual(c.icerik[0]["oturum"], "oturum-1")
        cagri = s.cagrilar()[0]
        a = cagri["argv"]
        self.assertIsNone(cagri["api_key"])                       # API anahtarı ortamdan çıkarıldı → abonelik
        self.assertEqual(deger(a, "--model"), A.ayarlar()["isler"]["A1"]["model"])
        self.assertEqual(deger(a, "--tools"), "WebSearch")         # A1 web aramalı
        self.assertIn("--safe-mode", a)
        self.assertIn("--strict-mcp-config", a)
        self.assertNotIn("--resume", a)
        self.assertTrue(cagri["cwd"].replace("\\", "/").endswith("Sistem/claude_code"))
        girdi = json.loads(cagri["stdin"])
        self.assertEqual(girdi["message"]["content"], [{"type": "text", "text": "Konu kartını yaz."}])
        self.assertTrue(sayilan)
        satir = maliyet.satirlar()[-1]
        self.assertTrue(satir["abonelik"])
        self.assertEqual(satir["usd"], 0.0)
        self.assertEqual(satir["tahmini_usd"], 0.42)
        self.assertEqual(satir["web_search_requests"], 2)
        o = maliyet.ozet(KOD)
        self.assertEqual(o["video_usd"], 0)
        self.assertTrue(o["abonelik"])
        self.assertIn("abonelik", maliyet.dokum(KOD))

    def test_aracsiz_is_ve_gorsel(self):
        s = SahteClaude(self, ['{"0001": [0.5, 0.4]}'])
        mesaj = [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "QUJD"}},
            {"type": "text", "text": "odak"}]}]
        LLM().istek("odak", KOD, [], mesaj)
        a = s.cagrilar()[0]["argv"]
        self.assertEqual(deger(a, "--tools"), "")
        self.assertNotIn("--effort", a)  # Haiku'da efor yok
        icerik = json.loads(s.cagrilar()[0]["stdin"])["message"]["content"]
        self.assertEqual(icerik[0]["type"], "image")

    def test_duzeltme_turunda_oturum_surdurulur(self):
        from kanal_studyosu.uretim import Uretim
        kart = "KONU KARTI · ORN-VID-06 · deneme\nBaşlık: Neden bekleriz"
        s = SahteClaude(self, [
            f'<dosya ad="{KOD}_1_konu_karti.md">{kart}</dosya><dosya ad="{KOD}_1_defter_degisiklikleri.md">A: yeni</dosya><ozet>ilk</ozet>',
            f'<dosya ad="{KOD}_1_konu_karti.md">{kart} (kısa)</dosya><ozet>düzeltildi</ozet>'])
        u = Uretim.yeni(KOD, "", "", LLM())
        u.baslat("A1")
        _bekle(u)
        self.assertEqual(u.asama_durumu("A1")["durum"], "onay_bekliyor", u.asama_durumu("A1").get("hata"))
        u.duzeltme_iste("A1", "Başlık daha kısa olsun.")
        _bekle(u)
        c1, c2 = s.cagrilar()
        self.assertNotIn("--resume", c1["argv"])
        self.assertEqual(deger(c2["argv"], "--resume"), "oturum-1")
        gonderilen = json.loads(c2["stdin"])["message"]["content"]
        self.assertEqual(len(gonderilen), 1)
        self.assertIn("Başlık daha kısa olsun.", gonderilen[0]["text"])
        self.assertIn("(kısa)", u.oku(f"{KOD}_1_konu_karti.md"))

    def test_servis_degisince_gecmis_metin_olarak_verilir(self):
        s = SahteClaude(self, ["<ozet>ok</ozet>"])
        mesajlar = [{"role": "user", "content": "ilk"}, {"role": "assistant", "content": [{"type": "text", "text": "eski"}]},
                    {"role": "user", "content": "düzelt"}]
        LLM().istek("A2", KOD, ["s"], mesajlar)
        icerik = json.loads(s.cagrilar()[0]["stdin"])["message"]["content"]
        self.assertIn("eski", icerik[0]["text"])
        self.assertEqual(icerik[-1]["text"], "düzelt")
        self.assertNotIn("--resume", s.cagrilar()[0]["argv"])

    def test_sinir_ve_giris_hatalari(self):
        SahteClaude(self, ["x"], "sinir")
        with self.assertRaises(LLMHatasi) as h:
            LLM().istek("A3", KOD, ["s"], [{"role": "user", "content": "yaz"}])
        self.assertIn("kullanım sınırına ulaşıldı", str(h.exception))
        self.assertIn("5pm", str(h.exception))
        SahteClaude(self, ["x"], "giris")
        with self.assertRaises(LLMHatasi) as h:
            LLM().istek("A3", KOD, ["s"], [{"role": "user", "content": "yaz"}])
        self.assertIn("/login", str(h.exception))

    def test_taninmayan_bayrak_atilir(self):
        s = SahteClaude(self, ["<ozet>ok</ozet>"], "bayrak")
        c = LLM().istek("A3", KOD, ["s"], [{"role": "user", "content": "yaz"}])
        self.assertEqual(c.metin, "<ozet>ok</ozet>")
        cagrilar = s.cagrilar()
        self.assertIn("--effort", cagrilar[0]["argv"])
        self.assertNotIn("--effort", cagrilar[1]["argv"])

    def test_durdur(self):
        SahteClaude(self, ["x"], "yavas")
        dur = threading.Event()
        threading.Timer(0.5, dur.set).start()
        t0 = time.time()
        with self.assertRaises(Durduruldu):
            LLM().istek("A3", KOD, ["s"], [{"role": "user", "content": "yaz"}], iptal=dur.is_set)
        self.assertLess(time.time() - t0, 10)

    def test_bulunamazsa_ve_durum(self):
        SahteClaude(self, ["x"])
        ok, mesaj = CC.durum()
        self.assertTrue(ok, mesaj)
        self.assertIn("abonelikle giriş yapılmış", mesaj)
        os.environ["SAHTE_AUTH"] = "api_key"
        self.addCleanup(os.environ.pop, "SAHTE_AUTH", None)
        self.assertIn("API", CC.durum()[1])
        os.environ["KANAL_STUDYOSU_CLAUDE"] = "/yok/claude"
        with self.assertRaises(LLMHatasi):
            LLM().istek("A3", KOD, ["s"], [{"role": "user", "content": "yaz"}])

    def test_onkontrol_ve_ayarlar(self):
        SahteClaude(self, ["x"])
        from kanal_studyosu import onkontrol
        m = {x["ad"]: x for x in onkontrol.calistir()["maddeler"]}
        self.assertTrue(m["Yazım servisi: Claude Code (abonelik)"]["tamam"])
        self.assertNotIn("anthropic", A.ANAHTARLAR)
        with self.assertRaises(ValueError):
            A.ayar_kaydet({"saglayici": "anthropic"})
        A.ayar_kaydet({"saglayici": "openrouter"})
        m = {x["ad"]: x for x in onkontrol.calistir()["maddeler"]}
        self.assertIn("Yazım servisi: OpenRouter", m)


def _bekle(u, sure=15):
    son = time.time() + sure
    time.sleep(0.1)
    while u.calisiyor() and time.time() < son:
        time.sleep(0.05)


if __name__ == "__main__":
    unittest.main()
