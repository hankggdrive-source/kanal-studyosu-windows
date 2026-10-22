"""Dosya düzeni ve silme politikası.

- Bu modül hiçbir dosyayı SİLMEZ; yalnızca taşır.
- Videolar/<KOD> içinde yalnızca sonuç dosyaları kalır; fazlası Arsiv/<KOD>'a taşınır.
- Üretim bitince silme adayları listelenir; kullanıcı cevap vermezse Silinecekler/<KOD>'a
  (klasör yapısı korunarak) taşınır. Kullanıcı kendisi siler.
"""
from __future__ import annotations

import fnmatch
import shutil
from datetime import datetime
from pathlib import Path

from . import kanal

SONUC_DOSYALARI = ("01_OKU_BENI.md", "02_ElevenLabs_seslendirme_metni.txt", "03_Gorsel_promptlari.txt",
                   "04_Paketleme_ve_Veo3.md", "05_Montaj_plani.tsv", "06_Odak_noktalari.json",
                   "{kod}_altyazi_{dil}.srt", "flow_indirilen")
# Flow devri sürerken geçici olarak izinli (içe almadan sonra arşive taşınır).
GECICI = ("flow_istek", "flow_cikti")
# Asla silme kapsamına girmez.
KORUNAN = ("*.mp4", "tam_yedek_*", "draft_info_*_oncesi.json", "Skill_eski_*", "eski_muzik_*")


def izinli(kod: str) -> set[str]:
    return {s.format(kod=kod, dil=kanal.hedef_dil()) for s in SONUC_DOSYALARI} | set(GECICI)


def fazlalar(kod: str) -> list[Path]:
    v = kanal.video_klasoru(kod)
    if not v.is_dir():
        return []
    return sorted(p for p in v.iterdir() if p.name not in izinli(kod) and p.name != ".DS_Store")


def _bos_ad(hedef: Path) -> Path:
    if not hedef.exists():
        return hedef
    damga = datetime.now().strftime("%Y%m%d_%H%M%S")
    return hedef.with_name(f"{hedef.stem}_{damga}{hedef.suffix}")


def fazlalari_arsive_tasi(kod: str) -> list[str]:
    tasinan = []
    for p in fazlalar(kod):
        hedef = _bos_ad(kanal.arsiv_klasoru(kod) / p.name)
        hedef.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(hedef))
        tasinan.append(p.name)
    return tasinan


def korunuyor_mu(yol: Path) -> bool:
    if kanal.kok() / "Videolar" in yol.parents or yol == kanal.kok() / "Videolar":
        return True
    return any(fnmatch.fnmatch(yol.name, k) for k in KORUNAN)


def silme_adaylari(kod: str) -> list[Path]:
    """Arsiv/<KOD> içindeki büyük ara dosyalar: Flow zip'leri, kontak/odak sayfaları, ara yedekler."""
    a = kanal.arsiv_klasoru(kod)
    if not a.is_dir():
        return []
    desen = ("*.zip", "kontak*.jpg", "odak", "flow_v*", "draft_info_yayin_oncesi.json")
    adaylar = [p for p in a.iterdir() if any(fnmatch.fnmatch(p.name, d) for d in desen)]
    return sorted((p for p in adaylar if not korunuyor_mu(p)), key=lambda p: p.name)


def silineceklere_tasi(kod: str, yollar: list[Path]) -> list[str]:
    hedef_kok = kanal.kok() / "Silinecekler" / kod
    tasinan = []
    for p in yollar:
        p = Path(p)
        if korunuyor_mu(p) or kanal.kok() not in p.parents:
            continue
        hedef = _bos_ad(hedef_kok / p.relative_to(kanal.arsiv_klasoru(kod) if kanal.arsiv_klasoru(kod) in p.parents
                                                  else kanal.kok()))
        hedef.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(hedef))
        tasinan.append(hedef.relative_to(kanal.kok()).as_posix())
    return tasinan
