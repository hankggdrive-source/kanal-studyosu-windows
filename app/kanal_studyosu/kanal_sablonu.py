"""Yeni kanal dosyası: kanal bilgileri + kanal anayasası tek metinde.

Kullanıcı şablonu (Yeni_Kanal_Sablonu.md) herhangi bir yapay zekaya verip kanalına göre doldurtur, sonra uygulamaya
yapıştırır. Okuma kodla yapılır (yapay zeka kullanılmaz). A bölümü `Alan: değer` satırlarıdır ve kanal ayarlarına
çevrilir; B bölümü olduğu gibi kanalın 01_Anayasa.md dosyası olur. Eksik ya da hatalı alanlar formda işaretlenir.
Ses, maskot, müzik ve onaylar dosyada yoktur, uygulamada seçilir.
"""
from __future__ import annotations

import re

from . import ayarlar as A
from . import kanallar
from . import yollar

DOSYA_ADI = "Yeni_Kanal_Sablonu.md"
A_BASLIK = "=== A · KANAL BİLGİLERİ ==="
B_BASLIK = "=== B · KANAL ANAYASASI ==="
_A_DESEN = re.compile(r"\bA\s*[·.:\-–]\s*KANAL\s+B[İI]LG[İI]LER[İI]", re.I)
_B_DESEN = re.compile(r"\bB\s*[·.:\-–]\s*KANAL\s+ANAYASASI", re.I)

# (etiket, yol, tür, açıklama, zorunlu)
ALANLAR = (
    ("Kanal adı", "ad", "metin", "YouTube'daki kanal adı.", True),
    ("Video dili", "dil.hedef", "dil", "Videoların seslendirileceği dil: " + ", ".join(kanallar.DILLER.values()) + ".",
     True),
    ("Video süresi (dakika)", "uzunluk.hedef_dk", "sayi", "Bir videonun hedef uzunluğu, ör. 12. Kelime sayısını "
     "uygulama bundan hesaplar.", True),
    ("Görsel oranı", "gorsel.oran", "oran", "16:9 (yatay) ya da 9:16 (dikey). Boşsa 16:9.", False),
    ("Flow karakter etiketi", "gorsel.karakter", "karakter", "Sahnelerde tekrar eden bir karakter varsa @ ile adı "
     "(ör. @Mira); yoksa boş bırak.", False),
    ("Karakter sahnesi etiketi", "etiketler.senaryo.karakter", "etiket", "Senaryoda karakterli paragrafların başına "
     "yazılan kısa ad, büyük harf ve boşluksuz (ör. MIRA). Boşsa KARAKTER.", False),
    ("Karakterin yüz ifadesi notu", "gorsel.ifade_notu", "metin", "İsteğe bağlı: karakterin yüz ifadeleri nasıl "
     "olmalı.", False),
    ("Görsel kurallar", "gorsel.kurallar", "metin", "Kanalın görsellerinde neye dikkat edilir (ör. yazı ve logo yok, "
     "çocuk figürü yok). Boşsa genel kurallar kullanılır.", False),
    ("Ek yasaklı görsel kelimeler", "gorsel.yasakli", "liste_ek", "İngilizce, virgülle. Görsel promptlarında asla "
     "geçmeyecek kelimeler; genel güvenlik listesine eklenir.", False),
    ("Hassas kelimeler", "hassas_kelimeler", "liste", "Video dilinde, virgülle. Başlık, açıklama ve ilk 30 saniyede "
     "kullanılmayacak kelimeler (kök yazılabilir).", False),
    ("Seslendirme tonu tag'leri", "etiketler.ses", "liste", "İngilizce, küçük harf, virgülle (ör. calm, softly, warm). "
     "Boşsa varsayılan liste.", False),
    ("Kapanış imzası", "imza", "metin", "Her videonun sonunda aynen tekrar eden tek satır, video dilinde. Yoksa boş.",
     False),
    ("Altyazı yazı tipi", "montaj.altyazi.yazi_tipi", "metin", "Bilgisayarda kurulu bir yazı tipi (ör. Nunito).", False),
    ("Altyazı yazı rengi", "montaj.altyazi.yazi", "renk", "#RRGGBB biçiminde.", False),
    ("Altyazı kutu rengi", "montaj.altyazi.kutu", "renk", "#RRGGBB biçiminde.", False),
    ("Kısaltma", "kisaltma", "metin", "İsteğe bağlı: kanal klasörünün adı (küçük harf, rakam, tire). Boşsa addan "
     "önerilir.", False),
    ("Video kodu öneki", "kod_oneki", "metin", "İsteğe bağlı: videolar ÖNEK-01, ÖNEK-02 diye adlanır (ör. BK). Boşsa "
     "addan önerilir.", False),
)

