"""Her açılışta genel ön kontrol (programlar, kurulum klasörü, anahtarlar) ve seçili kanalın üretime hazırlığı."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import ayarlar as A
from . import kanallar
from . import yollar


def program(ad: str) -> str | None:
    """Programın yolu. Windows'ta winget kurulumundan sonra PATH henüz yenilenmemiş olabilir: bilinen klasörlere de bakılır."""
    bulunan = shutil.which(ad)
    if bulunan:
        return bulunan
    yerel = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local")))
    adaylar = list((yerel / "Microsoft/WinGet/Links").glob(f"{ad}.exe"))
    for kok in (Path(os.environ.get("ProgramFiles", "C:/Program Files")), yerel / "Microsoft/WinGet/Packages"):
        adaylar += list(kok.glob(f"ImageMagick*/{ad}.exe")) + list(kok.glob(f"*FFmpeg*/**/bin/{ad}.exe"))
    return str(adaylar[0]) if adaylar else None


_program = program  # eski ad (üretim modülleri kullanır)


def _madde(ad: str, tamam: bool, mesaj: str, zorunlu: bool = True) -> dict:
    return {"ad": ad, "tamam": tamam, "mesaj": mesaj, "zorunlu": zorunlu}


def _pillow() -> bool:
    try:
        import PIL  # noqa: F401  (araçlar uygulamanın kendi Python ortamında çalışır)
        return True
    except ImportError:
        return False


def ai84_dogrula(anahtar: str = "") -> tuple[bool, str]:
    from .ai84 import AI84, AI84Hatasi
    anahtar = anahtar or A.anahtar("ai84")
    if not anahtar:
        return False, "AI84 anahtarı kayıtlı değil. Ayarlar'dan ekle."
    try:
        return True, f"AI84 anahtarı geçerli · {AI84(anahtar).krediler():,} kredi kaldı.".replace(",", ".")
    except AI84Hatasi as e:
        return False, str(e)


def calistir() -> dict:
    m = []
    m.append(_madde("Python", sys.version_info >= (3, 10), f"Python {sys.version.split()[0]}"))
    kok = yollar.kok()
    m.append(_madde("Kurulum klasörü", kok.is_dir() and os.access(kok, os.W_OK), str(kok)))
    eksik_prog = [p for p in ("ffmpeg", "ffprobe", "magick") if not program(p)]
    m.append(_madde("ffmpeg / ImageMagick", not eksik_prog,
                    "Hepsi kurulu." if not eksik_prog else "Eksik: " + ", ".join(eksik_prog) +
                    " ('1 - Ilk kurulum.cmd' dosyasını çalıştır; kurduktan sonra uygulamayı kapatıp yeniden aç)."))
    m.append(_madde("Pillow", _pillow(), "Kurulu" if _pillow() else "Maskot için gerekli. Uygulamayı yeniden aç (ilk açılışta kurulur).",
                    zorunlu=False))
    from .araclar import ARACLAR, araclar_klasoru
    eksik_arac = [x for x in ARACLAR if not (araclar_klasoru() / x).exists()]
    m.append(_madde("Montaj araçları", not eksik_arac, "Tam." if not eksik_arac else "Eksik: " + ", ".join(eksik_arac)))
    taslak = A.yol("capcut_taslak")
    tamam = taslak.is_dir() and os.access(taslak, os.W_OK)
    m.append(_madde("CapCut taslak klasörü", tamam, "Erişilebilir." if tamam else
                    f"{taslak} bulunamadı ya da yazılamıyor (CapCut kurulu mu? Ayarlar'dan yolu düzelt)."))
    if A.ayarlar().get("saglayici") == "openrouter":
        try:
            import anthropic  # noqa: F401
            m.append(_madde("OpenRouter kütüphanesi", True, "Kurulu"))
        except ImportError:
            m.append(_madde("OpenRouter kütüphanesi", False, "Kurulu değil. Uygulamayı .app ile yeniden aç (ilk açılışta kurulur)."))
        yazim = A.anahtar("openrouter")
        m.append(_madde("Yazım servisi: OpenRouter", bool(yazim),
                        "Anahtar kayıtlı." if yazim else "OpenRouter anahtarı kayıtlı değil. Ayarlar'dan ekle."))
    else:
        from . import claude_code
        ok, mesaj = claude_code.durum()
        m.append(_madde("Yazım servisi: Claude Code (abonelik)", ok, mesaj))
    m.append(_madde("Seslendirme anahtarı (AI84)", bool(A.anahtar("ai84")),
                    "kayıtlı" if A.anahtar("ai84") else "kayıtlı değil. Ayarlar'dan ekle."))
    akt = kanallar.aktif()
    if not akt:
        m.append(_madde("Kanal", False, "Henüz kanal yok. Kanal ekle."))
    else:
        c = kanallar.oku(akt)
        eks = kanallar.eksikler(akt)
        m.append(_madde(f"Kanal: {c['ad']}", not any(e["zorunlu"] for e in eks),
                        "Üretime hazır" if not eks else f"{len(eks)} not (kanal kartında)"))
    acik = capcut_acik()
    m.append(_madde("CapCut", not acik, "Kapalı." if not acik else
                    "Açık. Montaj adımından önce kapatman gerekecek.", zorunlu=False))
    return {"maddeler": m, "hazir": all(x["tamam"] for x in m if x["zorunlu"])}


def capcut_acik() -> bool:
    from .sistem_win import capcut_acik as acik
    return acik()
