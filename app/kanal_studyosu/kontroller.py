"""Modele gitmeden yapılan kontroller.

hatalar  → otomatik düzeltme turuna girer (aşamaya "düzeltme: …" olarak gider).
uyarilar → düzeltme istemez; ONAY ekranında "dikkat" olarak gösterilir.
Kurallar becerilerden, sayılar/etiketler/yasaklı kelimeler seçili kanalın ayarlarından (kanal.json) gelir.
Aşama 4'te TR/hedef dil paragraf uzunluğu, replik ve sayı karşılaştırması yapılmaz (iki dilde doğal olarak farklıdır).
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from . import kanal
from . import metin as M


@dataclass
class Sonuc:
    hatalar: list[str] = field(default_factory=list)
    uyarilar: list[str] = field(default_factory=list)
    bilgiler: list[str] = field(default_factory=list)
    ek: dict = field(default_factory=dict)  # sonraki adımlara taşınan bilgi (ör. maskot argümanları)

    @property
    def temiz(self) -> bool:
        return not self.hatalar

    def sozluk(self) -> dict:
        return {"hatalar": self.hatalar, "uyarilar": self.uyarilar, "bilgiler": self.bilgiler, "ek": self.ek}




def eksik_dosyalar(dosyalar: dict[str, str], beklenen: list[str]) -> list[str]:
    return [f"{ad} dosyası eksik ya da boş" for ad in beklenen if not dosyalar.get(ad, "").strip()]


def konu_karti(kart: str) -> Sonuc:
    s = Sonuc()
    n = len(kart.strip())
    s.bilgiler.append(f"Kart {n} karakter")
    sinir = int(kanal.ayar()["uzunluk"]["kart_karakter"])
    if n > sinir:
        s.hatalar.append(f"Konu kartı {n} karakter; sınır {sinir:,}. En uzun alanları kısalt.".replace(",", "."))
    if "KONU KARTI" not in kart:
        s.hatalar.append(f"Kart 'KONU KARTI · {kanal.onek()}-0X' başlığıyla başlamıyor.")
    return s


def senaryo_tr(tr: str) -> Sonuc:
    s = Sonuc()
    sen = M.ayir(tr)
    k = M.kelime_sayisi(sen.paragraflar)
    s.bilgiler.append(f"Kelime {k} · Paragraf {len(sen.paragraflar)}")
    a, b = kanal.ayar()["uzunluk"]["calisma_kelime"]
    if not a <= k <= b:
        s.hatalar.append(f"Türkçe metin {k} kelime; hedef {_s(a)}–{_s(b)} (etiketler hariç).")
    etiketsiz = [i for i, p in enumerate(sen.paragraflar, 1) if not M.ETIKET.match(p)]
    if etiketsiz:
        s.uyarilar.append("Etiketsiz paragraf: " + ", ".join(f"¶{i}" for i in etiketsiz[:10]))
    _senaryo_etiketleri(tr, s)
    return s


def _s(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def senaryo_etiketleri() -> set[str]:
    return set(kanal.ayar()["etiketler"]["senaryo"].values())


def _etiket_metni() -> str:
    return " ".join(f"[{x}]" for x in kanal.ayar()["etiketler"]["senaryo"].values())


def _senaryo_etiketleri(metin: str, s: Sonuc) -> None:
    """Senaryoda geçerli etiketler yalnız kanal ayarındaki dört etiket."""
    gecerli, yabanci = senaryo_etiketleri(), []
    for i, p in enumerate(M.ayir(metin).paragraflar, 1):
        for t in re.findall(r"\[([^\]\n]{1,60})\]", p):
            if t.strip() not in gecerli:
                yabanci.append(f"¶{i} [{t}]")
    if yabanci:
        s.uyarilar.append(f"Geçersiz etiket (yalnız {_etiket_metni()}): " + ", ".join(yabanci[:10]))


# Hazır metin: karşılaştırmada yazım biçimi farkı sayılmayan işaretler (kıvrık/düz tırnak, üç nokta).
_HAZIR_ESDEGER = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "«": '"', "»": '"', "…": "..."})
HAZIR_UZUN_PARAGRAF = 90  # kelime; yalnız uyarı


def _hazir_kelimeler(metin: str) -> list[str]:
    return " ".join(M.govde(p) for p in M.ayir(metin).paragraflar).translate(_HAZIR_ESDEGER).split()


def hazir_metin(orijinal: str, metin: str, dil: str) -> Sonuc:
    """Kullanıcının hazır metni: model yalnız paragraf araları ve etiketler ekleyebilir. Etiketler ve teslim
    satırları çıkarılınca kelimeler aynen aynı olmalı (hata). Kelime aralığı ve etiket notları uyarıdır."""
    s = Sonuc()
    a, b = _hazir_kelimeler(orijinal), _hazir_kelimeler(metin)
    sen = M.ayir(metin)
    s.bilgiler.append(f"Kelime {M.kelime_sayisi(sen.paragraflar)} · Paragraf {len(sen.paragraflar)}")
    if a != b:
        farklar = []
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
            if op == "equal":
                continue
            once = " ".join(a[max(0, i1 - 4):i1])
            farklar.append(f"“…{once} [{' '.join(a[i1:i2]) or '—'}]” yerine “[{' '.join(b[j1:j2]) or '—'}]”")
            if len(farklar) == 3:
                break
        s.hatalar.append("Metin değişmiş: etiketler çıkarılınca kullanıcının metniyle kelimesi kelimesine aynı "
                         "olmalı. Yalnız paragraf araları ve etiketler eklenebilir. Farklar: " + "; ".join(farklar))
    k = M.kelime_sayisi(sen.paragraflar)
    u = kanal.ayar()["uzunluk"]
    alt, ust = u["calisma_kelime"] if dil == "tr" else u["hedef_kelime"]
    if not alt <= k <= ust:
        s.uyarilar.append(f"Metin {k} kelime; bu dilde hedef {_s(alt)}–{_s(ust)} (hazır metin olduğu için yalnız bilgi).")
    etiketsiz = [i for i, p in enumerate(sen.paragraflar, 1) if not M.ETIKET.match(p)]
    if etiketsiz:
        s.uyarilar.append("Etiketsiz paragraf: " + ", ".join(f"¶{i}" for i in etiketsiz[:10]))
    uzun = [i for i, p in enumerate(sen.paragraflar, 1) if M.kelime_sayisi([p]) > HAZIR_UZUN_PARAGRAF]
    if uzun:
        s.uyarilar.append(f"{HAZIR_UZUN_PARAGRAF} kelimeden uzun paragraf (tek sahne için uzun olabilir): " +
                          ", ".join(f"¶{i}" for i in uzun[:10]))
    _senaryo_etiketleri(metin, s)
    return s


def hazir_kuyruk(metin: str, dil: str) -> str:
    """Hazır metnin teslim satırı (modelin yazdığı değil, kodun saydığı)."""
    sen = M.ayir(metin)
    k, n = M.kelime_sayisi(sen.paragraflar), len(sen.paragraflar)
    sen.kuyruk = (f"Kelime: {k}" if dil == "tr" else f"Parole: {k} · Paragrafi: {n}" if dil == "it"
                  else f"Words: {k} · Paragraphs: {n}")
    return sen.metin()


def senaryo_it(tr: str, it: str) -> Sonuc:
    """Hedef dil final (Aşama 4): kelime aralığı, paragraf sayısı TR ile aynı, hook ≥ eşik, teslim satırları
    (kanal ayarından). Ayrıca çift paragraf. TR/hedef dil uzunluk, replik ve sayı karşılaştırması yapılmaz."""
    s = Sonuc()
    T, I = M.ayir(tr), M.ayir(it)
    k = M.kelime_sayisi(I.paragraflar)
    dk, dil = kanal.hedef_dil().upper(), kanal.dil_adi()
    s.bilgiler.append(f"Kelime {k} · Paragraf {dk} {len(I.paragraflar)} / TR {len(T.paragraflar)}")
    a, b = kanal.ayar()["uzunluk"]["hedef_kelime"]
    if not a <= k <= b:
        s.hatalar.append(f"{dil} metin {k} kelime; hedef {_s(a)}–{_s(b)} (etiketler hariç).")
    if len(T.paragraflar) != len(I.paragraflar):
        s.hatalar.append(f"Paragraf sayısı farklı: TR {len(T.paragraflar)}, {dk} {len(I.paragraflar)}. "
                         f"Her TR paragrafının tek bir {dk} karşılığı olmalı.")
    govdeler = [M.govde(p) for p in I.paragraflar]
    for i in range(len(govdeler)):
        for j in range(i + 1, min(len(govdeler), i + 8)):
            if difflib.SequenceMatcher(None, govdeler[i], govdeler[j]).ratio() > 0.8:
                s.hatalar.append(f"¶{i + 1} ve ¶{j + 1} neredeyse aynı (çift paragraf). "
                                 f"TR ¶{j + 1}'in karşılığı eksik olabilir.")
    if not M.KELIME_SATIRI.search(I.kuyruk):
        s.hatalar.append("Teslim satırları (kelime ve paragraf sayısı, Hook puanı, Bilgi kazancı …) eksik.")
    esik = float(kanal.ayar()["uzunluk"]["hook_esigi"])
    m = re.search(r"Hook puan\w*\s*:\s*(\d+(?:[.,]\d+)?)\s*/\s*10", I.kuyruk)
    if m and float(m.group(1).replace(",", ".")) < esik:
        s.hatalar.append(f"Hook puanı {m.group(1)}/10; en az {esik:g} olmalı.")
    _senaryo_etiketleri(it, s)
    return s


# Eski sistemin iç işaretleri ([SOURCE NEEDED], [SAFETY REVIEW NEEDED]). Artık kullanılmıyor; model eski beceri
# kopyasından ya da önceki aşama metninden taşırsa dosyaya yazılmadan önce mekanik olarak çıkarılır
# (yerlerini "Açık noktalar" satırı tutar). Metnin geri kalanına dokunulmaz.
IC_ISARET = re.compile(r"[ \t]*\[(?:SOURCE NEEDED|SAFETY REVIEW NEEDED)\]")


def ic_isaretleri_temizle(metin: str) -> tuple[str, int]:
    yeni, n = IC_ISARET.subn("", metin)
    return (re.sub(r"[ \t]+\n", "\n", yeni) if n else metin), n


def izinli_tag() -> set[str]:
    return {t.strip().lower() for t in kanal.ayar()["etiketler"]["ses"]}


def tag_sinirlari() -> dict[str, int]:
    return {t.strip().lower(): int(n) for t, n in kanal.ayar()["etiketler"].get("ses_sinir", {}).items()}


def izinli_tag_metni() -> str:
    sinir = tag_sinirlari()
    m = " ".join(f"[{t}]" for t in sorted(izinli_tag()) if t not in sinir)
    return m + "".join(f" ve en fazla {n} [{t}]" for t, n in sinir.items())


def elevenlabs_metni(metin: str) -> list[str]:
    """Seslendirmeye giden metinde yalnız kanal ayarındaki ses tag'leri (sınırlarıyla) olabilir. Başka her köşeli
    not (ör. [SOURCE NEEDED], büyük harfli notlar) seslendirmeyi başlatmadan durdurur."""
    izinli, sinir = izinli_tag(), tag_sinirlari()
    sorun, say = [], {}
    for i, p in enumerate(bloklar(metin), 1):
        for t in re.findall(r"\[([^\]\n]*)\]", p):
            t_ = t.strip().lower()
            if t_ not in izinli:
                sorun.append(f"sahne {i}: [{t}]")
            else:
                say[t_] = say.get(t_, 0) + 1
    for t, n in sinir.items():
        if say.get(t, 0) > n:
            sorun.append(f"[{t}] {say[t]} kez (en fazla {n})")
    return sorun


def duzeltme_mesaji(onay_no: int | None, sonuc: Sonuc) -> str:
    satirlar = "\n".join(f"- {h}" for h in sonuc.hatalar)
    return (f"{duzeltme_basligi(onay_no)} (uygulamanın otomatik kontrolü):\n{satirlar}\n"
            "Yalnızca değişen kısımları <yama> ile ver; dosyayı baştan yazma.")


# --- Aşama 5: sahne paketi --------------------------------------------------------

_YAS = re.compile(r"\b\d+[- ]?(year|yr)s?[- ]old\b", re.I)


def _yasak_deseni() -> re.Pattern | None:
    y = [x for x in kanal.ayar()["gorsel"]["yasakli"] if x.strip()]
    return re.compile(r"\b(" + "|".join(re.escape(x) for x in sorted(y, key=len, reverse=True)) + r")\b", re.I) if y else None


def izinli_olumsuz() -> tuple[str, ...]:
    return tuple(x.strip().lower() for x in kanal.ayar()["gorsel"]["izinli_olumsuz"] if x.strip())


def bloklar(metin: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", metin.replace("\r\n", "\n").strip()) if b.strip()]


def tsv_satirlari(tsv: str) -> list[str]:
    return [s for s in tsv.replace("\r\n", "\n").split("\n") if s.strip()]


def _flow_guvenligi(adlar_metinler: list[tuple[str, str]]) -> list[str]:
    hatalar, yasak, izinli = [], _yasak_deseni(), izinli_olumsuz()
    for yer, p in adlar_metinler:
        bulunan = sorted({m.lower() for m in yasak.findall(p)}) if yasak else []
        if bulunan:
            hatalar.append(f"{yer}: yasaklı kelime {', '.join(bulunan)}")
        if _YAS.search(p):
            hatalar.append(f"{yer}: yaş ifadesi var")
        for m in re.finditer(r"\bno\s+([a-z]+(?:\s[a-z]+)?)", p, re.I):
            if not izinli or not m.group(1).lower().startswith(izinli):
                hatalar.append(f"{yer}: izinsiz olumsuzlama «{m.group(0)}»")
        for m in re.finditer(r"\b(nothing|without|never)\b", p, re.I):
            hatalar.append(f"{yer}: izinsiz olumsuzlama «{m.group(0)}»")
    return list(dict.fromkeys(hatalar))


def sahne_paketi(a: str, b: str, c: str, d: str, it_final: str) -> Sonuc:
    """Sahne becerisi Adım 6 (plan_kontrol ayrıca çalışır). Kurallar kanal ayarından."""
    s = Sonuc()
    pa, pb, rows = bloklar(a), bloklar(b), tsv_satirlari(d)
    s.bilgiler.append(f"Sahne {len(pa)} · Prompt {len(pb)} · Plan satırı {max(0, len(rows) - 1)}")
    if not (len(pa) == len(pb) == len(rows) - 1):
        s.hatalar.append(f"Sayılar eşit değil: A {len(pa)} paragraf, B {len(pb)} prompt, D {len(rows) - 1} satır (başlık hariç).")
    beklenen_baslik = "sahne\tbolum\trol\tduygu\thareket\todak\tefekt\tsonraki_gecis\tmaskot\tgerekce"
    if rows and rows[0].strip() != beklenen_baslik:
        s.hatalar.append("D başlık satırı beklenen sütunlarla aynı değil: " + beklenen_baslik.replace("\t", " · "))
    # Tag kuralları
    izinli, sinir, say = izinli_tag(), tag_sinirlari(), {}
    tagli, onceki = 0, None
    for i, p in enumerate(pa, 1):
        taglar = re.findall(r"\[([^\]]+)\]", p)
        if taglar:
            tagli += 1
            for t in taglar:
                if t.strip().lower() not in izinli:
                    s.hatalar.append(f"A ¶{i}: izinsiz tag [{t}]")
            if len(taglar) > 1:
                s.hatalar.append(f"A ¶{i}: paragrafta birden fazla tag")
            if not p.startswith("["):
                s.hatalar.append(f"A ¶{i}: tag paragrafın başında değil")
            for t in taglar:
                say[t.strip().lower()] = say.get(t.strip().lower(), 0) + 1
            if onceki == taglar[0] and i < len(pa):
                s.uyarilar.append(f"A ¶{i}: aynı tag art arda ([{taglar[0]}])")
            onceki = taglar[0]
        else:
            onceki = None
    oran = 100 * tagli / max(1, len(pa))
    s.bilgiler.append(f"Tag %{oran:.1f}")
    ust = float(kanal.ayar()["etiketler"]["tag_orani"])
    if oran > ust:
        s.hatalar.append(f"Tag'li paragraf oranı %{oran:.1f}; üst sınır %{ust:g}.")
    for t, n in sinir.items():
        if say.get(t, 0) > n:
            s.hatalar.append(f"[{t}] {say[t]} kez; en fazla {n}.")
    if re.search(r"<\s*break|<\s*speak|<\s*prosody", a, re.I):
        s.hatalar.append("A'da <break>/SSML var; duraklama noktalamayla yapılmalı.")
    if re.search(r"\[(" + "|".join(re.escape(x) for x in senaryo_etiketleri()) + r")\]", a):
        s.hatalar.append(f"A'da senaryo etiketi kalmış ({_etiket_metni()}).")
    # Metin birebir
    ga = M.govde(" ".join(pa)).split()
    gi = M.govde(" ".join(M.ayir(it_final).paragraflar)).split()
    if ga != gi:
        fark = next((i for i, (x, y) in enumerate(zip(ga, gi)) if x != y), min(len(ga), len(gi)))
        s.hatalar.append(f"A metni (tag'siz) final metinle birebir değil: {fark + 1}. kelimede ayrılıyor "
                         f"(A: «{' '.join(ga[fark:fark + 6])}» / final: «{' '.join(gi[fark:fark + 6])}»).")
    # Flow güvenliği (B ve C)
    s.hatalar += _flow_guvenligi([(f"B {i:04d}", p) for i, p in enumerate(pb, 1)])
    s.hatalar += _flow_guvenligi([(f"C satır {i}", l) for i, l in enumerate(c.splitlines(), 1) if "→" in l])
    kar = kanal.ayar()["gorsel"]["karakter"]
    if kar:
        yanlis = [i for i, p in enumerate(pb, 1) if kar in p and not p.startswith(kar)]
        if yanlis:
            s.uyarilar.append(f"B: {kar} promptun başında değil: " + ", ".join(f"{i:04d}" for i in yanlis[:10]))
    return s


def paket(paket_md: str) -> Sonuc:
    s = Sonuc()
    if "DEFTER KAYDI" not in paket_md:
        s.hatalar.append("Paket dosyasında '5. DEFTER KAYDI' bloğu yok.")
    # Hashtag satırı: en çok etiket içeren satır (renk kodları #F7F0E1 sayılmaz).
    etiketler = lambda l: [t for t in re.findall(r"(?<!\w)#\w+", l) if not re.fullmatch(r"#[0-9A-Fa-f]{6}", t)]
    etiket_satiri = max(paket_md.splitlines() or [""], key=lambda l: len(etiketler(l)))
    n = len(etiketler(etiket_satiri))
    if n and n != 5:
        s.uyarilar.append(f"Hashtag sayısı {n}; tam 5 olmalı.")
    _kanal_etiketi(paket_md, s)
    return s


def _kanal_etiketi(metin: str, s: Sonuc) -> None:
    etiket = "#" + re.sub(r"\W", "", kanal.ayar()["ad"])
    if len(etiket) > 1 and etiket.lower() not in metin.lower():
        s.uyarilar.append(f"{etiket} etiketi bulunamadı.")


def duzeltme_basligi(onay_no: int | None) -> str:
    return f"ONAY {onay_no} değil, düzeltme" if onay_no else "Düzeltme"


def aciklama_final(final_md: str, zamanlar: list[str]) -> Sonuc:
    """Aşama 6 Mesaj 2: verilen zaman damgaları aynen ve sırayla yer almalı (değiştirilmez, yuvarlanmaz)."""
    s = Sonuc()
    bulunan = re.findall(r"(?m)^\W*(\d{1,2}:\d{2})\b", final_md)
    s.bilgiler.append(f"Bölüm {len(bulunan)}")
    if zamanlar and bulunan != zamanlar:
        s.hatalar.append("Bölüm zaman damgaları verilenlerle birebir ve aynı sırada değil. Beklenen: "
                         + ", ".join(zamanlar) + " · Bulunan: " + (", ".join(bulunan) or "yok"))
    if zamanlar and zamanlar[0] != "0:00":
        s.uyarilar.append("İlk bölüm 0:00'da başlamıyor (YouTube şartı).")
    if 0 < len(zamanlar) < 3:
        s.uyarilar.append("3'ten az bölüm var (YouTube en az 3 ister).")
    sn = [int(z.split(":")[0]) * 60 + int(z.split(":")[1]) for z in zamanlar]
    kisa = [zamanlar[i] for i in range(len(sn) - 1) if sn[i + 1] - sn[i] < 10]
    if kisa:
        s.uyarilar.append("10 saniyeden kısa bölüm: " + ", ".join(kisa))
    _kanal_etiketi(final_md, s)
    return s
