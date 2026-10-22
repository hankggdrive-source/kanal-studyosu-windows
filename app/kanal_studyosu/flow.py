"""Flow adımı: klasör tabanlı devir (uygulama ↔ Claude masaüstü ajanı). Playwright yok.

Adaptör arayüzü: istek_hazirla → durum (bekle) → dogrula → ice_al.
- Uygulama Flow'a hiç bağlanmaz; görselleri kullanıcının Claude masaüstü sohbetindeki ajan üretir.
- Ajan görselleri/zip'i flow_cikti/'ye koyar ve BITTI.json yazar; sorun olursa SORUN.md.
- Yarı elle yedek yol: partiler ekranda "Kopyala" ile verilir, kullanıcı zip'i flow_cikti/'ye bırakır.
Hiçbir dosya silinmez; işlenen sinyal dosyaları ve klasörler arşive taşınır.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

from . import ayarlar as A
from . import kanal
from . import kontroller as K



def boyut() -> tuple[int, int]:
    """Flow'un indirdiği görsel ölçüsü: 16:9 → 1376x768, 9:16 → 768x1376."""
    return (768, 1376) if kanal.ayar()["gorsel"].get("oran") == "9:16" else (1376, 768)


PARTI = 5
AD = re.compile(r"^sahne(\d{4})(?:[_\-. ].*)?\.(jpe?g|png)$", re.I)

def ajan_talimati_flow() -> str:
    g = kanal.ayar()["gorsel"]
    oran, model = g.get("oran", "16:9"), g.get("flow_model", "Nano Banana 2")
    yon = "9:16 portrait aspect ratio (tall vertical, e.g. 1080x1920), never 1:1 square and never landscape" \
        if oran == "9:16" else "16:9 landscape aspect ratio (wide horizontal, e.g. 1920x1080), never 1:1 square and never portrait"
    kar = f", even when the {g['karakter']} character reference image is attached" if g.get("karakter") else ""
    return (f"Always generate every image in {yon}{kar}: always set the aspect ratio parameter to {oran} explicitly. "
            f"Generate exactly one image (x1) per prompt, using the {model} model. " + _AJAN_DEVAM)


_AJAN_DEVAM = (
    "Work "
    "through the whole prompt list in order, 5 at a time, without stopping to ask for confirmation between batches. "
    "If a generation fails, retry that same prompt at most 2 times, then skip it and continue; never send the same "
    "prompt more than 3 times in total. Name each image right after it is created: first prompt = sahne0001, second = "
    "sahne0002, and so on. Do not generate a prompt again if it already has a successful image. Keep your chat replies "
    "very short.")


def istek_klasoru(kod: str) -> Path:
    return kanal.video_klasoru(kod) / "flow_istek"


def cikti_klasoru(kod: str) -> Path:
    return kanal.video_klasoru(kod) / "flow_cikti"


def promptlar(kod: str) -> list[str]:
    return K.bloklar((kanal.video_klasoru(kod) / "03_Gorsel_promptlari.txt").read_text(encoding="utf-8"))


