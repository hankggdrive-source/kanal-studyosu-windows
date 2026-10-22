"""Geri Dönüşüm Kutusu'na taşıma (kalıcı silme yok; Geri Dönüşüm Kutusu boşaltılana kadar geri alınabilir).

Windows'ta send2trash kütüphanesiyle taşınır ("Geri yükle" çalışır). KANAL_STUDYOSU_COP ortam değişkeni verilirse
(testler) oraya taşınır.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def _benzersiz(hedef: Path) -> Path:
    if not hedef.exists():
        return hedef
    return hedef.with_name(f"{hedef.name} {datetime.now().strftime('%Y%m%d-%H%M%S')}")


def tasi(yol: Path) -> Path | None:
    """yol'u Çöp'e taşır; taşınan yeri (biliniyorsa) döndürür. Yol yoksa None."""
    yol = Path(yol)
    if not yol.exists():
        return None
    ozel = os.environ.get("KANAL_STUDYOSU_COP")
    if not ozel and platform.system() == "Windows":
        from send2trash import send2trash
        send2trash(str(yol))
        if not yol.exists():
            return None
    cop = Path(ozel) if ozel else Path.home() / ".local/share/Trash/files"
    cop.mkdir(parents=True, exist_ok=True)
    hedef = _benzersiz(cop / yol.name)
    shutil.move(str(yol), str(hedef))
    return hedef
