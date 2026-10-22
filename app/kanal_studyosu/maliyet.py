"""Token ve tahmini $ sayacı, bütçe sınırı.

Her API çağrısı Sistem/maliyet.jsonl'ye (kanal alanıyla; aylık bütçe bütün kanallar için ortak) bir satır olarak eklenir (video ve iş bazında).
Fiyatlar ayar dosyasındadır ($ / 1M token). Önbelleğe yazma: 5 dk için girişin
1,25 katı, 1 saat için 2 katı.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import ayarlar as A
from . import yollar


def _fiyat(model: str, ayar: dict) -> dict:
    return ayar["modeller"].get(model) or ayar["modeller"][max(
        ayar["modeller"], key=lambda m: ayar["modeller"][m]["cikis"])]  # bilinmeyen model: en pahalı varsayılır


def hesapla(kullanim: dict, model: str, ayar: dict, onbellek_suresi: str = "5m") -> float:
    """kullanim: input_tokens, output_tokens, cache_creation_input_tokens,
    cache_read_input_tokens, web_search_requests, iterations (yedek model devreye girdiyse)."""
    yazma_katsayi = 2.0 if onbellek_suresi == "1h" else 1.25
    parcalar = kullanim.get("iterations") or [dict(kullanim, model=model)]
    toplam = 0.0
    for p in parcalar:
        f = _fiyat(p.get("model") or model, ayar)
        toplam += (p.get("input_tokens", 0) * f["giris"]
                   + p.get("cache_creation_input_tokens", 0) * f["giris"] * yazma_katsayi
                   + p.get("cache_read_input_tokens", 0) * f["onbellek_okuma"]
                   + p.get("output_tokens", 0) * f["cikis"]) / 1_000_000
    toplam += kullanim.get("web_search_requests", 0) * ayar["web_arama_1000_usd"] / 1000
    return round(toplam, 6)


TUR_ADI = {"ilk": "İlk yazım", "oto": "Otomatik düzeltme", "kullanici": "Senin düzeltmen", "tekrar": "Tekrar dene",
           "kesildi": "Kesilen / reddedilen", "": "Ayrılmamış (eski kayıt)"}


def kaydet(video: str, is_adi: str, model: str, kullanim: dict, usd: float, tur: str = "ilk",
           sonuc: str = "", abonelik: bool = False, tahmini_usd: float = 0.0) -> dict:
    """tur: ilk | oto_duzeltme_N | kullanici_duzeltme | tekrar. sonuc: '' ya da max_tokens/refusal (ücret ödendi,
    cevap kullanılamadı). abonelik: Claude Code (usd 0, bütçeye sayılmaz; tahmini_usd yalnız bilgi)."""
    from . import kanallar
    satir = {"zaman": datetime.now(timezone.utc).isoformat(), "kanal": kanallar.aktif() or "", "video": video,
             "is": is_adi, "model": model,
             "usd": usd, "tur": tur, **({"sonuc": sonuc} if sonuc else {}),
             **({"abonelik": True, "tahmini_usd": round(tahmini_usd, 4)} if abonelik else {}),
             **{k: v for k, v in kullanim.items() if k != "iterations"}}
    yollar.maliyet_dosyasi().parent.mkdir(parents=True, exist_ok=True)
    with open(yollar.maliyet_dosyasi(), "a", encoding="utf-8") as f:
        f.write(json.dumps(satir, ensure_ascii=False) + "\n")
    return satir


def satirlar() -> list[dict]:
    try:
        with open(yollar.maliyet_dosyasi(), encoding="utf-8") as f:
            return [json.loads(s) for s in f if s.strip()]
    except FileNotFoundError:
        return []


def ozet(video: str | None = None) -> dict:
    ay = datetime.now(timezone.utc).strftime("%Y-%m")
    tum = satirlar()
    ay_top = sum(s["usd"] for s in tum if s["zaman"].startswith(ay))
    vid = [s for s in tum if video and s["video"] == video]
    asama: dict[str, float] = {}
    for s in vid:
        asama[s["is"]] = asama.get(s["is"], 0) + s["usd"]
    ayar = A.ayarlar()
    return {"abonelik_tahmini_usd": round(sum(s.get("tahmini_usd", 0) for s in vid), 2),
            "abonelik": any(s.get("abonelik") for s in vid),
            "ay_usd": round(ay_top, 4), "ay_sinir": ayar["butce"]["aylik_usd"],
            "video_usd": round(sum(s["usd"] for s in vid), 4), "video_sinir": ayar["butce"]["video_usd"],
            "asamalar": {k: round(v, 4) for k, v in asama.items()}}


class ButceAsimi(Exception):
    pass


def butce_kontrol(video: str, tahmini_usd: float) -> None:
    """Çağrı yapılmadan önce: sınır aşılacaksa ButceAsimi (kullanıcıya sorulur)."""
    o = ozet(video)
    if o["video_usd"] + tahmini_usd > o["video_sinir"]:
        raise ButceAsimi(f"Bu video için bütçe sınırına geldik: harcanan {o['video_usd']:.2f} $, "
                         f"bu adım tahminen {tahmini_usd:.2f} $, sınır {o['video_sinir']:.0f} $.")
    if o["ay_usd"] + tahmini_usd > o["ay_sinir"]:
        raise ButceAsimi(f"Bu ayın bütçe sınırına geldik: harcanan {o['ay_usd']:.2f} $, "
                         f"bu adım tahminen {tahmini_usd:.2f} $, sınır {o['ay_sinir']:.0f} $.")


def _sutun(s: dict) -> str:
    if s.get("sonuc"):
        return "kesildi"
    t = s.get("tur", "")
    return "oto" if t.startswith("oto") else "kullanici" if t.startswith("kullanici") else t


def dokum(video: str) -> str:
    """Video için ayrıntılı maliyet dökümü (Markdown): aşama × tür tablosu ve istek istek liste."""
    vid = [s for s in satirlar() if s.get("video") == video]
    sutunlar = ["ilk", "oto", "kullanici", "tekrar", "kesildi"] + (["" ] if any("tur" not in s for s in vid) else [])
    tablo: dict[str, dict[str, list]] = {}
    for s in vid:
        is_ = s["is"].replace("_yedek", "")
        tablo.setdefault(is_, {}).setdefault(_sutun(s), []).append(s["usd"])
    hucre = lambda l: f"{sum(l):.2f} $ ({len(l)})" if l else "—"
    st = [f"# {video} · Maliyet dökümü (tahmini, API)", "",
          "| İş | " + " | ".join(TUR_ADI[c] for c in sutunlar) + " | Toplam |",
          "|---|" + "---|" * (len(sutunlar) + 1)]
    for is_, d in tablo.items():
        st.append(f"| {is_} | " + " | ".join(hucre(d.get(c, [])) for c in sutunlar) +
                  f" | **{sum(sum(v) for v in d.values()):.2f} $** |")
    st.append("| **Toplam** | " + " | ".join(hucre([u for d in tablo.values() for u in d.get(c, [])])
                                            for c in sutunlar) + f" | **{sum(s['usd'] for s in vid):.2f} $** |")
    st += ["", "Parantez içi: istek sayısı. Kesilen / reddedilen: ücreti ödenen ama kullanılamayan cevap.",
           "Kesin tutar için sağlayıcının panelindeki kullanım geçmişine bak."]
    if any(s.get("abonelik") for s in vid):
        st += ["", f"Claude Code (abonelik) istekleri 0 $ sayılır; API'yle olsaydı tahmini karşılığı "
                   f"~{sum(s.get('tahmini_usd', 0) for s in vid):.2f} $ (yalnız bilgi)."]
    st += ["", "## İstek istek",
           "| Saat (UTC) | İş | Tür | Model | Giriş | Önbellek okuma | Çıkış | Arama | $ |", "|---|---|---|---|---|---|---|---|---|"]
    for s in vid:
        tur = (s.get("tur") or "?") + (f" · {s['sonuc']}" if s.get("sonuc") else "")
        st.append((f"| {s['zaman'][5:16].replace('T', ' ')} | {s['is']} | {tur} | {s.get('model', '')} | "
                  f"{s.get('input_tokens', 0) + s.get('cache_creation_input_tokens', 0):,} | "
                  f"{s.get('cache_read_input_tokens', 0):,} | {s.get('output_tokens', 0):,} | "
                  f"{s.get('web_search_requests', 0)} | "
                  + (f"abonelik (~{s.get('tahmini_usd', 0):.2f})" if s.get("abonelik") else f"{s['usd']:.4f}")
                  + " |").replace(",", "."))
    return "\n".join(st) + "\n"