_BOS = {"", "-", "—", "yok", "boş", "bos", "none", "n/a", "na", "null", "isteğe bağlı", "istege bagli"}
_DIL_ADLARI = {
    "tr": ("türkçe", "turkce", "turkish", "türk"), "it": ("italyanca", "italian", "italiano"),
    "en": ("ingilizce", "english"), "de": ("almanca", "german", "deutsch"),
    "es": ("ispanyolca", "spanish", "español", "espanol"), "fr": ("fransızca", "fransizca", "french",
                                                                              "français", "francais"),
    "pt": ("portekizce", "portuguese", "português", "portugues"), "nl": ("felemenkçe", "hollandaca", "dutch",
                                                                        "nederlands"),
    "pl": ("lehçe", "lehce", "polish", "polski"), "ru": ("rusça", "rusca", "russian", "русский"),
    "ar": ("arapça", "arapca", "arabic", "العربية"), "ja": ("japonca", "japanese", "日本語"),
}


# --- şablon ---------------------------------------------------------------

def _anayasa_govdesi() -> str:
    metin = (yollar.SABLONLAR / "kanal" / "Proje_dosyalari" / "01_Anayasa.md").read_text(encoding="utf-8")
    i = metin.find("\n## 1.")
    return metin[i + 1:] if i >= 0 else metin


def sablon_metni() -> str:
    satirlar = [
        "# KANAL STÜDYOSU · YENİ KANAL DOSYASI", "",
        "Bu dosyayla yeni bir kanal tek seferde eklenir.", "",
        "1. Bu dosyanın tamamını bir yapay zekaya (Claude, ChatGPT…) ver.",
        "2. Altına kanalını birkaç cümleyle anlat: konusu, kimin için, hangi dilde, videolar kaç dakika, anlatıcı nasıl,",
        "   görseller nasıl (karakter var mı, renkler).",
        "3. Yapay zekanın doldurduğu dosyayı Kanal Stüdyosu'nda Kanal ekle › Dosyayla ekle'ye yapıştır ya da dosyayı seç.",
        "",
        "Ses (ElevenLabs), maskot, müzik ve onaylar uygulamada seçilir; bu dosyada yoktur. Eksik kalan yerleri uygulama",
        "gösterir. Anayasa sonradan Kanal dosyaları › 01_Anayasa.md'den de düzenlenebilir.", "",
        "> YAPAY ZEKAYA TALİMAT: Aşağıdaki A ve B bölümlerini kullanıcının anlattığı kanala göre doldur ve dosyanın",
        "> tamamını geri ver. A bölümünde satır adlarını ve === başlıklarını değiştirme; her satırda iki noktadan sonrasını",
        "> yaz, bilmediğini boş bırak. B bölümünde ⟦DOLDUR: …⟧ işaretlerinin yerine kanala uygun metni yaz ve işareti sil;",
        "> diğer maddeleri kanala uymuyorsa düzelt ama başlıkları silme. {{KANAL_ADI}} gibi çift süslü parantezli yerlere",
        "> dokunma, onları uygulama doldurur. Bilgi eksikse önce kullanıcıya sor.", "",
        A_BASLIK, "",
    ]
    for etiket, _yol, _tur, aciklama, zorunlu in ALANLAR:
        satirlar += [f"> {aciklama}" + (" (zorunlu)" if zorunlu else ""), f"{etiket}: ", ""]
    satirlar += [B_BASLIK, "", _anayasa_govdesi().rstrip(), ""]
    return "\n".join(satirlar)


def sablon_dosyasi_yaz() -> None:
    """Kurulum klasörüne şablonu koyar (yoksa). Var olan dosyaya dokunulmaz (kullanıcı içine yazmış olabilir)."""
    yol = yollar.kok() / DOSYA_ADI
    if not yol.exists():
        A.atomik_yaz(yol, sablon_metni())


# --- okuma ----------------------------------------------------------------

def _normal(s: str) -> str:
    """Karşılaştırma için: küçük harf, ı/i ve İ/I aynı sayılır (BÜYÜK HARFLE yazılmış satır adı da tanınır)."""
    s = s.replace("İ", "i").lower().replace("ı", "i").replace("\u0307", "").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()


_ETIKETLER = {_normal(e): (e, y, t, z) for e, y, t, _, z in ALANLAR}


