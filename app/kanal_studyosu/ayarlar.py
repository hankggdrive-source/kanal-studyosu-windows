"""Genel ayarlar (bütün kanallar için ortak), JSON yardımcıları ve API anahtarları.

Varsayılanlar config/varsayilan.json'dan gelir; kullanıcının değiştirdikleri kurulum klasöründeki
Sistem/ayarlar.json'da tutulur. Kanala özgü ayarlar kanalın kendi kanal.json dosyasındadır (kanallar.py).
"""
from __future__ import annotations

import copy
import json
import os
import platform
import re
import subprocess
import threading
from pathlib import Path

from . import yollar

UYGULAMA = "Kanal Stüdyosu"
SURUM = "1.2.3-windows"

ANAHTAR_SERVIS = "studio.kanal"
# Yazım servisleri: Claude Code (abonelik; anahtar gerekmez) ve OpenRouter. Doğrudan Anthropic API kaldırıldı.
SAGLAYICILAR = ("claude_code", "openrouter")
ANAHTARLAR = {"ai84": (ANAHTAR_SERVIS, "ai84-api-key", "AI84_API_KEY"),
              "openrouter": (ANAHTAR_SERVIS, "openrouter-api-key", "OPENROUTER_API_KEY")}

_KILIT = threading.RLock()


def atomik_yaz(yol: Path, metin: str) -> None:
    """Önce geçici dosyaya yazar, sonra yer değiştirir (yarım dosya kalmaz)."""
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = yol.with_name(yol.name + ".tmp")
    with _KILIT:
        with open(gecici, "w", encoding="utf-8") as f:
            f.write(metin)
            f.flush()
            os.fsync(f.fileno())
        os.replace(gecici, yol)


def json_yaz(yol: Path, veri) -> None:
    atomik_yaz(yol, json.dumps(veri, ensure_ascii=False, indent=2))


def json_oku(yol: Path, varsayilan=None):
    try:
        return json.loads(Path(yol).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return copy.deepcopy(varsayilan)


def birlestir(taban: dict, ust: dict) -> dict:
    sonuc = copy.deepcopy(taban)
    for k, v in ust.items():
        if isinstance(v, dict) and isinstance(sonuc.get(k), dict):
            sonuc[k] = birlestir(sonuc[k], v)
        else:
            sonuc[k] = copy.deepcopy(v)
    return sonuc


def varsayilan() -> dict:
    return json.loads((yollar.CONFIG / "varsayilan.json").read_text(encoding="utf-8"))


def genel() -> dict:
    """Yalnız genel ayarlar (bütün kanallar için ortak)."""
    a = birlestir(varsayilan(), json_oku(yollar.ayar_dosyasi(), {}) or {})
    if a.get("saglayici") not in SAGLAYICILAR:  # eski sürümde "anthropic" seçilmiş olabilir
        a["saglayici"] = "claude_code"
    return a


# Üretim kodundaki iş adları → kanal.json'daki iş adları
IS_ESLEME = {"A1": "konu", "A2": "arastirma", "A3": "senaryo", "A4": "ceviri", "A5": "sahne", "A6": "paketleme",
             "A6_2": "bolumler", "A6_2_yedek": "bolumler_yedek"}


def ayarlar() -> dict:
    """Genel ayarlar + seçili kanalın modelleri, sesi, video ayarları ve video bütçesi (üretim kodu buradan okur)."""
    from . import kanallar
    a = genel()
    akt = kanallar.aktif()
    k = kanallar.oku(akt) if akt else kanallar.varsayilan()
    a["isler"] = {ic: k["isler"][dis] for ic, dis in IS_ESLEME.items() if dis in k["isler"]}
    a["isler"].update({ad: v for ad, v in k["isler"].items() if ad not in IS_ESLEME.values()})
    a["ses"] = dict(k["ses"])
    a["video"] = dict(k["montaj"]["video"])
    a["butce"]["video_usd"] = k["butce"]["video_usd"]
    return a


IZINLI = {"yollar", "butce", "onbellek_suresi", "duzeltme_tur_siniri", "saglayici"}


def ayar_kaydet(degisiklik: dict) -> dict:
    """Yalnızca bilinen alanları kullanıcı dosyasına yazar."""
    kullanici = json_oku(yollar.ayar_dosyasi(), {}) or {}
    for k, v in degisiklik.items():
        if k not in IZINLI:
            raise ValueError(f"Bilinmeyen ayar: {k}")
        kullanici[k] = birlestir(kullanici[k], v) if isinstance(v, dict) and isinstance(kullanici.get(k), dict) else v
    yeni = birlestir(varsayilan(), kullanici)
    _dogrula(yeni)
    json_yaz(yollar.ayar_dosyasi(), kullanici)
    return yeni


def _dogrula(a: dict) -> None:
    if float(a["butce"]["aylik_usd"]) <= 0:
        raise ValueError("Aylık bütçe sıfırdan büyük olmalı")
    if a.get("saglayici", "claude_code") not in SAGLAYICILAR:
        raise ValueError("Yazım servisi Claude Code ya da OpenRouter olmalı")
    if a["onbellek_suresi"] not in ("5m", "1h"):
        raise ValueError("Önbellek süresi 5m ya da 1h olmalı")


def yol(ad: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(genel()["yollar"][ad])))


# --- Anahtarlar (Windows Kimlik Bilgisi Yöneticisi; keyring yoksa ortam değişkeni) ---

def anahtar(tur: str) -> str:
    from . import sistem_win
    servis, hesap, ortam = ANAHTARLAR[tur]
    return sistem_win.anahtar_oku(servis, hesap, ortam)


def anahtar_kaydet(tur: str, deger: str) -> None:
    servis, hesap, _ = ANAHTARLAR[tur]
    deger = str(deger).strip()
    if not re.fullmatch(r"[A-Za-z0-9_\-.:+/=]{8,512}", deger):
        raise ValueError("Anahtar beklenen biçimde değil")
    from . import sistem_win
    sistem_win.anahtar_yaz(servis, hesap, deger)


def anahtar_sil(tur: str) -> None:
    from . import sistem_win
    servis, hesap, _ = ANAHTARLAR[tur]
    sistem_win.anahtar_sil(servis, hesap)