def talimat_metni(kod: str, proje_adi: str, klasor: Path, sadece: list[int] | None) -> str:
    kapsam = (f"Yalnız şu sahneleri üret: {', '.join(f'sahne{n:04d}' for n in sadece)} (eksikler.json). "
              "Aynı Flow projesinde devam et; var olan görsellere dokunma.") if sadece else \
        f"Flow'da yeni proje aç: adı `{proje_adi}`."
    g = kanal.ayar()["gorsel"]
    kar = g.get("karakter", "")
    kanal_adi, model, oran = kanal.ayar()["ad"], g.get("flow_model", "Nano Banana 2"), g.get("oran", "16:9")
    karakter_adimi = f"{kar} karakterini ekle (Flow'daki karakter), " if kar else ""
    karakter_kontrol = f" ve {kar} karakterinin tutarlı olduğunu" if kar else ""
    yon = "dikey" if oran == "9:16" else "yatay"
    return f"""# Flow üretimi · {kod}

Bu klasörü Kanal Stüdyosu hazırladı ({kanal_adi}). Görevin yalnızca Flow'da görsel üretmek. Başka hiçbir iş yapma; proje dosyalarını okuma.

**Klasör:** `{klasor}`

1. `istek.json` ve `promptlar.txt` dosyalarını oku. Promptlar sırayla, her biri tek paragraf; 1. prompt = sahne0001.
2. {kapsam}
3. {karakter_adimi}ayarları yap: "Hiçbir zaman", x1, model tam "{model}", {oran}. Ajan talimatı `istek.json` → `flow_ajan_talimati`.
4. Promptları **beşerli partiler** hâlinde gönder (`istek.json` → `partiler`). Asla hepsini tek mesajda verme. Her partiden sonra bitmesini bekle; ilk iki partiden sonra görsellerin {yon} olduğunu{karakter_kontrol} kontrol et. "Tekrar dene"ye basma.
5. Bitince projeyi indir ve zip'i (ya da `sahneNNNN_*.jpg` görselleri) şu klasöre koy: `{klasor.parent / 'flow_cikti'}`
6. Son olarak aynı klasöre `BITTI.json` yaz: `{{"kod": "{kod}", "uretilen": <sayı>, "notlar": "<varsa kısa not>"}}`
7. Bir sahne Flow politikasına takılır ya da çıkmazsa promptu kendin değiştirme. Sahne numarasını ve Flow'un mesajını `flow_cikti/SORUN.md` dosyasına yaz, sonra `BITTI.json` yaz.

Şifre girme. Oturum düşerse dur ve kullanıcıdan giriş iste.
"""


def istek_hazirla(kod: str, kisa_konu: str, sadece: list[int] | None = None) -> dict:
    P = promptlar(kod)
    numaralar = sadece or list(range(1, len(P) + 1))
    partiler = [{"sahneler": [f"sahne{n:04d}" for n in numaralar[i:i + PARTI]],
                 "promptlar": [P[n - 1] for n in numaralar[i:i + PARTI]]}
                for i in range(0, len(numaralar), PARTI)]
    proje = f"{kod} {kisa_konu}".strip()
    k = istek_klasoru(kod)
    istek = {"kod": kod, "proje_adi": proje, "toplam_sahne": len(P), "uretilecek": len(numaralar),
             "sadece_eksikler": bool(sadece), "partiler": partiler,
             "kanal": kanal.ayar()["ad"], "karakter": kanal.ayar()["gorsel"].get("karakter", ""),
             "ayarlar": {"oran": kanal.ayar()["gorsel"].get("oran", "16:9"), "adet": "x1",
                         "model": kanal.ayar()["gorsel"].get("flow_model", "Nano Banana 2"), "onay": "Hiçbir zaman"},
             "flow_ajan_talimati": ajan_talimati_flow(),
             "beklenen_cikti": {"bicim": "zip ya da jpg", "boyut": "{}x{}".format(*boyut()), "ad": "sahneNNNN_*.jpg"},
             "hazirlanma": datetime.now().isoformat(timespec="seconds")}
    A.json_yaz(k / "istek.json", istek)
    A.atomik_yaz(k / "promptlar.txt", "\n\n".join(P) + "\n")
    A.atomik_yaz(k / "TALIMAT_AJAN.md", talimat_metni(kod, proje, k, sadece))
    if sadece:
        A.json_yaz(k / "eksikler.json", {"sahneler": [f"sahne{n:04d}" for n in sadece]})
    cikti_klasoru(kod).mkdir(parents=True, exist_ok=True)
    return istek


def ajan_komutu(kod: str) -> str:
    return f"`kanal-studyosu-flow` becerisini kullan. Klasör: {istek_klasoru(kod)}"


def _gorseller(klasor: Path) -> dict[int, list[Path]]:
    by: dict[int, list[Path]] = {}
    for f in klasor.rglob("*"):
        m = AD.match(f.name)
        if f.is_file() and m and "__MACOSX" not in f.parts:
            by.setdefault(int(m.group(1)), []).append(f)
    return by


def durum(kod: str) -> dict:
    c = cikti_klasoru(kod)
    if not c.is_dir():
        return {"var": False}
    sorun = c / "SORUN.md"
    return {"var": True, "gorsel": len(_gorseller(c)), "zip": len(list(c.glob("*.zip"))),
            "bitti": (c / "BITTI.json").exists(),
            "sorun": sorun.read_text(encoding="utf-8")[:4000] if sorun.exists() else ""}


