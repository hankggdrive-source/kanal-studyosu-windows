"""Kanallar: ekleme, doğrulama, ayarlar, silme, seçim, kanal dosyaları ve içe aktarma.

Her kanal Kanallar/<kisaltma>/ klasöründedir; bütün ayarları kanal.json'dadır (varsayılanlar config/kanal_varsayilan.json).
Silme kalıcı değildir: klasör Çöp Kutusu'na taşınır. CapCut taslaklarından yalnız Kanal Stüdyosu'nun o kanal için
oluşturduğu ve iki izle doğrulananlar (taslaklar.json kaydı + taslak içindeki işaret dosyası) Çöp'e gider; Kanal
Stüdyosu dışında oluşmuş taslaklara hiçbir durumda dokunulmaz.
"""
from __future__ import annotations

import copy
import json
import math
import re
import shutil
import statistics
import uuid
from datetime import datetime
from pathlib import Path

from . import ayarlar as A
from . import cop
from . import kayit
from . import yollar

DILLER = {"tr": "Türkçe", "it": "İtalyanca", "en": "İngilizce", "de": "Almanca", "es": "İspanyolca",
          "fr": "Fransızca", "pt": "Portekizce", "nl": "Felemenkçe", "pl": "Lehçe", "ru": "Rusça",
          "ar": "Arapça", "ja": "Japonca"}
ASAMALAR = (("konu", "1 · Konu"), ("arastirma", "2 · Araştırma"), ("senaryo", "3 · Senaryo (Türkçe)"),
            ("ceviri", "4 · Hedef dil"), ("sahne", "5 · Sahne paketi"), ("paketleme", "6 · Paketleme"))
PROJE_DOSYALARI = ("00_Yonetici.md", "01_Anayasa.md", "02_Defter.md", "03_Aktif_Video.md")
ALT_KLASORLER = ("Proje_dosyalari", "Beceriler", "Varliklar/Muzik", "Varliklar/Maskot", "Varliklar/Karakter",
                 "Varliklar/son_ekran", "Videolar", "Arsiv", "Uretim", "Silinecekler", "Defter_arsivi")
DOLDUR = "⟦DOLDUR"
ISARET = ".kanal_studyosu.json"          # Kanal Stüdyosu'nun oluşturduğu CapCut taslağının içindeki iz
ATLA = {"arsiv", "videolar", "silinecekler", "defter_arsivi", ".yedek", "skill_eski"}
MEDYA = {".mp3", ".m4a", ".wav", ".aac", ".mov", ".mp4", ".png", ".jpg", ".jpeg", ".webp"}

KISALTMA = re.compile(r"^[a-z0-9][a-z0-9-]{1,30}$")
KOD_ONEKI = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*$")
RENK = re.compile(r"^#[0-9A-Fa-f]{6}$")

# Ortalama konuşma hızı (kelime/dk, ElevenLabs hızı 1,0). tr ve it gerçek bir kanalın değerlerinden (12 dk → Türkçe
# 1600–1800, İtalyanca 1950–2050); diğerleri başlangıç tahmini. Her videodan sonra gerçek ses süresi ölçülür ve kanalın
# kendi hızı bu ölçümlerin ortancası olur (uzunluk.hiz_olcum).
KONUSMA_HIZI = {"tr": 142, "it": 167, "en": 155, "de": 135, "es": 165, "fr": 160, "pt": 160, "nl": 145, "pl": 130,
                "ru": 130, "ar": 120, "ja": 150}
KELIME_PAYI = 0.05        # hesaplanan kelime sayısının ± payı
HIZ_OLCUM_SAYISI = 5      # dil başına saklanan son ölçüm


# --- yollar ---------------------------------------------------------------

def klasor(kisaltma: str) -> Path:
    if not KISALTMA.match(kisaltma or ""):
        raise ValueError("Geçersiz kanal kısaltması")
    return yollar.kanallar() / kisaltma


def _ayar_yolu(kisaltma: str) -> Path:
    return klasor(kisaltma) / "kanal.json"


def varsayilan() -> dict:
    return json.loads((yollar.CONFIG / "kanal_varsayilan.json").read_text(encoding="utf-8"))


# --- okuma ----------------------------------------------------------------

