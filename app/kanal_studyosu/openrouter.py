"""OpenRouter üzerinden Claude (Anthropic hesabı olmadan).

OpenRouter, Anthropic Messages biçimini birebir kabul eden bir uç nokta sunar (taban: https://openrouter.ai/api,
kimlik: OpenRouter anahtarı Bearer olarak). Uygulamanın Anthropic katmanı aynen kullanılır; burada yalnızca:
- model adları eşlenir (claude-sonnet-5-5 → anthropic/claude-sonnet-5.5; ayar dosyasından, yoksa OpenRouter listesinden),
- anahtar denenir (GET /api/v1/key, ücretsiz).
İstek ayrıntıları (desteklenmeyen alanların ayıklanması) llm.py'dedir.
"""
from __future__ import annotations

import re
import threading
import urllib.error
import urllib.request

from . import ayarlar as A
from . import kayit
from .ai84 import KIMLIK, AI84, AI84Hatasi, _curl, _json

API = "https://openrouter.ai/api"
_ESLESME: dict[str, str] = {}
_KILIT = threading.Lock()


def _get(yol: str, anahtar: str = "") -> tuple[int, dict]:
    bas = {"Accept": "application/json", **({"Authorization": f"Bearer {anahtar}"} if anahtar else {})}
    if _curl():
        try:
            kod, j, _ = AI84._curl_istek("GET", API + yol, bas, None, 25)
        except AI84Hatasi as e:  # ağ hatası (metin AI84'e göre yazılmış; yalnız ayrıntı alınır)
            return 0, {"message": str(e).split("(", 1)[-1].rstrip(").")}
        return kod, j
    try:
        with urllib.request.urlopen(urllib.request.Request(API + yol, headers={**bas, "User-Agent": KIMLIK}),
                                    timeout=25) as c:
            return c.status, _json(c.read())
    except urllib.error.HTTPError as e:
        return e.code, _json(e.read())
    except (urllib.error.URLError, OSError) as e:
        return 0, {"message": str(getattr(e, "reason", e))}


def _normal(ad: str) -> str:
    """anthropic/claude-sonnet-5.5[1m] → claude-sonnet-5-5 (ekler ve ":batch" gibi varyantlar yok sayılır)."""
    return re.sub(r"\[.*?\]|:.*$", "", ad.split("/", 1)[-1]).replace(".", "-").lower()


def model_eslestir(ic_model: str) -> str:
    """Uygulamadaki model adı → OpenRouter model kimliği. Önce ayar dosyasındaki sabit eşleme (kullanılan üç model,
    2 Ekim 2026 testinde doğrulandı), yoksa OpenRouter model listesinden; listede de yoksa 'anthropic/claude-x-y.z'."""
    sabit = A.ayarlar().get("openrouter", {}).get("modeller", {}).get(ic_model)
    if sabit:
        return sabit
    with _KILIT:
        if ic_model in _ESLESME:
            return _ESLESME[ic_model]
        kod, j = _get("/v1/models")
        adaylar = [m.get("id", "") for m in (j.get("data") or []) if str(m.get("id", "")).startswith("anthropic/")]
        adaylar.sort(key=lambda a: (":" in a, "[" in a, a))  # önce eksiz ad
        bulunan = next((a for a in adaylar if _normal(a) == ic_model.lower()), "")
        if not bulunan:
            kayit.yaz(f"OpenRouter'da {ic_model} bulunamadı (liste {kod}); 'anthropic/{ic_model}' deneniyor", "uyari")
            bulunan = "anthropic/" + re.sub(r"-(\d+)-(\d+)$", r"-\1.\2", ic_model)
        _ESLESME[ic_model] = bulunan
        return bulunan


def dogrula(anahtar: str = "") -> tuple[bool, str]:
    anahtar = anahtar or A.anahtar("openrouter")
    if not anahtar:
        return False, "OpenRouter anahtarı kayıtlı değil. Ayarlar'dan ekle."
    kod, j = _get("/v1/key", anahtar)
    if kod == 200:
        d = j.get("data", j)
        kalan = d.get("limit_remaining")
        ek = f" · kalan limit {kalan:.2f} $" if isinstance(kalan, (int, float)) else ""
        ucretsiz = " · ücretsiz hesap (kredi yükle)" if d.get("is_free_tier") else ""
        return True, f"OpenRouter anahtarı geçerli{ek}{ucretsiz}."
    if kod == 401:
        return False, "OpenRouter anahtarı geçersiz (HTTP 401)."
    if kod == 0:
        return False, f"OpenRouter'a ulaşılamadı ({j.get('message', 'ağ hatası')})."
    msg = (j.get("error") or {}).get("message") if isinstance(j.get("error"), dict) else j.get("message")
    return False, f"OpenRouter'a bağlanılamadı (HTTP {kod}){': ' + str(msg) if msg else ''}."


def bakiye(anahtar: str = "") -> float | None:
    """Kalan bakiye ($). Önce /credits (toplam yüklenen − toplam harcanan), olmazsa anahtarın kalan limiti.
    Okunamazsa None (gösterge '—' yazar)."""
    anahtar = anahtar or A.anahtar("openrouter")
    if not anahtar:
        return None
    kod, j = _get("/v1/credits", anahtar)
    d = j.get("data", j) if kod == 200 else {}
    if isinstance(d.get("total_credits"), (int, float)) and isinstance(d.get("total_usage"), (int, float)):
        return round(d["total_credits"] - d["total_usage"], 2)
    kod, j = _get("/v1/key", anahtar)
    kalan = (j.get("data", j) if kod == 200 else {}).get("limit_remaining")
    if isinstance(kalan, (int, float)):
        return round(kalan, 2)
    kayit.yaz(f"OpenRouter bakiyesi okunamadı (credits {kod})", "uyari")
    return None


def istemci(anahtar: str):
    import anthropic
    # Kimlik Bearer ile gider; api_key boş bırakılır (OpenRouter belgesindeki Claude Code kurulumu gibi).
    return anthropic.Anthropic(base_url=API, auth_token=anahtar, api_key=None, max_retries=2, timeout=900,
                               default_headers={"X-Title": "Kanal Studyosu"})
