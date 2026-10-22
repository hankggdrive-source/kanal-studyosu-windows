"""Tek kopya: açık kopya varken ikinci açılış yeni sunucu başlatmaz; eski/bozuk kayıt yok sayılır."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from kanal_studyosu import sunucu, tek_kopya  # noqa: E402


class TekKopyaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.dosya = self.tmp / "calisan.json"

    def test_acik_kopya_bulunur(self):
        s = sunucu.baslat(0)
        threading.Thread(target=s.serve_forever, daemon=True).start()
        self.addCleanup(s.server_close)
        self.addCleanup(s.shutdown)
        tek_kopya.kaydet(self.dosya, sunucu.PORT[0], sunucu.TOKEN)
        if sys.platform != "win32":  # Windows'ta dosya izni bu biçimde yok
            self.assertEqual(self.dosya.stat().st_mode & 0o777, 0o600)
        self.assertIsNone(tek_kopya.calisan(self.dosya))  # aynı süreç kendini "açık kopya" saymaz
        d = json.loads(self.dosya.read_text())
        d["pid"] = os.getppid()  # başka (yaşayan) bir süreç gibi (Windows'ta 1 numaralı süreç yok)
        self.dosya.write_text(json.dumps(d))
        self.assertEqual(tek_kopya.calisan(self.dosya), f"http://127.0.0.1:{sunucu.PORT[0]}/?token={sunucu.TOKEN}")
        d["token"] = "yanlis"
        self.dosya.write_text(json.dumps(d))
        self.assertIsNone(tek_kopya.calisan(self.dosya))  # sunucu cevap vermiyorsa (yetkisiz) yok sayılır

    def test_eski_ve_bozuk_kayit(self):
        self.assertIsNone(tek_kopya.calisan(self.dosya))  # dosya yok
        self.dosya.write_text("bozuk")
        self.assertIsNone(tek_kopya.calisan(self.dosya))
        self.dosya.write_text(json.dumps({"pid": 99999999, "port": 1, "token": "x"}))  # süreç yok
        self.assertIsNone(tek_kopya.calisan(self.dosya))
        tek_kopya.sil(self.dosya)  # başka sürecin kaydı: silinmez
        self.assertTrue(self.dosya.exists())
        tek_kopya.kaydet(self.dosya, 1234, "t")
        tek_kopya.sil(self.dosya)
        self.assertFalse(self.dosya.exists())


if __name__ == "__main__":
    unittest.main()
