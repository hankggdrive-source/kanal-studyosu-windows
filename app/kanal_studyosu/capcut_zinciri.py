"""CapCut zinciri: uygulamanın araçlar/ betiklerini sırayla çağırır (CapCut KAPALIYKEN).

srt_uret → odak (odak_izgara.py + görsel model) → capcut_taslak → senk_kontrol --metin
→ yayin_hazirla (müzik, 4 maskot, 8 sn son ekran) → senk_kontrol.
CapCut'ı açıp kontrol etmek ve dışa aktarmak kullanıcının işidir.
"""
from __future__ import annotations

import base64
import csv
import io
import json
import re
from pathlib import Path

from . import araclar
from . import ayarlar as A
from . import kanal
from . import kanallar
from . import kayit
from . import metin as M

ODAK_SORUSU = """Bu görsel bir kontak sayfası: her küçük resim bir video sahnesi, altında sarı sahne numarası var ve 3x3 ızgarayla bölünmüş.
Her sahne için yakınlaşmanın gideceği ODAK öğesinin, o sahnenin KENDİ küçük resmi içindeki merkezini ver.
Koordinatlar küçük resme göre 0–1 arasında: sol üst (0,0), sağ alt (1,1). Değerler 0,1–0,9 aralığında olsun.
Sahneler ve odak öğeleri:
{liste}
Yalnızca JSON ver, başka hiçbir şey yazma: {{"0001": [x, y], "0002": [x, y], ...}}"""


def taslak_klasoru(kod: str) -> Path:
    return A.yol("capcut_taslak") / kod


def srt(kod: str, video: Path) -> dict:
    d = kanal.video_klasoru(kod)
    c = araclar.calistir("srt_uret.py", str(video), str(d / "02_ElevenLabs_seslendirme_metni.txt"),
                         str(d / kanal.altyazi_adi(kod))).cikti
    m = re.search(r"cues (\d+) toplam ([\d:,]+)", c)
    return {"satir": int(m.group(1)) if m else None, "toplam": m.group(2) if m else ""}


def plan_satirlari(kod: str) -> list[dict]:
    yol = kanal.video_klasoru(kod) / "05_Montaj_plani.tsv"
    return [r for r in csv.DictReader(io.StringIO(yol.read_text(encoding="utf-8")), delimiter="\t") if r.get("sahne")]


def _json_al(metin: str) -> dict:
    m = re.search(r"\{.*\}", metin, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except ValueError:
        return {}


def _gecerli(n: str, deger) -> bool:
    return (isinstance(deger, list) and len(deger) == 2 and all(isinstance(v, (int, float)) for v in deger)
            and all(0.1 <= float(v) <= 0.9 for v in deger))


def odak(kod: str, video: Path, llm, ilerleme=lambda m: None) -> dict:
    """Kontak sayfalarına bakan görsel model (iş 'odak': Haiku; tutmazsa 'odak_yedek': Sonnet).
    Kod 0,1–0,9 aralığını ve eksik sahneyi denetler. → 06_Odak_noktalari.json"""
    hedef = kanal.arsiv_klasoru(kod) / "odak"
    araclar.calistir("odak_izgara.py", str(video), str(hedef))
    sayfalar = sorted(hedef.glob("sayfa*.jpg"), key=lambda p: int(re.search(r"\d+", p.stem).group(0)))
    plan = plan_satirlari(kod)
    sonuc: dict[str, list] = {}
    for i, sayfa in enumerate(sayfalar):
        sahneler = plan[i * 12:(i + 1) * 12]
        liste = "\n".join(f"{r['sahne']}: {r.get('odak') or 'ana öğe'}" for r in sahneler)
        resim = base64.standard_b64encode(sayfa.read_bytes()).decode()
        mesaj = [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": resim}},
            {"type": "text", "text": ODAK_SORUSU.format(liste=liste)}]}]
        for is_adi in ("odak", "odak_yedek"):
            ilerleme(f"Odak noktaları: sayfa {i + 1}/{len(sayfalar)}" + (" (yedek model)" if is_adi != "odak" else ""))
            j = _json_al(llm.istek(is_adi, kod, [], mesaj).metin)
            eksik = [r["sahne"] for r in sahneler if not _gecerli(r["sahne"], j.get(r["sahne"]))]
            if not eksik:
                break
            kayit.yaz(f"Odak sayfa {i + 1}: {len(eksik)} sahne geçersiz/eksik ({is_adi})", "uyari")
        for r in sahneler:
            sonuc[r["sahne"]] = [round(float(v), 3) for v in j[r["sahne"]]] if _gecerli(r["sahne"], j.get(r["sahne"])) \
                else [0.5, 0.45]  # iki model de veremezse güvenli varsayılan; raporda belirtilir
    varsayilan = [n for n, v in sonuc.items() if v == [0.5, 0.45]]
    A.json_yaz(kanal.video_klasoru(kod) / "06_Odak_noktalari.json", sonuc)
    return {"sahne": len(sonuc), "varsayilan": varsayilan}


