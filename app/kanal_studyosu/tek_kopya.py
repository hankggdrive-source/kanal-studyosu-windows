"""Tek kopya: uygulama zaten açıksa ikinci kopya başlamaz, tarayıcıda açık olan gösterilir.

Açık kopya kendi adresini (pid, port, erişim anahtarı) bir dosyaya yazar. Yeni açılış önce bu dosyaya bakar: süreç
yaşıyor ve sunucu cevap veriyorsa o adres döner. Dosya eskiyse (uygulama çökmüş) yok sayılır ve üzerine yazılır.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


def _yasiyor(pid: int) -> bool:
    # Windows'ta os.kill(pid, 0) süreci sonlandırır; güvenli denetim sistem_win'de.
    from .sistem_win import surec_yasiyor
    return surec_yasiyor(pid)


def calisan(dosya: Path) -> str | None:
    """Açık ve cevap veren kopyanın adresi; yoksa None."""
    try:
        d = json.loads(Path(dosya).read_text(encoding="utf-8"))
        pid, port, token = int(d["pid"]), int(d["port"]), str(d["token"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if pid == os.getpid() or not _yasiyor(pid):
        return None
    try:
        r = urllib.request.Request(f"http://127.0.0.1:{port}/api/durum", headers={"X-App-Token": token})
        with urllib.request.urlopen(r, timeout=3) as c:
            if c.status != 200:
                return None
    except OSError:
        return None
    return f"http://127.0.0.1:{port}/?token={token}"


def kaydet(dosya: Path, port: int, token: str) -> None:
    dosya = Path(dosya)
    dosya.parent.mkdir(parents=True, exist_ok=True)
    gecici = dosya.with_name(dosya.name + ".tmp")
    gecici.write_text(json.dumps({"pid": os.getpid(), "port": port, "token": token}), encoding="utf-8")
    os.chmod(gecici, 0o600)  # erişim anahtarı içerir
    os.replace(gecici, dosya)


def sil(dosya: Path) -> None:
    """Yalnız bu kopyanın yazdığı dosyayı siler."""
    try:
        if int(json.loads(Path(dosya).read_text(encoding="utf-8")).get("pid", -1)) == os.getpid():
            Path(dosya).unlink()
    except (OSError, ValueError):
        pass