def _bolumler(metin: str) -> tuple[str, str]:
    satirlar = [x for x in metin.replace("\r\n", "\n").split("\n") if not re.fullmatch(r"\s*```\w*\s*", x)]
    a = next((i for i, x in enumerate(satirlar) if _A_DESEN.search(x)), None)
    b = next((i for i, x in enumerate(satirlar) if _B_DESEN.search(x)), None)
    a_bolum = satirlar[(a + 1 if a is not None else 0):(b if b is not None else len(satirlar))]
    b_bolum = satirlar[b + 1:] if b is not None else []
    return "\n".join(a_bolum), "\n".join(b_bolum).strip()


def _satirlar(a_bolum: str) -> dict[str, str]:
    """`Alan: değer` satırları; bir alanın altındaki etiketsiz satırlar o alana eklenir (çok satırlı değer)."""
    degerler: dict[str, list[str]] = {}
    simdiki = None
    for ham in a_bolum.split("\n"):
        x = ham.strip()
        if x.startswith(">") or x.startswith("#"):
            simdiki = None if x.startswith("#") else simdiki
            continue
        temiz = re.sub(r"^[-*•]\s+", "", x).replace("**", "").replace("__", "")
        m = re.match(r"^([^:]{2,60}?)\s*:\s*(.*)$", temiz)
        if m and _normal(m.group(1)) in _ETIKETLER:
            simdiki = _normal(m.group(1))
            degerler[simdiki] = [m.group(2).strip()]
        elif simdiki and x:
            degerler[simdiki].append(temiz)
    return {k: "\n".join(v).strip() for k, v in degerler.items()}


def _bos_mu(v: str) -> bool:
    v = v.strip()
    return _normal(v) in _BOS or v.startswith("⟦") or (v.startswith("(") and v.endswith(")"))


def _dil(v: str) -> str | None:
    n = _normal(v)
    m = re.search(r"\(([a-z]{2})\)", n)
    if m and m.group(1) in kanallar.DILLER:
        return m.group(1)
    if n in kanallar.DILLER:
        return n
    for kod, adlar in _DIL_ADLARI.items():
        if any(re.search(rf"(^|[^\w]){re.escape(a)}($|[^\w])", n) for a in adlar):
            return kod
    return None


def _cevir(tur: str, v: str):
    """→ (değer, hata). Hata varsa değer None."""
    if tur == "metin":
        return v, None
    if tur == "dil":
        d = _dil(v)
        return (d, None) if d else (None, "dil tanınmadı")
    if tur == "sayi":
        m = re.search(r"\d+(?:[.,]\d+)?", v)
        if not m:
            return None, "sayı yok"
        x = float(m.group().replace(",", "."))
        return (int(x) if x == int(x) else x), None
    if tur == "oran":
        return ("9:16" if re.search(r"9\s*:\s*16|dikey|vertical|portrait", v, re.I) else "16:9"), None
    if tur == "karakter":
        if not v.strip().startswith("@") and re.search(r"(^|\W)(yok|none|no|karaktersiz)(\W|$)", _normal(v)):
            return "", None
        ad = v.split()[0].strip(".,;") if v.split() else ""
        return ("@" + ad.lstrip("@")) if ad else "", None
    if tur == "etiket":
        return v.split()[0].strip("[]").strip(".,;").upper(), None
    if tur in ("liste", "liste_ek"):
        return [x.strip().strip("\"'") for x in re.split(r"[,\n;]", v) if x.strip().strip("\"'")], None
    if tur == "renk":
        m = re.search(r"#[0-9A-Fa-f]{6}\b", v)
        return (m.group().upper(), None) if m else (None, "#RRGGBB biçiminde değil")
    return v, None


def _oner_kisaltma(ad: str, kullanilan: set[str]) -> str:
    tr = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiucgiosu")
    taban = re.sub(r"[^a-z0-9]+", "-", ad.translate(tr).lower()).strip("-")[:28] or "kanal"
    if len(taban) < 2:
        taban = (taban + "-kanal")[:28]
    aday, n = taban, 2
    while aday in kullanilan:
        aday, n = f"{taban}-{n}", n + 1
    return aday


def _oner_onek(ad: str, kullanilan: set[str]) -> str:
    tr = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiuCGIOSU")
    kelimeler = re.findall(r"[A-Za-z0-9]+", ad.translate(tr))
    taban = ("".join(k[0] for k in kelimeler) if len(kelimeler) > 1 else (kelimeler[0][:3] if kelimeler else "KN")).upper()
    taban = re.sub(r"^[0-9]+", "", taban)[:8] or "KN"
    aday, n = taban, 2
    while aday in kullanilan:
        aday, n = f"{taban}{n}", n + 1
    return aday


