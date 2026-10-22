"""Seçili kanalın klasörü ve ayarları (üretim modüllerinin kullandığı katman).

İlk (tek kanallı) sürümdeki kanal.py ile aynı arayüz; yollar sabit bir kanal klasörü yerine seçili kanalın klasöründen
(Kanallar/<kisaltma>/) gelir. Üretim sürerken kanal değiştirilemediği için "seçili kanal" üretimin kanalıdır.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from . import ayarlar as A
from . import kanallar

YONETICI, ANAYASA, DEFTER, AKTIF = kanallar.PROJE_DOSYALARI
PROJE_DOSYALARI = kanallar.PROJE_DOSYALARI
BECERILER = tuple(a for a, _ in kanallar.ASAMALAR)


def secili() -> str:
    k = kanallar.aktif()
    if not k:
        raise ValueError("Seçili kanal yok. Önce bir kanal ekle.")
    return k


def ayar() -> dict:
    return kanallar.oku(secili())


def kok() -> Path:
    return kanallar.klasor(secili())


def proje_klasoru() -> Path:
    return kok() / "Proje_dosyalari"


def rit(ad: str) -> str:
    """Proje dosyası (00_Yonetici.md … 03_Aktif_Video.md)."""
    return (proje_klasoru() / ad).read_text(encoding="utf-8")


def beceri(ad: str) -> str:
    return (kok() / "Beceriler" / ad / "SKILL.md").read_text(encoding="utf-8")


def onek() -> str:
    return ayar()["kod_oneki"]


def hedef_dil() -> str:
    return ayar()["dil"]["hedef"]


def dil_adi(kod: str | None = None) -> str:
    kod = kod or hedef_dil()
    return kanallar.DILLER.get(kod, kod)


def ceviri_var() -> bool:
    """Hedef dil Türkçe ise 4. aşama (hedef dilde yeniden yazım) atlanır."""
    return hedef_dil() != "tr"


def kod_deseni() -> re.Pattern:
    return re.compile(rf"^{re.escape(onek())}-(\d{{2,3}})$")


class _Kod:
    """Eski KOD sabitinin yerine: kanal.KOD.match(...) seçili kanalın önekine göre çalışır."""

    def match(self, s: str):
        return kod_deseni().match(s or "")


KOD = _Kod()


def kod_yap(n: int) -> str:
    return f"{onek()}-{n:0{int(ayar().get('kod_hane', 2))}d}"


def video_klasoru(kod: str) -> Path:
    return kok() / "Videolar" / kod


def arsiv_klasoru(kod: str) -> Path:
    return kok() / "Arsiv" / kod


def uygulama_klasoru(kod: str) -> Path:
    """Uygulamanın durum ve konuşma kayıtları (Videolar temiz kalsın diye arşivde)."""
    return arsiv_klasoru(kod) / "_uygulama"


def uretim_klasoru() -> Path:
    """Ses, görsel ve sahne videolarının üretildiği yer (ilk sürümdeki Creator Projects'in karşılığı)."""
    return kok() / "Uretim"


def altyazi_adi(kod: str) -> str:
    return f"{kod}_altyazi_{hedef_dil()}.srt"


def mevcut_kodlar() -> list[str]:
    v = kok() / "Videolar"
    if not v.is_dir():
        return []
    d = kod_deseni()
    return sorted((p.name for p in v.iterdir() if p.is_dir() and d.match(p.name)), key=lambda k: int(d.match(k).group(1)))


def defter_tablosu(defter: str | None = None) -> list[dict]:
    """Kanal Defteri A tablosundaki video satırları."""
    if defter is None:
        try:
            defter = rit(DEFTER)
        except FileNotFoundError:
            return []
    d = kod_deseni()
    satirlar, basliklar = [], None
    for s in defter.splitlines():
        if not s.startswith("|"):
            if basliklar and satirlar:
                break
            continue
        hucre = [h.strip() for h in s.strip().strip("|").split("|")]
        if hucre and hucre[0] == "Kod":
            basliklar = hucre
            continue
        if basliklar and hucre and d.match(hucre[0]):
            satirlar.append(dict(zip(basliklar, hucre)))
    return satirlar


def siradaki_kod() -> str:
    d = kod_deseni()
    numaralar = [int(d.match(k).group(1)) for k in mevcut_kodlar()]
    numaralar += [int(d.match(s["Kod"]).group(1)) for s in defter_tablosu()]
    numaralar += [int(d.match(k).group(1)) for k in (A.json_oku(uretim_listesi_yolu(), {}) or {}).get("videolar", {})
                  if d.match(k)]
    return kod_yap((max(numaralar) if numaralar else 0) + 1)


def uretim_listesi_yolu() -> Path:
    return kok() / "uretim_listesi.json"


def uretim_listesi() -> dict:
    """İlk açılışta Videolar + Kanal Defteri'nden oluşturulur; sonra yalnızca güncellenir."""
    yol = uretim_listesi_yolu()
    liste = A.json_oku(yol, None)
    if liste is None:
        liste = {"olusturma": datetime.now().isoformat(timespec="seconds"), "videolar": {}}
    defter = {s["Kod"]: s for s in defter_tablosu()}
    d = kod_deseni()
    degisti = False
    for kod in sorted(set(mevcut_kodlar()) | set(defter), key=lambda k: int(d.match(k).group(1))):
        if kod in liste["videolar"]:
            continue
        s = defter.get(kod, {})
        m = re.match(r"\s*([\d:]+)\s*/\s*(\d+)", s.get("Süre / sahne", ""))
        liste["videolar"][kod] = {"kod": kod, "baslik": s.get("Nihai başlık", ""), "durum": s.get("Durum", ""),
                                  "sure": m.group(1) if m else "", "sahne": int(m.group(2)) if m else None,
                                  "klasor": str(video_klasoru(kod)), "salt_okunur": True}
        degisti = True
    if degisti:
        A.json_yaz(yol, liste)
    return liste


def liste_guncelle(kod: str, **alanlar) -> None:
    liste = uretim_listesi()
    v = liste["videolar"].setdefault(kod, {"kod": kod, "klasor": str(video_klasoru(kod)), "salt_okunur": False})
    v.update(alanlar)
    A.json_yaz(uretim_listesi_yolu(), liste)


def rit03_yenile(kod: str, yeni_metin: str) -> Path:
    """03_Aktif_Video.md'yi yeniler; eski hâli silinmez, video arşivine kopyalanır."""
    yol = proje_klasoru() / AKTIF
    if yol.exists():
        eski = yol.read_text(encoding="utf-8")
        if eski != yeni_metin:
            A.atomik_yaz(arsiv_klasoru(kod) / f"03_Aktif_Video_oncesi_{datetime.now():%Y%m%d_%H%M%S}.md", eski)
    A.atomik_yaz(yol, yeni_metin)
    return yol


# --- modele giden KANAL AYARLARI bloğu --------------------------------------------

def ayarlar_blogu() -> str:
    k = ayar()
    u, e, g, m = k["uzunluk"], k["etiketler"], k["gorsel"], k["montaj"]
    sen = e["senaryo"]
    sinir = ", ".join(f"[{t}] en fazla {n}" for t, n in e.get("ses_sinir", {}).items()) or "yok"
    maskot = (f"{len(m['maskot']['sira'])} sahnede sırasıyla {', '.join(m['maskot']['sira'])} "
              f"(dosyalar: {', '.join(m['maskot']['dosyalar'])})") if m["maskot"]["sira"] else "maskot yok (bütün satırlar '-')"
    satirlar = [
        "# KANAL AYARLARI (uygulamadan; becerideki sayılarla çelişirse bunlar geçerlidir)",
        f"- Kanal: {k['ad']} · video kodu {k['kod_oneki']}-0X",
        f"- Diller: çalışma metinleri Türkçe; video dili {dil_adi()} ({k['dil']['hedef']})"
        + ("" if ceviri_var() else " — hedef dil Türkçe olduğu için 4. aşama yoktur, Türkçe senaryo finaldir"),
        f"- Hedef süre ~{u['hedef_dk']} dk · Türkçe senaryo {u['calisma_kelime'][0]}–{u['calisma_kelime'][1]} kelime · "
        f"{dil_adi()} senaryo {u['hedef_kelime'][0]}–{u['hedef_kelime'][1]} kelime (etiketler hariç)",
        f"- Konu kartı en fazla {u['kart_karakter']} karakter · hook puanı eşiği {u['hook_esigi']}/10",
        f"- Senaryo etiketleri: karakter sahnesi [{sen['karakter']}] · metafor [{sen['metafor']}] · şema [{sen['sema']}] · "
        f"ilk 30 sn [{sen['ilk30']}]",
        f"- Seslendirme tag'leri (yalnız bunlar): {' '.join('[' + t + ']' for t in e['ses'])} · sınırlar: {sinir} · "
        f"tag'li paragraf oranı en fazla %{e['tag_orani']}",
        f"- Flow karakteri: {g['karakter'] or 'yok (karakter etiketi kullanılmaz)'} · görsel oranı {g['oran']}",
        f"- Flow yasaklı kelimeler (hiçbir biçimde): {', '.join(g['yasakli']) or 'yok'}",
        f"- İzinli teknik olumsuzlamalar: {', '.join('no ' + x for x in g['izinli_olumsuz'])}",
        f"- Maskot: {maskot}",
    ]
    if g.get("kurallar"):
        satirlar.append(f"- Görsel kurallar: {g['kurallar']}")
    return "\n".join(satirlar)