def oku(kisaltma: str) -> dict:
    yol = _ayar_yolu(kisaltma)
    if not yol.exists():
        raise ValueError(f"Kanal bulunamadı: {kisaltma}")
    ham = A.json_oku(yol, {}) or {}
    k = A.birlestir(varsayilan(), ham)
    if "kelime_otomatik" not in (ham.get("uzunluk") or {}):
        k["uzunluk"]["kelime_otomatik"] = False  # bu özellikten önce açılmış kanal: elle girilen kelime aralıkları kalır
    return kelime_hesapla(k)


# --- kelime aralıkları (süre × konuşma hızı) ----------------------------------

def konusma_hizi(k: dict, dil: str) -> tuple[float, int]:
    """→ (kelime/dk, kaç ölçüme dayandığı). Ölçüm yoksa dilin ortalaması. Ses hızı (speed) ile çarpılır."""
    olcum = [x["hiz"] for x in ((k.get("uzunluk") or {}).get("hiz_olcum") or {}).get(dil, [])
             if isinstance(x, dict) and isinstance(x.get("hiz"), (int, float))]
    hiz = statistics.median(olcum) if olcum else KONUSMA_HIZI.get(dil, 150)
    hizi = (k.get("ses") or {}).get("speed") or 1
    return hiz * (float(hizi) if isinstance(hizi, (int, float)) and 0.5 <= hizi <= 2 else 1), len(olcum)


def kelime_araligi(k: dict, dil: str) -> list[int]:
    orta = konusma_hizi(k, dil)[0] * float(k["uzunluk"]["hedef_dk"])
    onluk = lambda x: int(math.floor(x / 10 + 0.5) * 10)  # noqa: E731 (arayüzdeki hesapla aynı yuvarlama)
    return [onluk(orta * (1 - KELIME_PAYI)), onluk(orta * (1 + KELIME_PAYI))]


def kelime_hesapla(k: dict) -> dict:
    """kelime_otomatik açıksa Türkçe ve hedef dil kelime aralıklarını süreden hesaplar (k yerinde değişir)."""
    u = k.get("uzunluk") or {}
    dk = u.get("hedef_dk")
    if u.get("kelime_otomatik") and isinstance(dk, (int, float)) and not isinstance(dk, bool) and 1 <= dk <= 60:
        u["calisma_kelime"] = kelime_araligi(k, "tr")
        u["hedef_kelime"] = kelime_araligi(k, (k.get("dil") or {}).get("hedef") or "tr")
    return k


def hiz_kaydet(kisaltma: str, kod: str, dil: str, kelime: int, sure_sn: float, ses_hizi: float = 1) -> float | None:
    """Bir videonun gerçek ses süresinden konuşma hızını kaydeder (aynı video yeniden ölçülürse eskisinin yerine).
    Akla yatkın olmayan ölçüm (çok kısa ya da 60–260 kelime/dk dışı) kaydedilmez. → kelime/dk (hız 1,0'a göre)."""
    if kelime < 50 or sure_sn < 20:
        return None
    hiz = kelime / (sure_sn / 60) / (ses_hizi if isinstance(ses_hizi, (int, float)) and 0.5 <= ses_hizi <= 2 else 1)
    if not 60 <= hiz <= 260:
        return None
    yol = _ayar_yolu(kisaltma)
    ham = A.json_oku(yol, {}) or {}
    olcum = ham.setdefault("uzunluk", {}).setdefault("hiz_olcum", {})
    eski = [x for x in olcum.get(dil, []) if isinstance(x, dict) and x.get("kod") != kod]
    olcum[dil] = (eski + [{"kod": kod, "hiz": round(hiz, 1), "kelime": kelime, "sure_sn": round(sure_sn, 1),
                           "tarih": datetime.now().isoformat(timespec="seconds")}])[-HIZ_OLCUM_SAYISI:]
    A.json_yaz(yol, ham)
    kayit.yaz(f"Konuşma hızı ölçüldü ({kod}, {DILLER.get(dil, dil)}): {kelime} kelime / {sure_sn / 60:.1f} dk → "
              f"dakikada {hiz:.0f} kelime")
    return hiz