def _boyut(f: Path) -> tuple[int, int] | None:
    from .onkontrol import _program
    q = subprocess.run([_program("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0:s=x", str(f)], capture_output=True, text=True)
    m = re.match(r"(\d+)x(\d+)", q.stdout.strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def _ziplari_ac(kod: str) -> None:
    for z in cikti_klasoru(kod).glob("*.zip"):
        hedef = cikti_klasoru(kod) / f"_acilan_{z.stem}"
        if hedef.exists():
            continue
        try:
            with zipfile.ZipFile(z) as zf:
                if zf.testzip() is not None:
                    raise zipfile.BadZipFile("bozuk dosya")
                zf.extractall(hedef)
        except zipfile.BadZipFile:
            raise ValueError(f"{z.name} açılamadı (indirme yarım kalmış olabilir).")


def dogrula(kod: str) -> dict:
    """→ {'tamam': bool, 'eksik': [n], 'boyut': [..], 'cift': [..], 'secilen': {n: yol}}"""
    _ziplari_ac(kod)
    toplam = len(promptlar(kod))
    by = _gorseller(cikti_klasoru(kod))
    # Daha önce içe alınmış görseller (yalnız eksikler turu) de sayılır.
    onceki = _gorseller(kanal.video_klasoru(kod) / "flow_indirilen") if \
        (kanal.video_klasoru(kod) / "flow_indirilen").is_dir() else {}
    secilen, hatali, cift, beklenen = {}, [], [], boyut()
    for n in range(1, toplam + 1):
        adaylar = by.get(n) or onceki.get(n) or []
        if not adaylar:
            continue
        if len(adaylar) > 1:
            cift.append(f"sahne{n:04d}: {len(adaylar)} görsel var, en yenisi alındı")
        f = max(adaylar, key=lambda p: p.stat().st_mtime)
        b = _boyut(f)
        if b != beklenen:
            hatali.append(f"sahne{n:04d}: {b[0]}x{b[1]}" if b else f"sahne{n:04d}: okunamadı")
            continue
        secilen[n] = f
    eksik = [n for n in range(1, toplam + 1) if n not in secilen]
    return {"tamam": not eksik, "toplam": toplam, "eksik": eksik, "boyut": hatali, "cift": cift,
            "secilen": {n: str(p) for n, p in secilen.items()}}


def ice_al(kod: str, secilen: dict) -> Path:
    """Görselleri Videolar/<kod>/flow_indirilen/'e kopyalar; istek/çıktı klasörlerini arşive taşır."""
    hedef = kanal.video_klasoru(kod) / "flow_indirilen"
    hedef.mkdir(exist_ok=True)
    for n, yol in secilen.items():
        yol = Path(yol)
        if hedef in yol.parents:
            continue
        shutil.copy2(yol, hedef / yol.name)
    sinyal_arsivle(kod, tumu=True)
    return hedef


def sinyal_arsivle(kod: str, tumu: bool = False) -> None:
    """BITTI.json/SORUN.md (ya da tumu=True ise flow_istek ve flow_cikti) arşive taşınır; silinmez."""
    damga = datetime.now().strftime("%Y%m%d_%H%M%S")
    a = kanal.arsiv_klasoru(kod) / f"flow_devri_{damga}"
    if tumu:
        for k in (istek_klasoru(kod), cikti_klasoru(kod)):
            if k.exists():
                a.mkdir(parents=True, exist_ok=True)
                shutil.move(str(k), str(a / k.name))
        return
    for ad in ("BITTI.json", "SORUN.md"):
        f = cikti_klasoru(kod) / ad
        if f.exists():
            a.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(a / ad))


def secilenler_klasorden(kod: str) -> dict[int, Path]:
    """İçe alınmış görseller: sahne no → dosya (Studio'ya verilecek)."""
    by = _gorseller(kanal.video_klasoru(kod) / "flow_indirilen")
    return {n: max(v, key=lambda p: p.stat().st_mtime) for n, v in by.items()}