def taslak(kod: str, video: Path) -> dict:
    if taslak_klasoru(kod).exists():
        raise araclar.AracHatasi(f"CapCut'ta '{kod}' adlı taslak zaten var. Uygulama mevcut taslağa dokunmaz; "
                                 "CapCut'ta adını değiştirip Tekrar dene.")
    d = kanal.video_klasoru(kod)
    c = araclar.calistir("capcut_taslak.py", "--video", str(video), "--plan", str(d / "05_Montaj_plani.tsv"),
                         "--odak", str(d / "06_Odak_noktalari.json"), "--srt", str(d / kanal.altyazi_adi(kod)),
                         "--ad", kod).cikti
    if taslak_klasoru(kod).is_dir():  # iki iz: kanal silinirken yalnız Kanal Stüdyosu'nun taslakları Çöp'e gider
        kanallar.taslak_kaydet(kanal.secili(), taslak_klasoru(kod))
    m = re.search(r"^ok .*?([\d.]+) sn sahne (\d+) altyazi (\d+)\s*\n(.*)", c, re.M)
    istatistik = _json_al(m.group(4)) if m else {}
    return {"sure": m.group(1) if m else "", "sahne": int(m.group(2)) if m else None,
            "altyazi": int(m.group(3)) if m else None, "istatistik": istatistik}


NORMAL_NOTLAR = ("konusma hizi farkli", "sessizlik")  # SKILL 10b-4: bunlar beklenen durumlar


def senk(kod: str, metin: bool = False) -> dict:
    c = araclar.calistir("senk_kontrol.py", kod, *(["--metin"] if metin else [])).cikti
    satirlar = c.splitlines()
    i = next((k for k, s in enumerate(satirlar) if s.startswith("SONUC:")), len(satirlar))
    notlar = [s for s in satirlar[i + 1:] if s.strip() and not re.match(r"^\d{4} ", s)] if i < len(satirlar) else []
    return {"temiz": i < len(satirlar) and "TEMIZ" in satirlar[i],
            "sorunlar": [s for s in notlar if not any(k in s for k in NORMAL_NOTLAR)],
            "normal": [s for s in notlar if any(k in s for k in NORMAL_NOTLAR)],
            "son_ekran": next((s for s in satirlar if s.startswith("son ekran var")), ""),
            "ozet": "\n".join(satirlar[:i + 1])[-1500:]}


def maskot_argumanlari(maskot: str) -> list[str]:
    """Yalnız '--maskot SAHNE:M:SÜRE' çiftleri (eski sürümün kaydına karışmış başka sözcükler atılır)."""
    p = (maskot or "").split()
    return [x for i in range(len(p) - 1) if p[i] == "--maskot" and re.fullmatch(r"\d+:\d+:\d+(?:\.\d+)?", p[i + 1])
            for x in (p[i], p[i + 1])]


MUZIK_UZANTI = (".mp3", ".m4a", ".wav", ".aac", ".flac")


def muzik_dosyalari() -> list[Path]:
    k = kanal.kok() / "Varliklar" / "Muzik"
    return sorted(f for f in k.glob("*") if f.suffix.lower() in MUZIK_UZANTI and not f.name.startswith(".")) \
        if k.is_dir() else []


