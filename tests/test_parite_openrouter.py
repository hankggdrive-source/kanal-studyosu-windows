"""OpenRouter üzerinden Claude: model eşleme, Anthropic'e özgü alanların ayıklanması, anahtar denemesi."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parite_yardim import SahteIstemci, gecici_ortam, mesaj  # noqa: E402

from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import openrouter as OR  # noqa: E402
from kanal_studyosu.llm import LLM, LLMHatasi  # noqa: E402

MESAJ = [{"role": "user", "content": "Konu kartını yaz."}]


def _listeyi_yamala(test, kod=200, j=None):
    j = j if j is not None else {"data": [{"id": "anthropic/claude-sonnet-5.5"}, {"id": "anthropic/claude-opus-5.5"},
                                          {"id": "anthropic/claude-haiku-4.5"}, {"id": "qwen/qwen3-max"}]}
    eski = OR._get
    OR._get = lambda yol, anahtar="": (kod, j)
    OR._ESLESME.clear()
    test.addCleanup(setattr, OR, "_get", eski)
    test.addCleanup(OR._ESLESME.clear)


def _hata400(msg="tools: unsupported"):
    import anthropic
    # Kütüphanenin HTTP katmanı sürüme göre değişiyor; yalnız tür ve mesaj gerekli.
    e = anthropic.BadRequestError.__new__(anthropic.BadRequestError)
    Exception.__init__(e, msg)
    e.message, e.status_code = msg, 400
    return e


class OpenRouterTest(unittest.TestCase):
    def setUp(self):
        self.r = gecici_ortam(self)
        A.ayar_kaydet({"saglayici": "openrouter"})
        _listeyi_yamala(self)

    def test_istek_bicimi(self):
        ist = SahteIstemci([mesaj("ok", model_sunulan="anthropic/claude-sonnet-5.5", arama=2)])
        c = LLM(ist).istek("A1", "ORN-VID-06", ["sistem"], MESAJ)
        p = ist.istekler[0]
        self.assertEqual(p["model"], "anthropic/claude-sonnet-5.5")
        self.assertNotIn("betas", p)          # sunucu tarafı yedek model Anthropic'e özgü
        self.assertNotIn("fallbacks", p)
        self.assertIn("cache_control", p)      # önbellek OpenRouter'da destekleniyor
        self.assertEqual(p["tools"][0]["type"], "web_search_20260209")
        self.assertEqual(c.yedek_model, "")   # OpenRouter'ın model adı yedek sanılmaz
        self.assertEqual(c.model, "claude-sonnet-5-5")
        self.assertGreater(c.usd, 0)

    def test_desteklenmeyen_alan_ayiklanir(self):
        ist = SahteIstemci([mesaj("ok")])
        cagri = {"n": 0}
        asil = ist.beta.messages.stream

        def stream(**p):
            cagri["n"] += 1
            if "output_config" in p or "tools" in p:
                raise _hata400()
            return asil(**p)
        ist.beta.messages.stream = stream
        c = LLM(ist).istek("A1", "ORN-VID-06", ["sistem"], MESAJ)
        self.assertEqual(c.metin, "ok")
        self.assertEqual(cagri["n"], 3)  # efor çıkarıldı, sonra web arama çıkarıldı
        self.assertNotIn("tools", ist.istekler[0])

    def test_anthropic_modunda_ayiklama_yok(self):
        A.ayar_kaydet({"saglayici": "claude_code"})  # sahte istemciyle Anthropic biçimli yol
        ist = SahteIstemci([])
        ist.beta.messages.stream = lambda **p: (_ for _ in ()).throw(_hata400())
        with self.assertRaises(LLMHatasi):
            LLM(ist).istek("A1", "ORN-VID-06", ["sistem"], MESAJ)

    def test_anthropic_modu_degismedi(self):
        A.ayar_kaydet({"saglayici": "claude_code"})  # sahte istemciyle Anthropic biçimli yol
        ist = SahteIstemci([mesaj("ok")])
        LLM(ist).istek("A3", "ORN-VID-06", ["sistem"], MESAJ)
        p = ist.istekler[0]
        self.assertEqual(p["model"], "claude-opus-5-5")
        self.assertEqual(p["fallbacks"], "default")

    def test_model_eslestir(self):
        self.assertEqual(OR.model_eslestir("claude-haiku-4-5"), "anthropic/claude-haiku-4.5")
        self.assertEqual(OR.model_eslestir("claude-opus-5-5"), "anthropic/claude-opus-5.5")
        self.assertEqual(OR.model_eslestir("claude-sonnet-5"), "anthropic/claude-sonnet-5")  # listede yok: tahmin

    def test_dogrula(self):
        _listeyi_yamala(self, 200, {"data": {"limit_remaining": 4.5, "is_free_tier": False}})
        ok, msg = OR.dogrula("sk-or-v1-deneme")
        self.assertTrue(ok)
        self.assertIn("4.50", msg)
        _listeyi_yamala(self, 401, {"error": {"message": "No auth"}})
        self.assertFalse(OR.dogrula("sk-or-v1-yanlis")[0])
        self.assertFalse(OR.dogrula("")[0] if not A.anahtar("openrouter") else False)

    def test_liste_ekli_adlar(self):
        _listeyi_yamala(self, 200, {"data": [{"id": "anthropic/claude-sonnet-5.5:batch[1m]"},
                                             {"id": "anthropic/claude-sonnet-5.5[1m]"}]})
        self.assertEqual(OR._normal("anthropic/claude-sonnet-5.5:batch[1m]"), "claude-sonnet-5-5")
        self.assertEqual(OR.model_eslestir("claude-sonnet-5-5"), "anthropic/claude-sonnet-5.5")  # sabit eşleme
        self.assertEqual(OR.model_eslestir("claude-opus-5"), "anthropic/claude-opus-5")

    def test_servis_degisince_dusunce_cikar(self):
        from kanal_studyosu import kanal
        from kanal_studyosu.uretim import Uretim
        kod = "ORN-VID-06"
        A.ayar_kaydet({"saglayici": "claude_code"})  # sahte istemciyle Anthropic biçimli yol
        ist = SahteIstemci([mesaj("<ozet>a</ozet>")] * 3)
        u = Uretim.yeni(kod, "", "", LLM(ist))
        yol = kanal.uygulama_klasoru(kod) / "konusma_A1.json"
        A.json_yaz(yol, {"sistem": ["s"], "saglayici": "anthropic", "mesajlar": [
            {"role": "user", "content": "x"},
            {"role": "assistant", "content": [{"type": "thinking", "thinking": "", "signature": "imza"},
                                              {"type": "text", "text": "eski metin"}]},
            {"role": "user", "content": "düzelt"}]})
        A.ayar_kaydet({"saglayici": "openrouter"})
        u.baslat("A1")
        son = __import__("time").time() + 10
        while u.calisiyor() and __import__("time").time() < son:
            __import__("time").sleep(0.05)
        gonderilen = ist.istekler[0]["messages"]
        self.assertEqual([b["type"] for b in gonderilen[1]["content"]], ["text"])
        self.assertEqual(gonderilen[1]["content"][0]["text"], "eski metin")
        self.assertEqual(A.json_oku(yol)["saglayici"], "openrouter")

    def test_unknown_yedek_sayilmaz(self):
        ist = SahteIstemci([mesaj("ok", model_sunulan="unknown")])
        c = LLM(ist).istek("A1", "ORN-VID-06", ["sistem"], MESAJ)
        self.assertEqual(c.yedek_model, "")

    def test_sinira_takilan_cevabin_ucreti_kaydedilir(self):
        from kanal_studyosu import maliyet
        ist = SahteIstemci([mesaj("yarım", model="claude-opus-5-5", durma="max_tokens", cikis=128000)])
        with self.assertRaises(LLMHatasi) as h:
            LLM(ist).istek("A4", "ORN-VID-06", ["sistem"], MESAJ)
        self.assertIn("128.000", str(h.exception))
        self.assertEqual(ist.istekler[0]["max_tokens"], 128000)
        self.assertGreater(maliyet.ozet("ORN-VID-06")["video_usd"], 2.5)

    def test_bakiye(self):
        cevaplar = {"/v1/credits": (200, {"data": {"total_credits": 20, "total_usage": 7.456}})}
        eski = OR._get
        OR._get = lambda yol, anahtar="": cevaplar.get(yol, (404, {}))
        self.addCleanup(setattr, OR, "_get", eski)
        self.assertEqual(OR.bakiye("sk-or-x"), 12.54)
        cevaplar.clear()
        cevaplar["/v1/key"] = (200, {"data": {"limit_remaining": 3.2}})  # /credits yoksa anahtar limiti
        self.assertEqual(OR.bakiye("sk-or-x"), 3.2)
        cevaplar.clear()
        self.assertIsNone(OR.bakiye("sk-or-x"))  # okunamazsa gösterge '—'
        self.assertIsNone(OR.bakiye(""))

    def test_gecersiz_saglayici(self):
        with self.assertRaises(ValueError):
            A.ayar_kaydet({"saglayici": "qwen"})


if __name__ == "__main__":
    unittest.main()