def liste() -> list[dict]:
    sonuc = []
    if not yollar.kanallar().exists():
        return sonuc
    for k in sorted(yollar.kanallar().iterdir()):
        if k.is_dir() and (k / "kanal.json").exists() and KISALTMA.match(k.name):
            try:
                c = oku(k.name)
            except (ValueError, json.JSONDecodeError) as e:
                kayit.yaz(f"Kanal okunamadı ({k.name}): {e}", "uyari")
                continue
            sonuc.append({"kisaltma": c["kisaltma"], "ad": c["ad"], "kod_oneki": c["kod_oneki"],
                          "hedef_dil": c["dil"]["hedef"], "hedef_dil_adi": DILLER.get(c["dil"]["hedef"], ""),
                          "test": bool(c.get("test")), "video_sayisi": len(videolar(k.name))})
    return sonuc


def videolar(kisaltma: str) -> list[str]:
    v = klasor(kisaltma) / "Videolar"
    return sorted(p.name for p in v.iterdir() if p.is_dir()) if v.exists() else []


# --- doğrulama ------------------------------------------------------------

def _sayi(d: dict, yol: str, hatalar: list, en_az=None, en_cok=None, tam=False) -> None:
    parca = yol.split(".")
    x = d
    for p in parca:
        x = x[int(p)] if isinstance(x, list) else x.get(p)
    if isinstance(x, bool) or not isinstance(x, (int, float)) or (tam and int(x) != x):
        hatalar.append(f"{yol}: sayı olmalı")
        return
    if (en_az is not None and x < en_az) or (en_cok is not None and x > en_cok):
        hatalar.append(f"{yol}: {en_az}–{en_cok} arasında olmalı")


