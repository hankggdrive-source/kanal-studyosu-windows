"""Windows'a özgü işler (Kanal Stüdyosu Windows sürümü). Mac sürümündeki Anahtar Zinciri, Finder, pgrep ve `open`
yerine geçer. Testlerin Linux'ta da çalışabilmesi için Windows dışında zararsız yedek davranışlar vardır.

- surec_yasiyor: os.kill(pid, 0) Windows'ta süreci SONLANDIRIR; onun yerine OpenProcess/GetExitCodeProcess.
- klasor_ac: Dosya Gezgini (os.startfile).
- capcut_acik: tasklist ile CapCut.exe.
- anahtar_*: Windows Kimlik Bilgisi Yöneticisi (keyring kütüphanesi); kütüphane yoksa ortam değişkeni.
- capcut_varsayilan / capcut_kullanici_verisi: %LOCALAPPDATA%\\CapCut\\User Data.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

WINDOWS = sys.platform == "win32"
_GIZLI = 0x08000000 if WINDOWS else 0  # CREATE_NO_WINDOW: alt süreçler siyah pencere açmasın


def gizli() -> dict:
    """subprocess çağrılarına eklenecek bayrak (Windows'ta konsol penceresi açılmaz)."""
    return {"creationflags": _GIZLI} if WINDOWS else {}


def alt_surecleri_gizle() -> None:
    """Uygulama konsolsuz (pythonw) çalışır; her ffmpeg/curl çağrısında siyah pencere açılmasın diye bütün alt
    süreçlere CREATE_NO_WINDOW eklenir. Yalnız Windows'ta, açılışta bir kez."""
    if not WINDOWS or getattr(subprocess.Popen, "_ks_gizli", False):
        return
    asil = subprocess.Popen.__init__

    def yeni(self, *a, **k):
        k["creationflags"] = k.get("creationflags", 0) | _GIZLI
        asil(self, *a, **k)
    subprocess.Popen.__init__ = yeni
    subprocess.Popen._ks_gizli = True


def surec_yasiyor(pid: int) -> bool:
    if pid <= 0:
        return False
    if not WINDOWS:
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ctypes.get_last_error() == 5  # erişim reddi: süreç var ama başka kullanıcının
    try:
        kod = wintypes.DWORD()
        if not k32.GetExitCodeProcess(h, ctypes.byref(kod)):
            return False
        return kod.value == 259  # STILL_ACTIVE
    finally:
        k32.CloseHandle(h)


def klasor_ac(yol) -> None:
    yol = str(yol)
    if WINDOWS:
        os.startfile(yol)  # noqa: S606 (yalnız kendi klasörlerimiz)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", yol])
    else:
        subprocess.Popen(["xdg-open", yol])


def capcut_acik() -> bool:
    if not WINDOWS:
        return False
    try:
        c = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe", "/NH"], capture_output=True, text=True,
                           **gizli()).stdout
        return "capcut.exe" in c.lower()
    except OSError:
        return False


def capcut_kullanici_verisi() -> Path:
    yerel = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(yerel) / "CapCut" / "User Data"


def capcut_varsayilan() -> str:
    return str(capcut_kullanici_verisi() / "Projects" / "com.lveditor.draft")


# --- anahtarlar ------------------------------------------------------------------

def _keyring():
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def anahtar_oku(servis: str, hesap: str, ortam: str) -> str:
    kr = _keyring()
    if kr is None:
        return os.environ.get(ortam, "")
    try:
        return kr.get_password(servis, hesap) or os.environ.get(ortam, "")
    except Exception:
        return os.environ.get(ortam, "")


def anahtar_yaz(servis: str, hesap: str, deger: str) -> None:
    kr = _keyring()
    if kr is None:
        raise ValueError("Anahtar kaydı için 'keyring' kütüphanesi gerekli (uygulamayı başlatıcıyla aç; ilk açılışta kurulur).")
    try:
        kr.set_password(servis, hesap, deger)
    except Exception as e:
        raise ValueError(f"Anahtar Windows Kimlik Bilgisi Yöneticisi'ne kaydedilemedi ({type(e).__name__}).")


def anahtar_sil(servis: str, hesap: str) -> None:
    kr = _keyring()
    if kr is None:
        return
    try:
        kr.delete_password(servis, hesap)
    except Exception:
        pass
