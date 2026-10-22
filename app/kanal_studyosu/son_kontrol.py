"""Son kontrol (uygulama içinde): kod kontrolleri + yapay zekâ kontrolleri → RAPOR.md ve 01_OKU_BENI.md.

- Sahne–görsel uyumu ve görselde yazı: görsel model (iş 'uyum'), 12'lik kontak sayfaları; kanalın görsel kuralları soruda.
- Rapor özeti ve kullanıcı mesajı: Haiku (iş 'rapor').
- Sayım, senkron, hassas kelime, dosya düzeni: kod.
"""
from __future__ import annotations

import base64
import json
import re
from datetime import datetime

from . import ayarlar as A
from . import dosya_duzeni
from . import kanal
from . import maliyet
from . import metin as M

UYUM_SORUSU = """Ekteki kontak sayfalarında her küçük resim bir sahne; altında sarı sahne numarası var.
Aşağıda her sahnenin seslendirme cümlesi var.

Kanalın görsel kuralları (kanal ayarından); bunlara uyan görseller SORUN DEĞİLDİR:
{kurallar}

Her sahne için kontrol et:
1) Görsel cümleyle uyuşuyor mu? Yalnızca gerçek uyumsuzlukları "zayif" say: yanlış mekân/nesne, metnin
   anlattığına ters duygu (ör. ağır bir anda belirgin gülümseme), konuyla ilgisiz görsel.
2) Görselde okunabilir yazı, harf ya da kelime var mı?
Yalnızca SORUNLU sahneleri JSON olarak ver, başka bir şey yazma:
{{"0012": {{"uyum": "zayif", "yazi": false, "not": "kısa Türkçe açıklama"}}, ...}}
Sorun yoksa {{}} yaz.

{liste}"""