def dogrula(k: dict, kendi: str | None = None) -> tuple[list[str], list[str]]:
    """→ (hatalar, uyarılar). kendi: düzenlenen kanalın kısaltması (benzersizlik denetiminde kendisi sayılmaz)."""
    h, u = [], []
    k = kelime_hesapla(copy.deepcopy(k))
    k = dict(k, kisaltma=str(k.get("kisaltma", "")).strip().lower(), kod_oneki=str(k.get("kod_oneki", "")).strip().upper())
    ad = str(k.get("ad", "")).strip()
    if not ad or len(ad) > 60:
        h.append("Kanal adı 1–60 karakter olmalı")
    if not KISALTMA.match(str(k.get("kisaltma", ""))):
        h.append("Kısaltma küçük harf, rakam ve tireyle 2–31 karakter olmalı (ör. bilim-kahvesi, tarih-kanali)")
    if not KOD_ONEKI.match(str(k.get("kod_oneki", ""))) or len(str(k.get("kod_oneki", ""))) > 12:
        h.append("Video kodu öneki büyük harf/rakam, tireyle ayrılabilir, en fazla 12 karakter (ör. BK, TRH-VID)")
    for c in liste():
        if c["kisaltma"] == kendi:
            continue
        if c["kisaltma"] == k.get("kisaltma"):
            h.append(f"'{c['kisaltma']}' kısaltması başka bir kanalda kullanılıyor")
        if c["kod_oneki"].upper() == str(k.get("kod_oneki", "")).upper():
            h.append(f"'{c['kod_oneki']}' öneki '{c['ad']}' kanalında kullanılıyor")
    if k.get("dil", {}).get("hedef") not in DILLER:
        h.append("Hedef dil listeden seçilmeli")
    _sayi(k, "kod_hane", h, 2, 3, tam=True)
    _sayi(k, "uzunluk.hedef_dk", h, 1, 60)
    for alan in () if k["uzunluk"].get("kelime_otomatik") else ("calisma_kelime", "hedef_kelime"):
        _sayi(k, f"uzunluk.{alan}.0", h, 50, 20000, tam=True)
        _sayi(k, f"uzunluk.{alan}.1", h, 50, 20000, tam=True)
        a = k["uzunluk"][alan]
        if all(isinstance(x, (int, float)) for x in a) and a[0] >= a[1]:
            h.append(f"uzunluk.{alan}: alt sınır üst sınırdan küçük olmalı")
    _sayi(k, "uzunluk.kart_karakter", h, 500, 20000, tam=True)
    _sayi(k, "uzunluk.hook_esigi", h, 1, 10)
    s = k.get("ses", {})
    for alan, a, b in (("stability", 0, 1), ("similarity_boost", 0, 1), ("style", 0, 1), ("speed", 0.7, 1.2)):
        _sayi(k, f"ses.{alan}", h, a, b)
    if not s.get("voice_id"):
        u.append("Ses (voice_id) seçilmedi; üretim başlamadan önce gerekli")
    if s.get("language_code") and s["language_code"] != k.get("dil", {}).get("hedef"):
        u.append(f"Ses dil kodu ({s['language_code']}) hedef dilden ({k.get('dil', {}).get('hedef')}) farklı")
    g = k.get("gorsel", {})
    if g.get("karakter") and not re.fullmatch(r"@[\wÀ-ÿ\-]{1,30}", g["karakter"]):
        h.append("Karakter etiketi @ ile başlamalı (ör. @Mira) ya da boş bırakılmalı")
    if not isinstance(g.get("yasakli"), list) or not isinstance(g.get("izinli_olumsuz"), list):
        h.append("Yasaklı kelimeler ve izinli olumsuzlamalar liste olmalı")
    e = k.get("etiketler", {})
    sen = e.get("senaryo", {})
    if not isinstance(sen, dict) or set(sen) != {"karakter", "metafor", "sema", "ilk30"} or \
            not all(re.fullmatch(r"[\wÀ-ÿ★\-]{1,20}", str(x)) for x in sen.values()):
        h.append("Senaryo etiketleri: karakter, metafor, şema ve ilk 30 sn için birer kısa ad (boşluksuz)")
    elif len(set(sen.values())) < 4:
        h.append("Senaryo etiketleri birbirinden farklı olmalı")
    if not isinstance(e.get("ses"), list) or not e["ses"] or \
            not all(re.fullmatch(r"[a-z][a-z ]{1,20}", str(x)) for x in e["ses"]):
        h.append("Ses tag'leri küçük harfli kısa kelimeler olmalı (ör. calm, softly)")
    _sayi(k, "etiketler.tag_orani", h, 0, 100)
    m = k.get("montaj", {})
    _sayi(k, "montaj.son_ekran_sn", h, 0, 30)
    _sayi(k, "montaj.muzik_lufs", h, -60, -10)
    mk = m.get("maskot", {})
    n = len(mk.get("dosyalar", []))
    gecersiz = [x for x in mk.get("sira", []) if not re.fullmatch(r"M\d", str(x)) or not 1 <= int(str(x)[1:]) <= n]
    if gecersiz:
        h.append(f"Maskot sırası yalnız M1…M{n} içerebilir ({', '.join(map(str, gecersiz))} geçersiz)" if n else
                 "Maskot dosyası yokken maskot sırası boş olmalı")
    alt = m.get("altyazi", {})
    for r in ("yazi", "kutu"):
        if not RENK.match(str(alt.get(r, ""))):
            h.append(f"Altyazı {('yazı' if r == 'yazi' else 'kutu')} rengi #RRGGBB olmalı")
    _sayi(k, "montaj.altyazi.kutu_opaklik", h, 0, 1)
    _sayi(k, "montaj.altyazi.boyut", h, 1, 40)
    if set(k.get("onaylar", {})) - {x for x, _ in ASAMALAR if x not in ("sahne",)}:
        h.append("Onaylar yalnız konu, araştırma, senaryo, çeviri ve paketleme için ayarlanır")
    modeller = A.genel()["modeller"]
    for is_adi, isa in k.get("isler", {}).items():
        if isa.get("model") not in modeller:
            h.append(f"{is_adi}: bilinmeyen model {isa.get('model')}")
    _sayi(k, "butce.video_usd", h, 0.01, 500)
    for etiket, desen in (k.get("kalip_sayaclari") or {}).items():
        try:
            re.compile(desen)
        except re.error:
            h.append(f"Kalıp sayacı '{etiket}': geçersiz düzenli ifade")
    for kelime in k.get("hassas_kelimeler") or []:
        try:
            re.compile(kelime)
        except re.error:
            h.append(f"Hassas kelime '{kelime}': geçersiz düzenli ifade")
    return h, u


# --- ekleme ---------------------------------------------------------------

