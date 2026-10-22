"""Model cevabını dosyalara, yamalara ve sohbet özetine ayırır.

Uygulama çerçevesi modele şu biçimi söyler:
  <dosya ad="ORN-VID-06_3_senaryo_tr.md"> … </dosya>
  <yama dosya="…" paragraf="12" [islem="sil|sonrasina_ekle"]> … </yama>
  <yama dosya="…" satir="Başlık"> … </yama>
  <yama dosya="…" bolum="§4"> … </yama>
  <yama dosya="…" kuyruk="1"> … </yama>
  <ozet> … </ozet>
  Açık noktalar: ¶12 … | yok   (sohbet cevabının son satırı; ayrı alana alınır)
Etiket yoksa ve beklenen dosya sayısı kadar kod bloğu varsa, bloklar sırayla
dosyalara eşlenir (becerilerdeki "dosya aracı yoksa kod bloğu" kuralı).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

DOSYA = re.compile(r'<dosya\s+ad="([^"]+)"\s*>(.*?)</dosya>', re.S)
YAMA = re.compile(r"<yama\s+([^>]*)>(.*?)</yama>", re.S)
OZET = re.compile(r"<ozet>(.*?)</ozet>", re.S)
OZNITELIK = re.compile(r'(\w+)="([^"]*)"')
KOD_BLOGU = re.compile(r"```[^\n]*\n(.*?)\n```", re.S)
# Sohbet cevabının sonundaki düz yazı satır: "Açık noktalar: ¶12 … " ya da "Açık noktalar: yok".
# Dosyalardan ayrı tutulur ve ekranda ayrı gösterilir; seslendirmeye ya da sahne akışına gitmez.
ACIK = re.compile(r"^[ \t>*_-]*Açık noktalar[ \t*_]*:[ \t*_]*(.*?)[ \t*_]*$", re.M | re.I)


@dataclass
class Ayrisma:
    dosyalar: dict[str, str] = field(default_factory=dict)
    yamalar: dict[str, list[dict]] = field(default_factory=dict)
    ozet: str = ""
    acik_noktalar: str = ""


def _cit_temizle(icerik: str) -> str:
    """Dosya içeriği bir kod bloğuna sarılmışsa çitleri kaldırır."""
    s = icerik.strip("\n")
    m = re.fullmatch(r"\s*```[^\n]*\n(.*?)\n```\s*", s, re.S)
    return (m.group(1) if m else s).strip("\n") + "\n"


def ayristir(metin: str, beklenen: list[str] | None = None) -> Ayrisma:
    a = Ayrisma()
    for ad, icerik in DOSYA.findall(metin):
        a.dosyalar[ad.strip()] = _cit_temizle(icerik)
    for oz, icerik in YAMA.findall(metin):
        o = dict(OZNITELIK.findall(oz))
        if "dosya" not in o:
            continue
        y: dict = {"icerik": icerik.strip("\n")}
        if "paragraf" in o:
            y["paragraf"] = int(o["paragraf"])
            y["islem"] = o.get("islem", "degistir")
        elif "satir" in o:
            y["satir"] = o["satir"]
        elif "bolum" in o:
            y["bolum"] = o["bolum"]
        elif o.get("kuyruk"):
            y["kuyruk"] = True
        else:
            continue
        a.yamalar.setdefault(o["dosya"].strip(), []).append(y)
    disari = YAMA.sub("", DOSYA.sub("", metin))  # dosya/yama içerikleri hariç sohbet metni
    acik = ACIK.findall(re.sub(r"</?ozet>", "\n", disari))
    if acik:
        a.acik_noktalar = acik[-1].strip().strip("«»\"'`").strip()  # «yok» → yok
    m = OZET.search(metin)
    if m:
        a.ozet = ACIK.sub("", m.group(1)).strip()
    if not a.dosyalar and not a.yamalar and beklenen:
        bloklar = KOD_BLOGU.findall(metin)
        if len(bloklar) == len(beklenen):
            a.dosyalar = {ad: b.strip("\n") + "\n" for ad, b in zip(beklenen, bloklar)}
    if not a.ozet:
        kalan = ACIK.sub("", OZET.sub("", disari)).strip()
        a.ozet = kalan[:3000]
    return a