def gorsel_uyum(kod: str, llm) -> dict:
    sayfalar = sorted((kanal.arsiv_klasoru(kod) / "odak").glob("sayfa*.jpg"),
                      key=lambda p: int(re.search(r"\d+", p.stem).group(0)))
    paragraflar = [M.govde(p) for p in (kanal.video_klasoru(kod) / "02_ElevenLabs_seslendirme_metni.txt")
                   .read_text(encoding="utf-8").strip().split("\n\n") if p.strip()]
    liste = "\n".join(f"{i:04d}: {p[:170]}" for i, p in enumerate(paragraflar, 1))
    icerik = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                           "data": base64.standard_b64encode(s.read_bytes()).decode()}}
              for s in sayfalar]
    kurallar = kanal.ayar()["gorsel"].get("kurallar") or "- Görselde yazı ve logo olmaz."
    kurallar = "\n".join(l if l.lstrip().startswith("-") else f"- {l}" for l in kurallar.splitlines() if l.strip())
    icerik.append({"type": "text", "text": UYUM_SORUSU.format(liste=liste, kurallar=kurallar)})
    cevap = llm.istek("uyum", kod, [], [{"role": "user", "content": icerik}])
    m = re.search(r"\{.*\}", cevap.metin, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except ValueError:
        return {"?": {"uyum": "?", "yazi": False, "not": "Model cevabı okunamadı; kontak sayfalarına elle bak."}}


def rapor_yaz(kod: str, veri: dict, uyum: dict, llm) -> str:
    """RAPOR.md (Arsiv) ve 01_OKU_BENI.md (Videolar). Döner: kullanıcıya kısa özet."""
    m = maliyet.ozet(kod)
    sorunlu = [f"- Sahne {n}: {v.get('not', '')}" + (" · görselde yazı var" if v.get("yazi") else "")
               for n, v in sorted(uyum.items())]
    fazla = [p.name for p in dosya_duzeni.fazlalar(kod)]
    satirlar = [
        f"# {kod} · Üretim raporu", f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}", "",
        "## Özet bilgiler",
        f"- Konu / başlık: {veri.get('baslik', '')}",
        *([f"- Başlangıç: {veri['baslangic']}"] if veri.get("baslangic") else []),
        *([f"- Bu üretimde kapalı onaylar: {veri['onaysiz']} (kontroller temizse beklemeden geçti)"]
          if veri.get("onaysiz") else []),
        f"- Süre / sahne: {veri.get('sure', '')} / {veri.get('sahne', '')}",
        *([f"- Ses kenarı: {veri['ses_kenar']}"] if veri.get("ses_kenar") else []),
        f"- CapCut taslağı: **{kod}** (CapCut'ı açınca listede; görünmezse kapatıp aç)",
        f"- Müzik: {veri.get('muzik', '') or 'bilgi yok'}",
        f"- Maskot sahneleri: {veri.get('maskot', '') or '-'}",
        f"- Altyazı satırı: {veri.get('srt_satir', '')}",
        (f"- Yazım: Claude Code aboneliği (API'yle olsaydı ~{m['abonelik_tahmini_usd']:.2f} $; abonelikten ücret düşmez)"
         + (f" · OpenRouter: {m['video_usd']:.2f} $" if m["video_usd"] else "") if m.get("abonelik") else
         f"- Maliyet (API): {m['video_usd']:.2f} $ · aşamalar: " +
         ", ".join(f"{k} {v:.2f} $" for k, v in m["asamalar"].items())),
        "  (ayrıntılı döküm, Kanal Defteri dahil: Kapanış'tan sonra `MALIYET.md`)",
        "", "## Kod kontrolleri",
        f"- Senkron (senk_kontrol): {veri.get('senk', '')}",
        f"- Hassas kelime: {veri.get('hassas', '')}",
        f"- Odak: {veri.get('odak', '')}",
        f"- Dosya düzeni: " + ("temiz" if not fazla else "fazla dosya: " + ", ".join(fazla)),
        "", "## Sahne–görsel uyumu (yapay zekâ)",
        *(sorunlu or ["- Sorunlu sahne bulunmadı."]),
        "", "## Senin işin", "- CapCut'ta taslağı aç, rötuş yap, dışa aktar.",
        "- Kapak görsellerini Flow'da üret (04 dosyasındaki kapak promptları); iki kapağı Test & compare ile yarıştır.",
    ]
    if veri.get("uyarilar"):
        satirlar += ["", "## Uyarılar", *[f"- {u}" for u in veri["uyarilar"]]]
    rapor = "\n".join(satirlar) + "\n"
    ozet = ""
    try:
        cevap = llm.istek("rapor", kod, [], [{"role": "user", "content":
                          "Aşağıdaki üretim raporunu kullanıcı için en fazla 6 satırlık, sade Türkçe bir özete çevir. "
                          "Teknik terim (token, port, JSON) kullanma. Önce sonuç, sonra yapılması gerekenler.\n\n" + rapor}])
        ozet = cevap.metin.strip()
    except Exception as e:  # özet olmasa da rapor yazılır
        ozet = f"(Özet yazılamadı: {e})"
    rapor = rapor.replace("## Özet bilgiler", f"## Kısa özet\n{ozet}\n\n## Özet bilgiler", 1)
    A.atomik_yaz(kanal.arsiv_klasoru(kod) / "RAPOR.md", rapor)
    oku_beni = "\n".join([
        f"# {kod} — Üretim klasörü", "",
        f"**Başlık:** {veri.get('baslik', '')}",
        f"**Süre / sahne:** {veri.get('sure', '')} / {veri.get('sahne', '')}",
        f"**CapCut taslağı:** {kod}",
        f"**Müzik:** {veri.get('muzik', '') or '-'} · **Maskot:** {veri.get('maskot', '') or '-'}",
        f"**Sahne videoları:** {veri.get('video_klasoru', '')}",
        "", "## Kısa özet", ozet, "",
        f"Ayrıntılı rapor: `Arsiv/{kod}/RAPOR.md` · Üreten: Kanal Stüdyosu {A.SURUM}", ""])
    A.atomik_yaz(kanal.video_klasoru(kod) / "01_OKU_BENI.md", oku_beni)
    return ozet
