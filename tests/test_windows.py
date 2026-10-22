"""Windows sürümüne özgü parçalar. Windows'ta (GitHub Actions) gerçekten, başka sistemde yedek davranışla çalışır."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from kanal_studyosu import claude_code as CC  # noqa: E402
from kanal_studyosu import sistem_win as W  # noqa: E402

ARACLAR = Path(__file__).resolve().parent.parent / "app" / "araclar"


class SistemTest(unittest.TestCase):
    def test_surec_denetimi_sureci_oldurmez(self):
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        self.addCleanup(p.kill)
        self.assertTrue(W.surec_yasiyor(p.pid))
        self.assertTrue(W.surec_yasiyor(p.pid))  # iki kez sorulunca da yaşıyor (os.kill(pid,0) Windows'ta öldürürdü)
        self.assertIsNone(p.poll())
        p.kill()
        p.wait()
        self.assertFalse(W.surec_yasiyor(p.pid))
        self.assertFalse(W.surec_yasiyor(0))

    def test_capcut_yollari(self):
        self.assertTrue(W.capcut_varsayilan().replace("\\", "/").endswith("CapCut/User Data/Projects/com.lveditor.draft"))
        self.assertIsInstance(W.capcut_acik(), bool)

    def test_claude_cmd_sarmalanir(self):
        self.assertEqual(CC._komut("C:/Users/x/AppData/Roaming/npm/claude.cmd")[:2], ["cmd", "/c"])
        self.assertEqual(CC._komut("C:/Users/x/.local/bin/claude.exe"), ["C:/Users/x/.local/bin/claude.exe"])

    def test_varsayilan_capcut_ayari_ortam_degiskeniyle(self):
        from kanal_studyosu import ayarlar as A
        d = json.loads((Path(A.VARSAYILAN) if hasattr(A, "VARSAYILAN") else
                        Path(__file__).resolve().parent.parent / "app/config/varsayilan.json").read_text(encoding="utf-8"))
        self.assertIn("%LOCALAPPDATA%", d["yollar"]["capcut_taslak"])

    @unittest.skipUnless(sys.platform == "win32", "yalnız Windows")
    def test_alt_surec_gizleme(self):
        W.alt_surecleri_gizle()
        W.alt_surecleri_gizle()  # iki kez çağrılınca bozulmaz
        self.assertEqual(subprocess.run([sys.executable, "-c", "print(1)"], capture_output=True, text=True).stdout.strip(), "1")


class TaslakTest(unittest.TestCase):
    def test_iki_adla_yazilir_ve_efekt_yollari_cevrilir(self):
        import tempfile
        kok = Path(tempfile.mkdtemp())
        capcut = kok / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
        dr = capcut / "BK-01"
        (dr / "Timelines" / "X").mkdir(parents=True)
        os.environ["KS_CAPCUT"] = str(capcut)
        self.addCleanup(os.environ.pop, "KS_CAPCUT", None)
        sys.path.insert(0, str(ARACLAR))
        import importlib
        import ortak
        importlib.reload(ortak)
        ortak.taslak_yaz(str(dr), {"a": 1})
        for ad in ("draft_info.json", "draft_content.json", "draft_info.json.bak", "draft_content.json.bak"):
            self.assertTrue((dr / ad).exists(), ad)
            self.assertTrue((dr / "Timelines" / "X" / ad).exists(), ad)
        (dr / "draft_info.json").unlink()
        self.assertTrue(ortak.taslak_yolu(str(dr)).endswith("draft_content.json"))
        self.assertEqual(ortak.taslak_oku(str(dr)), {"a": 1})
        veri = ortak.capcut_kullanici_verisi()
        self.assertTrue(veri.endswith("CapCut/User Data"), veri)
        self.assertNotIn("\\", veri)


if __name__ == "__main__":
    unittest.main()