def _yer_tutucular(k: dict) -> dict[str, str]:
    return {"{{KANAL_ADI}}": k["ad"], "{{KOD_ONEKI}}": k["kod_oneki"],
            "{{HEDEF_DIL}}": DILLER.get(k["dil"]["hedef"], k["dil"]["hedef"]), "{{HEDEF_DIL_KODU}}": k["dil"]["hedef"]}


def _sablon_yaz(k: dict, hedef: Path) -> None:
    kaynak = yollar.SABLONLAR / "kanal"
    yer = _yer_tutucular(k)
    for dosya in kaynak.rglob("*.md"):
        metin = dosya.read_text(encoding="utf-8")
        for a, b in yer.items():
            metin = metin.replace(a, b)
        A.atomik_yaz(hedef / dosya.relative_to(kaynak), metin)


def anayasa_metni(govde: str, k: dict) -> str:
    """Yeni kanal dosyasının B bölümünden 01_Anayasa.md: şablonun baş kısmı (doldurma notu olmadan) + gövde."""
    sablon = (yollar.SABLONLAR / "kanal" / "Proje_dosyalari" / "01_Anayasa.md").read_text(encoding="utf-8")
    bas = sablon.split("\n## 1.", 1)[0]
    bas = "\n".join(x for x in bas.split("\n") if not x.startswith(">")).replace(
        "Sürüm 1 · kanal açıldı.", "Sürüm 1 · kanal açıldı (yeni kanal dosyasından).")
    metin = re.sub(r"\n{3,}", "\n\n", bas.rstrip()) + "\n\n" + govde.strip() + "\n"
    for a, b in _yer_tutucular(k).items():
        metin = metin.replace(a, b)
    return metin


def ekle(veri: dict, kaynak: str = "sablon", ice_aktar_klasor: str = "", anayasa: str = "") -> dict:
    """Yeni kanal: doğrular, klasörleri kurar, kanal.json'u yazar, şablonları (ya da içe aktarılanları) koyar.
    anayasa: yeni kanal dosyasının anayasa bölümü (varsa 01_Anayasa.md olur)."""
    k = A.birlestir(varsayilan(), veri or {})
    k["kisaltma"] = str(k.get("kisaltma", "")).strip().lower()
    k["kod_oneki"] = str(k.get("kod_oneki", "")).strip().upper()
    if not k["ses"].get("language_code"):
        k["ses"]["language_code"] = k["dil"]["hedef"]
    kelime_hesapla(k)
    hatalar, _ = dogrula(k)
    if hatalar:
        raise ValueError("; ".join(hatalar))
    hedef = klasor(k["kisaltma"])
    if hedef.exists():
        raise ValueError(f"Kanallar/{k['kisaltma']} klasörü zaten var")
    if kaynak == "klasor" and not Path(ice_aktar_klasor).expanduser().is_dir():
        raise ValueError("İçe aktarılacak klasör bulunamadı")
    k.update(kimlik=uuid.uuid4().hex, olusturma=datetime.now().isoformat(timespec="seconds"))
    gecici = hedef.with_name(f".{k['kisaltma']}.kuruluyor")
    if gecici.exists():
        shutil.rmtree(gecici)  # yarım kalmış önceki kurulum (uygulamanın kendi ara klasörü)
    try:
        for alt in ALT_KLASORLER:
            (gecici / alt).mkdir(parents=True, exist_ok=True)
        _sablon_yaz(k, gecici)
        A.json_yaz(gecici / "kanal.json", k)
        A.json_yaz(gecici / "taslaklar.json", [])
        rapor = ice_aktar(gecici, Path(ice_aktar_klasor).expanduser()) if kaynak == "klasor" else []
        if (anayasa or "").strip():
            A.atomik_yaz(gecici / "Proje_dosyalari" / "01_Anayasa.md", anayasa_metni(anayasa, k))
            rapor.append("Anayasa: yeni kanal dosyasından")
        gecici.rename(hedef)
    except Exception:
        shutil.rmtree(gecici, ignore_errors=True)
        raise
    kayit.yaz(f"Kanal eklendi: {k['ad']} ({k['kisaltma']}, {k['kod_oneki']}, {DILLER[k['dil']['hedef']]})")
    if aktif() is None:
        aktif_sec(k["kisaltma"])
    return {"kanal": k, "ice_aktarma": rapor}