def yayin_hazirla(kod: str, maskot: str) -> dict:
    arg = maskot_argumanlari(maskot)
    k = kanal.ayar()["montaj"]
    bos = k["muzik"] and not muzik_dosyalari()
    if bos:  # kanal kartındaki uyarının söylediği gibi: müziksiz devam
        kayit.yaz(f"{kod}: müzik açık ama Varliklar/Muzik klasörü boş; montaj müziksiz yapılıyor", "uyari")
    arg += ["--son-sn", str(k["son_ekran_sn"])] + ([] if k["muzik"] and not bos else ["--muziksiz"])
    try:
        c = araclar.calistir("yayin_hazirla.py", kod, *arg, zaman_asimi=3600).cikti
    except araclar.AracHatasi:
        # Uzun maskot üretiminde yarıda kalabilir; tekrar çalıştırılınca bitmiş maskotları atlar (BENI_OKU).
        kayit.yaz("yayin_hazirla bir kez daha deneniyor", "uyari")
        c = araclar.calistir("yayin_hazirla.py", kod, *arg, zaman_asimi=3600).cikti
    # muzik_otomatik.py de "tamam …" yazar; yayin_hazirla'nın satırı "| muzik:" içeren sonuncusudur.
    tamam = [s for s in re.findall(r"^tamam .*", c, re.M) if "| muzik:" in s]
    if not tamam:
        raise araclar.AracHatasi("yayin_hazirla.py beklenen 'tamam' satırını vermedi.", c[-4000:])
    secilen = re.search(r"secilen:.*", c)
    return {"satir": tamam[-1], "muzik": "muzik: var" in tamam[-1],
            "secilen": secilen.group(0) if secilen else
            ("yok: Varliklar/Muzik klasörü boş olduğu için müziksiz üretildi" if bos else "")}


def muzik_yenile(kod: str) -> str:
    """Bitmiş taslağın müziğini yeniden yapar (muzik_otomatik.py --ekle): yeni rastgele parçalar, eski müzik dosyası ve
    taslak arşive kopyalanır. CapCut kapalı olmalı. Döner: seçilen parçalar satırı."""
    if capcut_acik():
        raise araclar.AracHatasi("CapCut açık. Önce CapCut'ı kapat, sonra yeniden dene.")
    if not muzik_dosyalari():
        raise araclar.AracHatasi("Varliklar/Muzik klasöründe parça yok. Kanal kartında Klasörü aç ile müzik ekle.")
    son = str(kanal.ayar()["montaj"]["son_ekran_sn"])
    c = araclar.calistir("muzik_otomatik.py", kod, "--ekle", "--son-sn", son, zaman_asimi=1800).cikti
    secilen = re.search(r"secilen:.*", c)
    return secilen.group(0) if secilen else "yenilendi"


def capcut_acik() -> bool:
    from .onkontrol import capcut_acik as acik
    return acik()


def bolum_zamanlari(kod: str) -> list[dict]:
    """Taslaktaki her 'bolum' değişiminin başlangıcı (m:ss) ve o sahnenin ilk cümlesi (SKILL 10c)."""
    dr = json.loads((taslak_klasoru(kod) / "draft_info.json").read_text(encoding="utf-8"))
    segler = [t for t in dr["tracks"] if t["type"] == "video"][0]["segments"]
    plan = plan_satirlari(kod)
    paragraflar = [M.govde(p) for p in
                   (kanal.video_klasoru(kod) / "02_ElevenLabs_seslendirme_metni.txt").read_text(encoding="utf-8")
                   .strip().split("\n\n") if p.strip()]
    sonuc, onceki = [], None
    for i, r in enumerate(plan):
        if r["bolum"] != onceki and i < len(segler):
            bas = segler[i]["target_timerange"]["start"] / 1e6
            m, s = divmod(int(bas), 60)
            ilk = re.split(r"(?<=[.!?…»])\s+", paragraflar[i])[0] if i < len(paragraflar) else ""
            sonuc.append({"zaman": f"{m}:{s:02d}", "bolum": r["bolum"], "sahne": r["sahne"], "ilk_cumle": ilk})
        onceki = r["bolum"]
    return sonuc