def oku(metin: str) -> dict:
    """Doldurulmuş dosyayı okur → {kanal, anayasa, eksik: [{yol, etiket, neden}], hatalar, uyarilar, okunan, doldur}.
    kanal: varsayılanlarla birleşmiş, kaydedilmeye hazır taslak (kısaltma ve önek boşsa addan önerilir)."""
    if not (metin or "").strip():
        raise ValueError("Metin boş. Doldurulmuş kanal dosyasını yapıştır.")
    a_bolum, b_bolum = _bolumler(metin)
    satir = _satirlar(a_bolum)
    if not satir:
        raise ValueError("Dosyada kanal bilgisi satırı bulunamadı. 'Kanal adı: …' gibi satırlar olmalı "
                         "(Şablonu kopyala ile yeni şablon alabilirsin).")
    k = kanallar.varsayilan()
    k["uzunluk"]["kelime_otomatik"] = True
    eksik, okunan = [], 0
    for anahtar, (etiket, yol, tur, zorunlu) in _ETIKETLER.items():
        v = satir.get(anahtar, "")
        if _bos_mu(v):
            if zorunlu:
                eksik.append({"yol": yol, "etiket": etiket, "neden": "boş"})
            continue
        deger, hata = _cevir(tur, v)
        if hata:
            eksik.append({"yol": yol, "etiket": etiket, "neden": f"{hata}: {v[:60]}"})
            continue
        if tur == "liste_ek":
            deger = list(dict.fromkeys(_al(k, yol) + [x.lower() for x in deger]))
        elif tur == "liste" and not deger:
            continue
        elif yol == "etiketler.ses":
            deger = [x.lower() for x in deger]
        _koy(k, yol, deger)
        okunan += 1
    kullanilan = {c["kisaltma"] for c in kanallar.liste()}
    onekler = {c["kod_oneki"].upper() for c in kanallar.liste()}
    if k.get("ad") and not k.get("kisaltma"):
        k["kisaltma"] = _oner_kisaltma(k["ad"], kullanilan)
    if k.get("ad") and not k.get("kod_oneki"):
        k["kod_oneki"] = _oner_onek(k["ad"], onekler)
    k["kisaltma"], k["kod_oneki"] = str(k["kisaltma"]).strip().lower(), str(k["kod_oneki"]).strip().upper()
    k["ses"]["language_code"] = k["dil"]["hedef"]
    kanallar.kelime_hesapla(k)
    hatalar, uyarilar = kanallar.dogrula(k)
    eksik_yollar = {e["yol"] for e in eksik}
    hatalar = [h for h in hatalar if not any(h.startswith(p) for p in _hata_onekleri(eksik_yollar))]
    uyarilar = [u for u in uyarilar if "voice_id" not in u]  # ses formda seçilir
    if not b_bolum:
        uyarilar.append("Dosyada anayasa bölümü (=== B · KANAL ANAYASASI ===) bulunamadı; anayasa genel şablondan "
                        "başlar.")
    doldur = b_bolum.count(kanallar.DOLDUR)
    if doldur:
        uyarilar.append(f"Anayasada {doldur} doldurulmamış yer (⟦DOLDUR⟧) kaldı; sonra Kanal dosyaları › "
                        "01_Anayasa.md'den tamamlayabilirsin.")
    return {"kanal": k, "anayasa": b_bolum, "eksik": eksik, "hatalar": hatalar, "uyarilar": uyarilar,
            "okunan": okunan, "doldur": doldur}


def _hata_onekleri(yollar_: set[str]) -> tuple[str, ...]:
    """Eksik listesinde zaten gösterilen alanların doğrulama mesajları tekrar edilmez."""
    on = []
    if "ad" in yollar_:
        on += ["Kanal adı", "Kısaltma", "Video kodu öneki"]
    if "uzunluk.hedef_dk" in yollar_:
        on.append("uzunluk.hedef_dk")
    if "dil.hedef" in yollar_:
        on.append("Hedef dil")
    if yollar_ & {"montaj.altyazi.yazi", "montaj.altyazi.kutu"}:
        on.append("Altyazı")
    return tuple(on)


def _al(o: dict, yol: str):
    for p in yol.split("."):
        o = o[p]
    return o


def _koy(o: dict, yol: str, v) -> None:
    p = yol.split(".")
    for x in p[:-1]:
        o = o.setdefault(x, {})
    o[p[-1]] = v
