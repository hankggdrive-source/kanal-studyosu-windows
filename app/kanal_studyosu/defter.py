"""Kanal Defteri (02_Defter.md) yenileme.

1) Yeni defteri model (iş: "defter", Sonnet) yazar: 1. aşamanın defter değişiklikleri +
   6. aşamanın DEFTER KAYDI + açılış–kapanış defteri çıktısı + süre/sahne.
2) Kod yapıyı denetler: A tablosunda her video kodu tek satır, sıralı, eksik yok; bölümler duruyor.
   Sorun varsa en fazla 2 düzeltme turu.
3) Eski defter Arsiv/<KOD>/'a, yenisinin tarihli kopyası Defter_arsivi/'ne yazılır.
4) 02_Defter.md yenisiyle değiştirilir. Hiçbir şey silinmez.
"""
from __future__ import annotations

import re
from datetime import datetime

from . import ayarlar as A
from . import cikti
from . import kanal
from . import kayit
from .kontroller import Sonuc

DEFTER = kanal.DEFTER

GOREV = """# GÖREV: KANAL DEFTERİNİ YENİLE (Kanal Stüdyosu)
Bu konuşma Kanal Stüdyosu uygulamasında, API üzerinden yürüyor. Sana mevcut 02_Defter.md ve bu videonun kayıtları <belge> olarak veriliyor. 00_Yonetici.md'deki düzenle defterin YENİ TAM HÂLİNİ yaz:
- 1. aşamanın defter değişikliklerini uygula.
- 6. aşamanın DEFTER KAYDI bloğunu ilgili bölümlere işle (A satırı, D, E, F, mekanik etiketler).
- F bölümündeki açılış–kapanış tablosunu ve kalıp sayılarını verilen Açılış–Kapanış Defteri çıktısıyla güncelle.
- Videonun süre/sahne bilgisini A tablosuna yaz.
- Başka satırlara dokunma; hiçbir videoyu silme. A tablosunda her video kodu tek satırdır ve kodlar sıralıdır.
- Başlıktaki sürüm satırını bugünün tarihiyle güncelle.
Çıktı biçimi: <dosya ad="02_Defter.md">yeni defterin tamamı</dosya> ve <ozet>en fazla 5 satır: neler değişti</ozet>."""


def _bolumler(metin: str) -> list[str]:
    return re.findall(r"^## ([A-Z])\.", metin, re.M)


def yapi_kontrol(eski: str, yeni: str, kod: str) -> Sonuc:
    s = Sonuc()
    eski_kodlar = [r["Kod"] for r in kanal.defter_tablosu(eski)]
    yeni_kodlar = [r["Kod"] for r in kanal.defter_tablosu(yeni)]
    beklenen = sorted(set(eski_kodlar) | {kod}, key=lambda k: int(k.rsplit("-", 1)[1]))
    s.bilgiler.append(f"A tablosu: {len(yeni_kodlar)} video")
    ciftler = sorted({k for k in yeni_kodlar if yeni_kodlar.count(k) > 1})
    if ciftler:
        s.hatalar.append(f"A tablosunda birden fazla satırı olan kod: {', '.join(ciftler)}")
    eksik = [k for k in beklenen if k not in yeni_kodlar]
    if eksik:
        s.hatalar.append(f"A tablosunda eksik kod: {', '.join(eksik)}")
    fazla = [k for k in yeni_kodlar if k not in beklenen]
    if fazla:
        s.hatalar.append(f"A tablosunda beklenmeyen kod: {', '.join(fazla)}")
    if not ciftler and yeni_kodlar != sorted(yeni_kodlar, key=lambda k: int(k.rsplit("-", 1)[1])):
        s.hatalar.append("A tablosunda kodlar sıralı değil.")
    kayip = [b for b in _bolumler(eski) if b not in _bolumler(yeni)]
    if kayip:
        s.hatalar.append(f"Bölüm(ler) kaybolmuş: {', '.join(kayip)}")
    if len(yeni) < 0.8 * len(eski):
        s.hatalar.append(f"Yeni defter eskisinden çok kısa ({len(yeni)} / {len(eski)} karakter); içerik silinmiş olabilir.")
    return s


