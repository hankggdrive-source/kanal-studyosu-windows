"""Montaj araçlarını (uygulamanın araclar/ klasöründeki betikler) çağırır.

Betikler ilk sürümün Araclar betiklerinden taşındı; iş mantıkları aynıdır. Kanala özgü her şeyi ortam
değişkenlerinden alırlar:
  KS_KANAL   kanal klasörü (Videolar/, Arsiv/, Varliklar/ burada)
  KS_AYAR    kanal.json (dil, altyazı stili, maskot, müzik, hassas kelimeler, kalıp sayaçları)
  KS_ONEK    video kodu öneki
  KS_URETIM  ses/görsel/sahne videosu klasörlerinin kökü (Kanallar/<kanal>/Uretim)
  KS_CAPCUT  CapCut taslak klasörü
  KS_ARACLAR betiklerin klasörü
Betikler sistemdeki python3 ile çalışır (Pillow gibi kütüphaneler orada).
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import ayarlar as A
from . import kanal
from . import kayit
from . import yollar

ARACLAR = ("srt_uret.py", "odak_izgara.py", "capcut_taslak.py", "plan_kontrol.py", "senk_kontrol.py",
           "hassas_kelime_kontrol.py", "acilis_kapanis_defteri.py", "muzik_otomatik.py", "muzik_yatagi.py",
           "yayin_hazirla.py", "maskot_gom.py", "ortak.py", "capcut_efekt_verisi.json", "sablon_altyazi.json",
           "capcut_iskelet")


class AracHatasi(Exception):
    """Betik çalıştırılamadı (model hatası değil): kullanıcıya gösterilir, modele gitmez.
    ayrinti: betiğin çıktısının sonu (hata ekranında 'Ayrıntı' olarak gösterilir, kopyalanabilir)."""

    def __init__(self, mesaj: str, ayrinti: str = ""):
        super().__init__(mesaj)
        self.ayrinti = ayrinti


@dataclass
class Sonuc:
    kod: int
    cikti: str


def araclar_klasoru() -> Path:
    return yollar.KAYNAK / "araclar"


def _python() -> str:
    """Betikler uygulamanın kendi Python ortamında çalışır (Pillow orada kurulu). Konsol penceresi açmayan
    pythonw yerine python.exe kullanılır (betik çıktısı okunur)."""
    import sys
    py = Path(sys.executable)
    if py.name.lower() == "pythonw.exe" and (py.parent / "python.exe").exists():
        return str(py.parent / "python.exe")
    return str(py)


def ortam() -> dict:
    from .onkontrol import program
    ekler = [str(Path(p).parent) for p in (program("ffmpeg"), program("magick")) if p]
    yol_ = os.pathsep.join(ekler + [os.environ.get("PATH", "")])
    return dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PATH=yol_, KS_KANAL=str(kanal.kok()),
                KS_AYAR=str(kanal.kok() / "kanal.json"), KS_ONEK=kanal.onek(), KS_URETIM=str(kanal.uretim_klasoru()),
                KS_CAPCUT=str(A.yol("capcut_taslak")), KS_ARACLAR=str(araclar_klasoru()), KS_PYTHON=_python())


def calistir(betik: str, *argumanlar: str, zaman_asimi: int = 1800) -> Sonuc:
    yol = araclar_klasoru() / betik
    if not yol.exists():
        raise AracHatasi(f"araclar/{betik} bulunamadı.")
    komut = [_python(), str(yol)] + list(argumanlar)
    kayit.yaz(f"Araç: {betik} {' '.join(argumanlar)}")
    try:
        from .sistem_win import gizli
        p = subprocess.run(komut, cwd=str(yol.parent), env=ortam(), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=zaman_asimi, **gizli())
    except subprocess.TimeoutExpired:
        raise AracHatasi(f"{betik} {zaman_asimi // 60} dakikada bitmedi.")
    cikti = (p.stdout or "") + (("\n" + p.stderr) if p.stderr.strip() else "")
    if p.returncode != 0:
        kayit.yaz(f"{betik} hata verdi:\n{cikti[-2000:]}", "hata")
        raise AracHatasi(f"{betik} hata verdi.", f"$ {betik} {' '.join(argumanlar)}\n{cikti[-4000:]}")
    return Sonuc(p.returncode, cikti)


# --- Belirli betiklerin çıktıları ------------------------------------------------

def plan_kontrol(tsv_yolu: str, sahne_sayisi: int) -> dict:
    """→ {'temiz': bool, 'hatalar': [...], 'maskot': '--maskot 10:1:2 …', 'kes': '70.3'}"""
    c = calistir("plan_kontrol.py", str(tsv_yolu), str(sahne_sayisi)).cikti
    son = next((s for s in reversed(c.splitlines()) if s.startswith(("TEMIZ", "HATA"))), "")
    hatalar = []
    if "[" in son:  # betik listeyi Python biçiminde yazar; tırnak içeren mesajlar da doğru ayrılsın
        try:
            hatalar = [str(h) for h in ast.literal_eval(son[son.find("["):].strip())]
        except (ValueError, SyntaxError):
            hatalar = re.findall(r"'([^']*)'", son[son.find("["):])
    # Maskotsuz kanalda satır boştur; yalnız kendi satırı okunur (alt satırdaki "TEMIZ []" karışmasın).
    m = re.search(r"yayin_hazirla maskot:[ \t]*([^\n]*)", c)
    k = re.search(r"KES %\s*([\d.]+)", c)
    return {"temiz": son.startswith("TEMIZ"), "hatalar": hatalar, "maskot": m.group(1).strip() if m else "",
            "kes": k.group(1) if k else ""}


def hassas_kelime(kod: str) -> dict:
    """→ {'temiz': bool, 'paketleme': [...], 'metin': [...]} (betik Videolar/<kod>/04 ve 02'yi okur)."""
    c = calistir("hassas_kelime_kontrol.py", kod).cikti
    satirlar = [s.strip() for s in c.splitlines() if s.strip()]
    return {"temiz": any("TEMIZ" in s for s in satirlar[:1]),
            "paketleme": [s for s in satirlar if s.startswith("paketleme satir")],
            "metin": [s for s in satirlar if s.startswith("metin ilk 30 sn")]}


def acilis_kapanis() -> str:
    """Kanal klasöründeki Acilis_Kapanis_Defteri.md'yi yeniden üretir ve içeriğini döndürür."""
    calistir("acilis_kapanis_defteri.py")
    return (kanal.kok() / "Acilis_Kapanis_Defteri.md").read_text(encoding="utf-8")
