"""Kurulum klasörü ve uygulamanın kendi klasörleri.

Uygulama, kullanıcının seçtiği klasöre kopyalanır; ilk açılışta o klasörün içinde Sistem/ ve Kanallar/ kurulur.
Kök klasör sırasıyla: KANAL_STUDYOSU_KOK ortam değişkeni (başlatıcı .app'in bulunduğu klasörü verir) → geliştirme
sırasında depo içindeki calisma/ klasörü.
"""
from __future__ import annotations

import os
from pathlib import Path

KAYNAK = Path(__file__).resolve().parent.parent          # program dosyaları (config/, sablonlar/)
CONFIG = KAYNAK / "config"
SABLONLAR = KAYNAK / "sablonlar"


def kok() -> Path:
    return Path(os.environ.get("KANAL_STUDYOSU_KOK") or (KAYNAK / "calisma")).expanduser().resolve()


def sistem() -> Path:
    return kok() / "Sistem"


def kanallar() -> Path:
    return kok() / "Kanallar"


def ayar_dosyasi() -> Path:
    return sistem() / "ayarlar.json"


def maliyet_dosyasi() -> Path:
    return sistem() / "maliyet.jsonl"


def aktif_dosyasi() -> Path:
    return sistem() / "aktif.json"


def calisan_dosyasi() -> Path:
    """Açık kopyanın adresi (tek_kopya)."""
    return sistem() / "calisan.json"


def kayit_dosyasi() -> Path:
    return sistem() / "kayit.log"


def kur() -> list[str]:
    """İlk açılışta (ve her açılışta, eksikse) klasör düzenini kurar. Var olan hiçbir şeye dokunmaz."""
    olusan = []
    for k in (sistem(), kanallar()):
        if not k.exists():
            k.mkdir(parents=True)
            olusan.append(str(k))
    return olusan
