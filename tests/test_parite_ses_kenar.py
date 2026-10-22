"""Sahne sesinin kenarları (sondaki kesik ve tık), kontrol özeti, TTS istek kaydı ve apostrof düzleştirme."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parite_yardim import gecici_ortam  # noqa: E402
from test_parite_ses import FFMPEG, _SahteAPI  # noqa: E402

from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import ses_kenar as SK  # noqa: E402
from kanal_studyosu import studio_baglanti as ST  # noqa: E402


def _ses(yol: Path, filtre: str) -> bytes:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", filtre, "-b:a", "128k", str(yol)], check=True)
    return yol.read_bytes()


# 0,3 sn sessizlik + 1,2 sn ton (sesli noktada aniden biter) + 0,5 sn sessizlik + 10 ms tık + 0,1 sn sessizlik
KESIK_TIKLI = ("aevalsrc='if(between(t,0.3,1.5),0.4*sin(2*PI*330*t),0)+if(between(t,2.0,2.01),0.5*sin(2*PI*2000*t),0)'"
               ":s=44100:d=2.11")


@unittest.skipUnless(FFMPEG, "ffmpeg gerekli")
class KenarTest(unittest.TestCase):
    def setUp(self):
        self.r = gecici_ortam(self)
        cp = self.r.parent / "Creator Projects"
        cp.mkdir()
        A.ayar_kaydet({"yollar": {"creator_projects": str(cp)}})
        self.cid, self.vid = ST.video_bul_ya_da_olustur("ORN-VID-07", "ORN-VID-07 Prova", None)
        self.k = ST.video_klasoru(self.cid, self.vid)

    def _vj(self):
        return json.loads((self.k / "video.json").read_text(encoding="utf-8"))

    def _uret(self, ses: bytes, metin: str = "L’unica cosa, dell’altra: “basta”.") -> dict:
        ST.metin_ver(self.cid, self.vid, metin, 1)
        g = self.r.parent / "g.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=gray:s=800x1000", "-frames:v", "1",
                        str(g)], check=True)
        ST.gorselleri_koy(self.cid, self.vid, {1: g})
        self.api = _SahteAPI(ses)
        ST.seslendir(self.vid, lambda m: None, api=self.api)
        ST.son_kontrol(self.cid, self.vid)
        j = ST.videolari_uret(self.vid, lambda m: None)
        self.assertEqual((j["ok"], j["failed"]), (1, 0), self._vj()["scenes"])
        return self._vj()["scenes"][0]

    def test_kesik_ve_tik_duzelir(self):
        ham = self.r.parent / "a.mp3"
        s = self._uret(_ses(ham, KESIK_TIKLI))
        k = s["kenar"]
        self.assertTrue(k["tik"])
        self.assertAlmostEqual(k["tail"], 1.5, delta=0.02)  # tık değil, konuşmanın bittiği an
        self.assertEqual(k["once"], "sert")
        self.assertEqual(k["sonra"], "")
        self.assertLess(abs(k["seviye_farki"]), 0.2)
        mp4 = self.k / s["video_file"]
        # süre: ses + 0,4 sn nefes payı, kısalmadı
        self.assertAlmostEqual(ST._sure(mp4), ST._sure(ham) + 0.4, delta=0.06)
        a1 = SK.pcm(mp4)
        self.assertLess(max(abs(x) for x in a1[int(1.6 * SK.SR):]), 9)  # tık susturuldu
        self.assertEqual(list((self.k / "temp").glob("*.wav")), [])  # ara dosya kalmadı
        self.assertTrue(ham.read_bytes() == (self.k / "audio" / "sahne0001.mp3").read_bytes())  # ham ses aynen
        o = ST.kenar_ozeti(self.vid)
        self.assertTrue(o["temiz"])
        self.assertIn("sert 1 / orta 0 → sonrası 0/0", o["metin"])
        self.assertIn("susturulan tık 1", o["metin"])

    def test_istek_kaydi_ve_duz_apostrof(self):
        self._uret(_ses(self.r.parent / "a.mp3", "sine=frequency=330:duration=1"))
        self.assertEqual(self.api.gonderilen, ["L'unica cosa, dell'altra: \"basta\"."])
        self.assertIn("L’unica", (self.k / "script.txt").read_text(encoding="utf-8"))  # kaynak aynen
        satir = json.loads((self.k / "logs" / "tts_istekleri.jsonl").read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual((satir["scene"], satir["audio_file"], satir["job_id"]), (1, "audio/sahne0001.mp3", "is-1"))
        self.assertEqual((satir["model_id"], satir["voice_id"], satir["language_code"]),
                         ("eleven_v3", "ornekSesKimligi0001", "it"))
        self.assertEqual(satir["voice_settings"], {"stability": 0.5, "similarity_boost": 0.75, "style": 0, "speed": 1,
                                                   "use_speaker_boost": True})
        self.assertEqual(satir["text"], "L'unica cosa, dell'altra: \"basta\".")
        self.assertEqual(satir["seed"], "gönderilmedi")
        self.assertNotIn("anahtar", json.dumps(satir).lower())

    def test_eski_video_kenarsiz(self):
        """Kenar ayarı olmadan açılmış (eski) videoya dokunulmaz."""
        d = self._vj()
        d["video_settings"].pop("kenar")
        (self.k / "video.json").write_text(json.dumps(d), encoding="utf-8")
        s = self._uret(_ses(self.r.parent / "a.mp3", KESIK_TIKLI))
        self.assertNotIn("kenar", s)
        self.assertIsNone(ST.kenar_ozeti(self.vid))


class OzetTest(unittest.TestCase):
    def setUp(self):
        self.r = gecici_ortam(self)  # kontroller seçili kanalın ayarlarını okur

    def test_temiz_degil(self):
        o = SK.ozet([{"sahne": 1, "once": "sert", "sonra": "orta", "sonra_db": 21.4, "seviye_farki": 0.05},
                     {"sahne": 2, "once": "", "sonra": "", "tik": True, "seviye_farki": -0.11}])
        self.assertFalse(o["temiz"])
        self.assertEqual(o["kalan"], ["sahne 0001 (orta, 21 dB)"])
        self.assertEqual((o["once_sert"], o["sonra_orta"], o["tik"], o["seviye_db"]), (1, 1, 1, 0.11))


if __name__ == "__main__":
    unittest.main()