# --- içe aktarma ----------------------------------------------------------

_BECERI_ESLEME = (("konu", "konu"), ("arastirma", "arastirma"), ("senaryo", "senaryo"), ("ceviri", "ceviri"),
                  ("italyanca", "ceviri"), ("hedef", "ceviri"), ("translat", "ceviri"), ("sahne", "sahne"),
                  ("paketleme", "paketleme"))


def ice_aktar(kanal_klasoru: Path, kaynak: Path) -> list[str]:
    """kaynak klasördeki beceri, proje dosyası ve medyayı kanal klasörüne KOPYALAR (kaynak değişmez).
    Arsiv/Videolar/Silinecekler gibi klasörlerdeki eski kopyalar atlanır; aynı hedefe birden çok aday varsa
    adında CURRENT geçen, sonra en üst klasördeki seçilir."""
    rapor = []

    def uygun(p: Path) -> bool:
        return not any(x.lower().startswith(tuple(ATLA)) for x in p.relative_to(kaynak).parts[:-1])

    def sec(adaylar: dict[str, list[Path]]) -> dict[str, Path]:
        return {h: min(l, key=lambda p: ("CURRENT" not in p.name, len(p.relative_to(kaynak).parts), len(p.name)))
                for h, l in adaylar.items()}

    beceri: dict[str, list[Path]] = {}
    for skill in kaynak.rglob("SKILL.md"):
        ad = skill.parent.name.lower()
        hedef = next((h for anahtar, h in _BECERI_ESLEME if anahtar in ad), None)
        if hedef and uygun(skill):
            beceri.setdefault(hedef, []).append(skill)
    for hedef, skill in sorted(sec(beceri).items()):
        shutil.copy2(skill, kanal_klasoru / "Beceriler" / hedef / "SKILL.md")
        rapor.append(f"Beceri: {skill.parent.name} → {hedef}")
    proje: dict[str, list[Path]] = {}
    for md in kaynak.rglob("*.md"):
        m = re.match(r"(?:[A-Za-z]+_)?0([0-3])_", md.name)
        if m and md.name != "SKILL.md" and uygun(md):
            proje.setdefault(PROJE_DOSYALARI[int(m.group(1))], []).append(md)
    for hedef, md in sorted(sec(proje).items()):
        shutil.copy2(md, kanal_klasoru / "Proje_dosyalari" / hedef)
        rapor.append(f"Proje dosyası: {md.name} → {hedef}")
    for ad, alt in (("muzik", "Muzik"), ("maskot", "Maskot")):
        for d in (p for p in kaynak.rglob("*") if p.is_dir() and p.name.lower() == ad and uygun(p / "x")):
            for f in sorted(d.iterdir()):
                if f.is_file() and f.suffix.lower() in MEDYA:
                    shutil.copy2(f, kanal_klasoru / "Varliklar" / alt / f.name)
                    rapor.append(f"{alt}: {f.name}")
    return rapor


# --- güncelleme -----------------------------------------------------------

def guncelle(kisaltma: str, degisiklik: dict) -> tuple[dict, list[str]]:
    eski = oku(kisaltma)
    degisiklik = dict(degisiklik or {})
    for sabit in ("kisaltma", "kimlik", "olusturma"):
        degisiklik.pop(sabit, None)
    if "kod_oneki" in degisiklik:
        degisiklik["kod_oneki"] = str(degisiklik["kod_oneki"]).strip().upper()
    yeni = A.birlestir(eski, degisiklik)
    # Listeler birleştirilmez, olduğu gibi alınır
    for yol in (("gorsel", "yasakli"), ("gorsel", "izinli_olumsuz"), ("etiketler", "ses"), ("montaj", "maskot", "dosyalar"),
                ("montaj", "maskot", "sira"), ("hassas_kelimeler",), ("uzunluk", "calisma_kelime"), ("uzunluk", "hedef_kelime"),
                ("kalip_sayaclari",), ("etiketler", "ses_sinir")):
        kaynak = degisiklik
        for p in yol:
            kaynak = kaynak.get(p) if isinstance(kaynak, dict) else None
        if isinstance(kaynak, list) or (isinstance(kaynak, dict) and yol in (("kalip_sayaclari",), ("etiketler", "ses_sinir"))):
            hedef = yeni
            for p in yol[:-1]:
                hedef = hedef[p]
            hedef[yol[-1]] = kaynak
    if videolar(kisaltma):
        for alan, ad in ((("kod_oneki",), "Video kodu öneki"), (("dil", "hedef"), "Hedef dil")):
            a, b = eski, yeni
            for p in alan:
                a, b = a[p], b[p]
            if a != b:
                raise ValueError(f"{ad} bu kanalda video üretildikten sonra değiştirilemez")
    hatalar, uyarilar = dogrula(yeni, kendi=kisaltma)
    if hatalar:
        raise ValueError("; ".join(hatalar))
    if eski["dil"]["hedef"] != yeni["dil"]["hedef"]:
        uyarilar.append("Hedef dil değişti: beceri ve proje dosyalarında eski dil adı geçiyor olabilir; kontrol et")
    A.json_yaz(_ayar_yolu(kisaltma), yeni)
    kayit.yaz(f"Kanal ayarları kaydedildi: {yeni['ad']}")
    return yeni, uyarilar


