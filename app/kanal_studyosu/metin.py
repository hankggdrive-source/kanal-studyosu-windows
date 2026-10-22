"""Senaryo metinleri: paragraf ayrıştırma, kelime sayımı, mekanik yama.

Paragraf = boş satırla ayrılan blok. Etiket satırı ([MIRA] [★30sn]) paragrafın
parçasıdır. Dosya sonundaki teslim satırları ("Parole: …", "Kelime: …" ile
başlayan kuyruk) paragraf sayılmaz.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

ETIKET = re.compile(r"\[[^\]\n]{1,40}\]")
# "Açık noktalar" satırı dosyaya düşerse de konuşma metni sayılmaz (seslendirmeye/sahnelere gitmez).
KUYRUK_BASI = re.compile(r"^\s*\**\s*(Parole|Kelime|Paragrafi|Paragraf|Words|Açık noktalar)\s*\**\s*:"
                         r"|^\s*\**\s*[\wÀ-ÿ]+\s*\**\s*:\s*\**\s*\d{3,5}\b", re.IGNORECASE)
# Teslim satırındaki kelime sayısı (dil fark etmez): "Parole: 2003 · Paragrafi: 71", "Words: 1980", "Kelime: 1720"
KELIME_SATIRI = re.compile(r"(?m)^\s*\**\s*[\wÀ-ÿ]+\s*\**\s*:\s*\**\s*\d{3,5}\b")


@dataclass
class Senaryo:
    paragraflar: list[str]
    kuyruk: str  # teslim satırları (boş olabilir)

    def metin(self) -> str:
        govde = "\n\n".join(self.paragraflar)
        return govde + ("\n\n" + self.kuyruk if self.kuyruk else "") + "\n"


def ayir(metin: str) -> Senaryo:
    satirlar = metin.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    kuyruk = ""
    for i, s in enumerate(satirlar):
        if KUYRUK_BASI.match(s):
            kuyruk = "\n".join(satirlar[i:]).strip()
            satirlar = satirlar[:i]
            break
    bloklar = [b.strip() for b in re.split(r"\n\s*\n", "\n".join(satirlar)) if b.strip()]
    return Senaryo(bloklar, kuyruk)


def govde(paragraf: str) -> str:
    """Etiketsiz, tek boşluklu konuşma metni."""
    return " ".join(ETIKET.sub(" ", paragraf).split())


def kelime_sayisi(metin_ya_da_paragraflar) -> int:
    if isinstance(metin_ya_da_paragraflar, str):
        paragraflar = ayir(metin_ya_da_paragraflar).paragraflar
    else:
        paragraflar = metin_ya_da_paragraflar
    return sum(len([w for w in govde(p).split() if re.search(r"\w", w)]) for p in paragraflar)


# --- Mekanik yama -----------------------------------------------------------
# Model düzeltme turunda yalnızca değişen kısımları verir. Kod bunları
# numarasıyla/anahtarıyla birebir yerine koyar; içerik üretmez.

class YamaHatasi(ValueError):
    pass


def yama_uygula(metin: str, yamalar: list[dict]) -> str:
    """yamalar: {'paragraf': N, 'islem': 'degistir'|'sil'|'sonrasina_ekle', 'icerik': …}
    ya da {'satir': 'Başlık', 'icerik': …} ya da {'bolum': '§4', 'icerik': …}
    ya da {'kuyruk': True, 'icerik': …}. Paragraf numaraları yamadan önceki dosyaya göredir."""
    paragraf_yamalari = [y for y in yamalar if "paragraf" in y]
    diger = [y for y in yamalar if "paragraf" not in y]
    for y in diger:
        if y.get("kuyruk"):
            s = ayir(metin)
            s.kuyruk = y["icerik"].strip()
            metin = s.metin()
        elif "satir" in y:
            metin = _satir_degistir(metin, y["satir"], y["icerik"])
        elif "bolum" in y:
            metin = _bolum_degistir(metin, y["bolum"], y["icerik"])
        else:
            raise YamaHatasi("Tanınmayan yama")
    if paragraf_yamalari:
        s = ayir(metin)
        n = len(s.paragraflar)
        for y in paragraf_yamalari:
            if not 1 <= int(y["paragraf"]) <= n:
                raise YamaHatasi(f"¶{y['paragraf']} yok (dosyada {n} paragraf var)")
        # Önce yerinde değişiklikler (numara kaymaz), sonra silme/ekleme sondan başa.
        for y in paragraf_yamalari:
            if y.get("islem", "degistir") == "degistir":
                s.paragraflar[int(y["paragraf"]) - 1] = y["icerik"].strip()
        for y in sorted((y for y in paragraf_yamalari if y.get("islem", "degistir") != "degistir"),
                        key=lambda y: int(y["paragraf"]), reverse=True):
            i = int(y["paragraf"]) - 1
            if y["islem"] == "sil":
                del s.paragraflar[i]
            elif y["islem"] == "sonrasina_ekle":
                yeni = [b.strip() for b in re.split(r"\n\s*\n", y["icerik"].strip()) if b.strip()]
                s.paragraflar[i + 1:i + 1] = yeni
            else:
                raise YamaHatasi(f"Bilinmeyen işlem: {y['islem']}")
        metin = s.metin()
    return metin


def _satir_degistir(metin: str, anahtar: str, yeni: str) -> str:
    satirlar = metin.split("\n")
    for i, s in enumerate(satirlar):
        if s.strip().startswith(anahtar):
            satirlar[i] = yeni.strip()
            return "\n".join(satirlar)
    raise YamaHatasi(f"'{anahtar}' ile başlayan satır bulunamadı")


def _bolum_degistir(metin: str, baslik: str, yeni: str) -> str:
    satirlar = metin.split("\n")
    temiz = [s.lstrip("# ").strip() for s in satirlar]
    bas = next((i for i, s in enumerate(temiz)
                if s.startswith(baslik) and not s[len(baslik):len(baslik) + 1].isdigit()), None)
    if bas is None:
        raise YamaHatasi(f"'{baslik}' bölümü bulunamadı")
    bit = len(satirlar)
    for j in range(bas + 1, len(satirlar)):
        if temiz[j].startswith("§") or satirlar[j].startswith("#"):
            bit = j
            break
    return "\n".join(satirlar[:bas] + [yeni.strip()] + satirlar[bit:])