def defter_kaydi(paket_md: str) -> str:
    """6. aşama paketinden DEFTER KAYDI bloğu (bulunamazsa paketin tamamı)."""
    satirlar = paket_md.splitlines()
    bas = next((i for i, l in enumerate(satirlar) if "DEFTER KAYDI ·" in l), None)
    if bas is None:
        return paket_md
    son = next((j for j in range(bas + 1, len(satirlar))
                if satirlar[j].startswith("```") or satirlar[j].startswith("## ")), len(satirlar))
    return "\n".join(satirlar[bas:son]).strip()


def yenile(llm, kod: str, sure_sahne: str, acilis_kapanis: str, ilerleme=None, butce_onayli=False) -> dict:
    from .asamalar import belge
    arsiv = kanal.arsiv_klasoru(kod)
    eski = kanal.rit(DEFTER)
    degisiklik = (arsiv / f"{kod}_1_defter_degisiklikleri.md").read_text(encoding="utf-8")
    paket = (arsiv / f"{kod}_6_paket.md").read_text(encoding="utf-8")
    sistem = ["\n\n".join(f"# PROJE DOSYASI: {ad}\n\n{kanal.rit(ad)}" for ad in kanal.PROJE_DOSYALARI[:2]), GOREV]
    mesajlar = [{"role": "user", "content": "\n\n".join([
        f"{kod} üretimi bitti. Kanal Defteri'ni yenile. Bugün: {datetime.now().strftime('%d.%m.%Y')}. "
        f"{kod} süre / sahne: {sure_sahne}.",
        belge(DEFTER, eski), belge(f"{kod}_1_defter_degisiklikleri.md", degisiklik),
        belge(f"{kod} DEFTER KAYDI", defter_kaydi(paket)),
        belge("Acilis_Kapanis_Defteri.md", acilis_kapanis)])}]
    sinir = int(A.ayarlar()["duzeltme_tur_siniri"])
    for tur in range(sinir + 1):
        cevap = llm.istek("defter", kod, sistem, mesajlar, ilerleme=ilerleme, butce_onayli=butce_onayli and tur == 0,
                          tur=f"oto_duzeltme_{tur}" if tur else "ilk")
        mesajlar += cevap.ek_mesajlar + [{"role": "assistant", "content": cevap.icerik}]
        a = cikti.ayristir(cevap.metin, [DEFTER])
        yeni = a.dosyalar.get(DEFTER, "")
        sonuc = yapi_kontrol(eski, yeni, kod) if yeni else Sonuc(hatalar=["Yeni defter dosyası verilmedi."])
        if sonuc.temiz:
            break
        if tur < sinir:
            kayit.yaz(f"Defter: yapı kontrolü {len(sonuc.hatalar)} sorun buldu, düzeltme {tur + 1}/{sinir}")
            mesajlar.append({"role": "user", "content": "Düzeltme (uygulamanın yapı kontrolü):\n" +
                             "\n".join(f"- {h}" for h in sonuc.hatalar) +
                             "\nDefterin tamamını <dosya> ile yeniden ver."})
    A.json_yaz(kanal.uygulama_klasoru(kod) / "konusma_defter.json", {"sistem": sistem, "mesajlar": mesajlar})
    if not sonuc.temiz:
        # Defter değiştirilmez; aday arşive yazılır, kullanıcıya gösterilir.
        if yeni:
            A.atomik_yaz(arsiv / "02_Defter_yeni_aday_KONTROLDEN_GECMEDI.md", yeni)
        return {"tamam": False, "kontrol": sonuc.sozluk(), "ozet": a.ozet}
    damga = datetime.now()
    A.atomik_yaz(arsiv / f"02_Defter_oncesi_{damga.strftime('%Y%m%d_%H%M%S')}.md", eski)
    tarihli = kanal.kok() / "Defter_arsivi" / f"{damga.strftime('%Y-%m-%d')}_02_Defter.md"
    if tarihli.exists():
        tarihli = tarihli.with_name(f"{damga.strftime('%Y-%m-%d_%H%M%S')}_02_Defter.md")
    A.atomik_yaz(tarihli, yeni)
    A.atomik_yaz(kanal.proje_klasoru() / DEFTER, yeni)
    kayit.yaz(f"{kod}: Kanal Defteri yenilendi (tarihli kopya: {tarihli.name})")
    return {"tamam": True, "kontrol": sonuc.sozluk(), "ozet": a.ozet, "tarihli": str(tarihli)}