# --- silme ----------------------------------------------------------------

def taslaklar_dosyasi(kisaltma: str) -> Path:
    return klasor(kisaltma) / "taslaklar.json"


def taslak_kaydet(kisaltma: str, taslak_klasoru: Path) -> None:
    """Kanal Stüdyosu bir CapCut taslağı oluşturunca çağırır: iki iz bırakır (kayıt + taslak içindeki işaret)."""
    k = oku(kisaltma)
    taslak_klasoru = Path(taslak_klasoru)
    A.json_yaz(taslak_klasoru / ISARET, {"kanal_kimlik": k["kimlik"], "kanal": kisaltma,
                                         "olusturma": datetime.now().isoformat(timespec="seconds")})
    kayitli = A.json_oku(taslaklar_dosyasi(kisaltma), []) or []
    if taslak_klasoru.name not in kayitli:
        A.json_yaz(taslaklar_dosyasi(kisaltma), kayitli + [taslak_klasoru.name])


def silinecek_taslaklar(kisaltma: str) -> tuple[list[Path], list[str]]:
    """→ (Çöp'e gidecek taslak klasörleri, dokunulmayacakların nedenleri)."""
    k = oku(kisaltma)
    kok = A.yol("capcut_taslak")
    gidecek, kalan = [], []
    for ad in A.json_oku(taslaklar_dosyasi(kisaltma), []) or []:
        if not isinstance(ad, str) or "/" in ad or ad in ("", ".", ".."):
            continue
        t = kok / ad
        if not t.is_dir():
            continue
        isaret = A.json_oku(t / ISARET, None)
        if isinstance(isaret, dict) and isaret.get("kanal_kimlik") == k["kimlik"]:
            gidecek.append(t)
        else:
            kalan.append(f"{ad}: Kanal Stüdyosu işareti yok ya da başka kanala ait; dokunulmadı")
    return gidecek, kalan


def sil(kisaltma: str, onay_adi: str) -> dict:
    k = oku(kisaltma)
    if str(onay_adi).strip().casefold() != k["ad"].strip().casefold():
        raise ValueError("Silmek için kanal adını aynen yaz")
    akt = A.json_oku(yollar.aktif_dosyasi(), {}) or {}
    if (akt.get("uretim") or {}).get("kanal") == kisaltma:
        raise ValueError("Bu kanalda süren bir üretim var; önce üretimi kapat ya da iptal et")
    gidecek, kalan = silinecek_taslaklar(kisaltma)
    tasinan = []
    for t in gidecek:
        cop.tasi(t)
        tasinan.append(f"CapCut taslağı: {t.name}")
    cop.tasi(klasor(kisaltma))
    tasinan.append(f"Kanal klasörü: Kanallar/{kisaltma}")
    if akt.get("kanal") == kisaltma:
        akt.pop("kanal", None)
        diger = liste()
        if diger:
            akt["kanal"] = diger[0]["kisaltma"]
        A.json_yaz(yollar.aktif_dosyasi(), akt)
    kayit.yaz(f"Kanal silindi (Çöp Kutusu'na taşındı): {k['ad']} · {len(tasinan)} öğe")
    return {"tasinan": tasinan, "dokunulmayan": kalan}


