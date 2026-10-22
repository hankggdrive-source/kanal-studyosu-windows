"""Müzik yatağı: farklı parçalarla doldurma, kısa parçanın sonuna kadar sürmesi, boş klasörde müziksiz devam."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_genel_kanal import ortam  # noqa: E402

from kanal_studyosu import araclar  # noqa: E402
from kanal_studyosu import ayarlar as A  # noqa: E402
from kanal_studyosu import capcut_zinciri as C  # noqa: E402

FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
KOD = "BK-01"


def ton(yol: Path, frekans: int, sure: int) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency={frekans}:duration={sure}",
                    str(yol)], check=True)


def sure(yol: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(yol)],
                                capture_output=True, text=True).stdout)


def ses(yol: Path, bas: float) -> float:
    o = subprocess.run(["ffmpeg", "-nostats", "-ss", str(bas), "-t", "3", "-i", str(yol), "-af", "volumedetect", "-f",
                        "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+)", o).group(1))


@unittest.skipUnless(FFMPEG, "ffmpeg gerekli")
class MuzikTest(unittest.TestCase):
    def setUp(self):
        self.k = ortam(self)
        self.muz = self.k / "Varliklar" / "Muzik"
        self.dr = A.yol("capcut_taslak") / KOD
        self.dr.mkdir(parents=True)
        (self.dr / "draft_info.json").write_text(json.dumps({
            "duration": 200_000_000, "materials": {"videos": [{"id": "m1", "path": "x/sahne0001.mp4"}]},
            "tracks": [{"type": "video", "segments": [{"material_id": "m1", "target_timerange": {"start": 0}}]}]}))

    def test_farkli_parcalarla_sonuna_kadar(self):
        for i, f in enumerate((220, 330, 440, 550)):
            ton(self.muz / f"parca{i}.mp3", f, 70)
        cikis = self.k / "muzik.m4a"
        c = araclar.calistir("muzik_otomatik.py", KOD, "--cikis", str(cikis), "--son-sn", "8", "--tohum", "3").cikti
        secilen = re.search(r"secilen:.*", c).group(0)
        adlar = re.findall(r"(parca\d\.mp3)", secilen)
        self.assertGreaterEqual(len(adlar), 3, secilen)          # 208 sn için 70 sn'lik parçalardan en az 3
        self.assertEqual(len(adlar), len(set(adlar)), secilen)   # klasör bitmeden tekrar yok
        self.assertAlmostEqual(sure(cikis), 208, delta=0.5)
        for t in (10, 100, 180, 203):
            self.assertGreater(ses(cikis, t), -60, f"{t}. saniyede müzik yok")

    def test_tek_kisa_parca_dongulenir(self):
        ton(self.muz / "kisa.mp3", 300, 50)
        cikis = self.k / "muzik.m4a"
        araclar.calistir("muzik_otomatik.py", KOD, "--cikis", str(cikis), "--son-sn", "8")
        self.assertAlmostEqual(sure(cikis), 208, delta=0.5)
        for t in (40, 120, 200):
            self.assertGreater(ses(cikis, t), -60, f"{t}. saniyede müzik yok")

    def test_bos_klasorde_muziksiz(self):
        gecen = {}

        def sahte(betik, *arg, **k):
            gecen["arg"] = arg
            return araclar.Sonuc(0, "tamam 3 sahne, sure 20.0 | muzik: YOK")
        eski = araclar.calistir
        araclar.calistir = sahte
        self.addCleanup(setattr, araclar, "calistir", eski)
        r = C.yayin_hazirla(KOD, "TEMIZ []")
        self.assertIn("--muziksiz", gecen["arg"])
        self.assertNotIn("TEMIZ", gecen["arg"])
        self.assertIn("müziksiz üretildi", r["secilen"])


if __name__ == "__main__":
    unittest.main()
