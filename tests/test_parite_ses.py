"""AI84 istemcisi (yerel sahte sunucuyla) ve uygulamanın kendi ses/video katmanı (eski Studio'suz)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parite_yardim import gecici_ortam  # noqa: E402

from kanal_studyosu import ai84 as AI  # noqa: E402
from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import studio_baglanti as ST  # noqa: E402

FFMPEG = shutil.which("ffmpeg") and shutil.which("ffprobe")


class _Sahte(BaseHTTPRequestHandler):
    """Belgedeki davranışlar: 429 + Retry-After, sorguda 5xx, failed + errorCategory, done + audioUrl."""
    senaryo: dict = {}

    def log_message(self, *a):
        pass

    def _yaz(self, kod, veri, bas=None):
        g = json.dumps(veri).encode() if not isinstance(veri, bytes) else veri
        self.send_response(kod)
        for k, v in (bas or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(g)))
        self.end_headers()
        self.wfile.write(g)

    def do_GET(self):
        s = self.senaryo
        s.setdefault("istekler", []).append(("GET", self.path, self.headers.get("xi-api-key")))
        if self.path == "/ses.mp3":  # imzalı ses adresi: anahtarsız indirilir
            return self._yaz(200, b"ID3" + b"\0" * 400)
        if self.headers.get("xi-api-key") != "dogru-anahtar-123":
            return self._yaz(401, {"error": "Unauthorized"})
        if self.path == "/v1/credits":
            return self._yaz(200, {"credits": 12345})
        if self.path.startswith("/v2/text-to-speech/async/"):
            jid = self.path.rsplit("/", 1)[1]
            s["sorgu"] = s.get("sorgu", 0) + 1
            if s["sorgu"] == 1:
                return self._yaz(502, {"error": "gateway"})  # iş sürüyor sayılmalı
            if s["sorgu"] == 2:
                return self._yaz(200, {"job": {"id": jid, "status": "processing"}})
            if jid == "kotu":
                return self._yaz(200, {"job": {"id": jid, "status": "failed", "errorMessage": "Metin çok uzun",
                                               "errorCategory": 1, "errorMessageKey": "too_long"}})
            port = self.server.server_port
            return self._yaz(200, {"job": {"id": jid, "status": "done", "credit_cost": 7,
                                           "audioUrl": f"http://127.0.0.1:{port}/ses.mp3"}})
        self._yaz(404, {})

    def do_POST(self):
        s = self.senaryo
        uz = int(self.headers.get("Content-Length") or 0)
        s.setdefault("istekler", []).append(("POST", self.path, json.loads(self.rfile.read(uz))))
        s["post"] = s.get("post", 0) + 1
        if s["post"] == 1:
            return self._yaz(429, {"error": "rate"}, {"Retry-After": "2"})
        self._yaz(200, {"job_id": "is-1", "credit_cost": 7})


class AI84IstemciTest(unittest.TestCase):
    def setUp(self):
        _Sahte.senaryo = {}
        self.s = ThreadingHTTPServer(("127.0.0.1", 0), _Sahte)
        threading.Thread(target=self.s.serve_forever, daemon=True).start()
        self.addCleanup(self.s.shutdown)
        self.taban = f"http://127.0.0.1:{self.s.server_port}"
        self.beklemeler = []
        self.api = AI.AI84("dogru-anahtar-123", self.taban, bekle=self.beklemeler.append)

    def test_kredi_ve_gecersiz_anahtar(self):
        self.assertEqual(self.api.krediler(), 12345)
        with self.assertRaises(AI.AI84Hatasi) as h:
            AI.AI84("yanlis-anahtar-1", self.taban).krediler()
        self.assertEqual(h.exception.http, 401)
        self.assertIn("geçersiz", str(h.exception))
        with self.assertRaises(AI.AI84Hatasi):
            AI.AI84("", self.taban).krediler()

    def test_gonder_429_sonra_sorgu_5xx_ve_indir(self):
        j = self.api.tts_gonder({"text": "Ciao", "voice_id": "v"})
        self.assertEqual(j["job_id"], "is-1")
        self.assertEqual(self.beklemeler[0], 2.0)  # Retry-After
        durumlar = []
        job = self.api.tts_bekle("is-1", aralik=0, durum_cb=durumlar.append)
        self.assertEqual(job["status"], "done")
        self.assertEqual(durumlar, ["processing", "done"])  # 502 iş sürüyor sayıldı
        self.assertTrue(self.api.indir(job["audioUrl"]).startswith(b"ID3"))
        post = [x for x in _Sahte.senaryo["istekler"] if x[0] == "POST"][-1]
        self.assertEqual(post[2]["text"], "Ciao")

    def test_403_sunucu_mesaji_gosterilir(self):
        h = AI.AI84._hata(403, {"_ham": "<html>Attention Required! | Cloudflare</html>"})
        self.assertIn("HTTP 403", str(h))
        self.assertIn("Cloudflare", str(h))
        self.assertIn("Insufficient", str(AI.AI84._hata(403, {"message": "Insufficient plan"})))

    def test_basarisiz_is_kategori(self):
        with self.assertRaises(AI.AI84Hatasi) as h:
            self.api.tts_bekle("kotu", aralik=0)
        self.assertEqual((h.exception.kategori, h.exception.anahtar), (1, "too_long"))
        self.assertEqual(str(h.exception), "Metin çok uzun")


def _ses(yol: Path, sn: float = 1.0) -> bytes:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency=330:duration={sn}",
                    "-b:a", "128k", str(yol)], check=True)
    return yol.read_bytes()


class _SahteAPI:
    def __init__(self, ses: bytes, gecikme: float = 0, basarisiz=()):
        self.ses, self.gecikme, self.basarisiz, self.gonderilen, self.sorgulanan = ses, gecikme, set(basarisiz), [], []

    def tts_gonder(self, g):
        self.gonderilen.append(g["text"])
        return {"job_id": f"is-{len(self.gonderilen)}"}

    def tts_bekle(self, jid):
        self.sorgulanan.append(jid)
        time.sleep(self.gecikme)
        if jid in self.basarisiz:
            raise AI.AI84Hatasi("10 dakikada tamamlanmadı", None)  # zaman aşımı: iş AI84'te sürüyor olabilir
        return {"status": "done", "audioUrl": "https://x/a.mp3", "credit_cost": 5}

    def indir(self, url):
        return self.ses


@unittest.skipUnless(FFMPEG, "ffmpeg gerekli")
class SesVideoTest(unittest.TestCase):
    def setUp(self):
        self.r = gecici_ortam(self)
        cp = self.r.parent / "Creator Projects"
        cp.mkdir()
        A.ayar_kaydet({"yollar": {"creator_projects": str(cp)}})
        self.cid, self.vid = ST.video_bul_ya_da_olustur("ORN-VID-06", "ORN-VID-06 Lo specchio", None)
        self.k = ST.video_klasoru(self.cid, self.vid)
        self.ses = _ses(self.r.parent / "a.mp3")

    def _metin(self, n):
        ST.metin_ver(self.cid, self.vid, "\n\n".join(f"Frase numero {i}." for i in range(1, n + 1)), n)

    def _vj(self):
        return json.loads((self.k / "video.json").read_text(encoding="utf-8"))

    def test_kanal_ve_video_kaydi_olusur(self):
        c = {"voice": ST.ses_ayari()}  # Kanal Stüdyosu: ses kanal ayarından (channel.json yok)
        self.assertEqual(c["voice"]["model_id"], "eleven_v3")
        self.assertTrue(self.k.name.startswith("orn-vid-06-lo-specchio-"))
        self.assertEqual(ST.video_bul_ya_da_olustur("ORN-VID-06", "x", self.vid), (self.cid, self.vid))  # devam

    def test_ayni_ses_yeniden_uretilmez_ve_hatali_tekrar(self):
        self._metin(3)
        api = _SahteAPI(self.ses, basarisiz={"is-2"})
        j = ST.seslendir(self.vid, lambda m: None, api=api)
        self.assertEqual((j["ok"], j["failed"]), (2, 1))
        s2 = self._vj()["scenes"][1]
        self.assertEqual(s2["audio_status"], "failed")
        self.assertEqual(s2["job_id"], "is-2")  # zaman aşımı: iş numarası korunur (tekrar ücretsiz sorgulanır)
        j = ST.seslendir(self.vid, lambda m: None, api=api)  # tekrar=False: hatalı atlanır, kimse yeniden gönderilmez
        self.assertEqual(len(api.gonderilen), 3)
        api.basarisiz.clear()
        j = ST.seslendir(self.vid, lambda m: None, tekrar=True, api=api)
        self.assertEqual((j["ok"], j["failed"]), (3, 0))
        self.assertEqual(len(api.gonderilen), 3)  # aynı iş sorgulandı, yeni ücretli istek yok
        self.assertEqual(api.sorgulanan[-1], "is-2")

    def test_gonderim_aninda_kapanma_belirsiz(self):
        self._metin(1)
        d = self._vj()
        d["scenes"][0].update(audio_status="submitting", job_id=None)
        (self.k / "video.json").write_text(json.dumps(d), encoding="utf-8")
        api = _SahteAPI(self.ses)
        j = ST.seslendir(self.vid, lambda m: None, api=api)
        self.assertEqual(j["failed"], 1)
        self.assertEqual(api.gonderilen, [])  # kendiliğinden yeniden gönderilmez
        self.assertEqual(self._vj()["scenes"][0]["audio_status"], "unknown")
        self.assertEqual(ST.seslendir(self.vid, lambda m: None, tekrar=True, api=api)["ok"], 1)

    def test_durdur_kaldigi_yerden(self):
        self._metin(8)
        api = _SahteAPI(self.ses, gecikme=0.1)
        eski = ST._istemci
        ST._istemci = lambda: api
        self.addCleanup(setattr, ST, "_istemci", eski)
        bas = time.time()
        with self.assertRaises(ST.StudioHatasi) as h:
            ST.is_calistir("tts", self.cid, self.vid, lambda m: None, iptal=lambda: time.time() - bas > 0.25)
        self.assertIn("Durduruldu", str(h.exception))
        yapilan = len(api.gonderilen)
        self.assertLess(yapilan, 8)
        j = ST.is_calistir("tts", self.cid, self.vid, lambda m: None)
        self.assertEqual(j["ok"], 8)
        self.assertEqual(len(api.gonderilen), 8)  # bitenler yeniden üretilmedi

    def test_sahne_videosu(self):
        self._metin(2)
        for n, renk in ((1, "red"), (2, "blue")):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color={renk}:s=800x1000",
                            "-frames:v", "1", str(self.r.parent / f"g{n}.jpg")], check=True)
        ST.gorselleri_koy(self.cid, self.vid, {n: self.r.parent / f"g{n}.jpg" for n in (1, 2)})
        ST.seslendir(self.vid, lambda m: None, api=_SahteAPI(self.ses))
        ST.son_kontrol(self.cid, self.vid)
        j = ST.videolari_uret(self.vid, lambda m: None)
        self.assertEqual((j["ok"], j["failed"]), (2, 0), self._vj()["scenes"])
        v = ST.videolari_dogrula(self.k, 2)
        self.assertEqual(v["sorunlar"], [])
        self.assertAlmostEqual(v["sure"], 2 * 1.4, delta=0.15)  # ses + 0,4 sn nefes payı
        zaman = (self.k / "scene-videos" / "sahne0001.mp4").stat().st_mtime
        ST.videolari_uret(self.vid, lambda m: None)  # değişiklik yok: yeniden üretilmez
        self.assertEqual((self.k / "scene-videos" / "sahne0001.mp4").stat().st_mtime, zaman)


class SesAyariTest(unittest.TestCase):
    def setUp(self):
        self.r = gecici_ortam(self)  # kontroller seçili kanalın ayarlarını okur

    def test_govde(self):
        g = ST._tts_govde(A.ayarlar()["ses"], "Ciao")
        self.assertEqual((g["voice_id"], g["model_id"], g["language_code"]), ("ornekSesKimligi0001", "eleven_v3", "it"))
        self.assertEqual(set(g["voice_settings"]), {"stability", "similarity_boost", "style", "speed", "use_speaker_boost"})
        self.assertEqual(ST.ses_dogrula(A.ayarlar()["ses"]), [])
        # Eski Studio ile aynı hash: önceden üretilmiş sesler tanınır.
        self.assertEqual(ST._ses_hash("a", {"x": 1}),
                         __import__("hashlib").sha256(("a\0" + json.dumps({"x": 1}, sort_keys=True)).encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