# --- seçim ----------------------------------------------------------------

def aktif() -> str | None:
    k = (A.json_oku(yollar.aktif_dosyasi(), {}) or {}).get("kanal")
    return k if k and (yollar.kanallar() / k / "kanal.json").exists() else None


def aktif_sec(kisaltma: str) -> None:
    oku(kisaltma)
    akt = A.json_oku(yollar.aktif_dosyasi(), {}) or {}
    if (akt.get("uretim") or {}).get("kanal") not in (None, kisaltma):
        raise ValueError("Süren bir üretim varken kanal değiştirilemez")
    akt["kanal"] = kisaltma
    A.json_yaz(yollar.aktif_dosyasi(), akt)


# --- kanal dosyaları (proje dosyaları ve beceriler) -------------------------

def _dosya_yolu(kisaltma: str, ad: str) -> Path:
    if ad in PROJE_DOSYALARI:
        return klasor(kisaltma) / "Proje_dosyalari" / ad
    m = re.fullmatch(r"Beceriler/([a-z]+)/SKILL\.md", ad)
    if m and m.group(1) in dict(ASAMALAR):
        return klasor(kisaltma) / ad
    raise ValueError("Bu dosya düzenlenemez")


def dosyalar(kisaltma: str) -> list[dict]:
    sonuc = []
    for ad in list(PROJE_DOSYALARI) + [f"Beceriler/{a}/SKILL.md" for a, _ in ASAMALAR]:
        yol = _dosya_yolu(kisaltma, ad)
        metin = yol.read_text(encoding="utf-8") if yol.exists() else ""
        sonuc.append({"ad": ad, "var": yol.exists(), "doldur": metin.count(DOLDUR), "boyut": len(metin)})
    return sonuc


def dosya_oku(kisaltma: str, ad: str) -> str:
    yol = _dosya_yolu(kisaltma, ad)
    return yol.read_text(encoding="utf-8") if yol.exists() else ""


def dosya_yaz(kisaltma: str, ad: str, icerik: str) -> None:
    """Önceki hâl kanal klasöründeki .yedek/ altına tarihli kopya olarak saklanır."""
    yol = _dosya_yolu(kisaltma, ad)
    if yol.exists():
        yedek = klasor(kisaltma) / ".yedek" / f"{datetime.now():%Y%m%d_%H%M%S}_{ad.replace('/', '_')}"
        yedek.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(yol, yedek)
    A.atomik_yaz(yol, icerik)


# --- üretime hazırlık -------------------------------------------------------

def eksikler(kisaltma: str) -> list[dict]:
    """Üretim başlamadan tamamlanması gerekenler (zorunlu) ve öneriler."""
    k = oku(kisaltma)
    kl = klasor(kisaltma)
    sonuc = []
    if not k["ses"].get("voice_id"):
        sonuc.append({"zorunlu": True, "mesaj": "Kanal ayarları › Ses: ElevenLabs sesi (voice_id) seçilmedi"})
    doldurulmamis = [d["ad"] for d in dosyalar(kisaltma) if d["doldur"]]
    if doldurulmamis:
        sonuc.append({"zorunlu": False, "mesaj": "Kanal dosyalarında doldurulmamış yer var: " + ", ".join(doldurulmamis)})
    if k["montaj"]["muzik"] and not any(f.suffix.lower() in {".mp3", ".m4a", ".wav", ".aac"}
                                        for f in (kl / "Varliklar/Muzik").glob("*")):
        sonuc.append({"zorunlu": False, "mesaj": "Müzik açık ama Varliklar/Muzik klasörü boş (müziksiz üretilir)"})
    for f in k["montaj"]["maskot"]["dosyalar"]:
        if not (kl / "Varliklar/Maskot" / f).exists():
            sonuc.append({"zorunlu": True, "mesaj": f"Maskot dosyası yok: Varliklar/Maskot/{f}"})
    if k["gorsel"]["karakter"] and not any((kl / "Varliklar/Karakter").glob("*")):
        sonuc.append({"zorunlu": False, "mesaj": f"{k['gorsel']['karakter']} için Varliklar/Karakter'e referans görsel koyabilirsin"})
    return sonuc
