"""Aşama tanımları ve modele giden mesajların kurulması.

Sistem öneki (önbellekli, bir video boyunca sabit): proje dosyaları 00 + 01 + 02 → aşama becerisi (içerik
değiştirilmeden) → uygulama çerçevesi notu + KANAL AYARLARI (kanal.json'dan).
Kullanıcı mesajı (değişken): beceriyi tetikleyen kısa Türkçe mesaj + onaylı girdiler.
Hedef dil Türkçe olan kanalda 4. aşama yoktur; Türkçe senaryo finaldir.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from . import araclar
from . import ayarlar as A
from . import kanal
from . import kontroller as K

CERCEVE = """# UYGULAMA ÇERÇEVESİ (Kanal Stüdyosu)
Bu konuşma Kanal Stüdyosu uygulamasında, API üzerinden yürüyor. Yukarıdaki proje dosyaları (00–02) ve aşama becerisi aynen geçerlidir. Yalnızca şu teknik farklar vardır:
1. Ajan yok. Uygulama dosyaları otomatik kaydeder, kontrolleri kod yapar, onayları kullanıcı uygulama ekranında verir. Kullanıcı mesajlarını uygulama iletir.
2. Dosya aracı yok. Her çıktı dosyasını tam adıyla şu biçimde ver: <dosya ad="DOSYA_ADI">tam içerik</dosya>. İçeriği kod bloğuna sarma.
3. Sohbet cevabını (özet, kontrol satırları, durum kartı) <ozet>…</ozet> içinde ver. Dosya içeriğini özette tekrar etme.
4. Düzeltme turunda dosyayı baştan yazma; yalnız değişen kısımları yama olarak ver. Numaralar yamadan önceki dosyaya göredir:
   <yama dosya="AD" paragraf="12">paragrafın yeni hali, etiketleriyle</yama>
   <yama dosya="AD" paragraf="12" islem="sil"></yama>
   <yama dosya="AD" paragraf="12" islem="sonrasina_ekle">eklenecek paragraf(lar)</yama>
   <yama dosya="AD" satir="Başlık">satırın yeni tam hali (bu metinle başlayan ilk satırın yerine geçer; montaj planında satir="0023")</yama>
   <yama dosya="AD" bolum="§4">bölümün yeni tam hali</yama>
   <yama dosya="AD" kuyruk="1">teslim satırlarının yeni hali (kelime/paragraf satırları değiştiyse)</yama>
   Değişiklik çok kapsamlıysa dosyanın tamamını <dosya> ile yeniden verebilirsin.
5. Becerideki "Model: …" satırı bilgi içindir; modeli uygulama seçer.
6. Web arama aracı açıksa onu kullan; değilse bilgini kullan. Sayı uydurma. Doğrulanacak iddiaları ve hassas bölümleri metnin içinde işaretleme; sohbet cevabının sonunda düz yazı tek satır ver: "Açık noktalar: ¶N … " (paragraf numarasıyla; yoksa "Açık noktalar: yok").
7. Konuşma her aşamada yenidir. Önceki aşamaların onaylı çıktıları mesajda <belge ad="…"> olarak verilir; 03_Aktif_Video.md de güncel hâliyle mesajdadır. Becerilerde başka adlarla anılan proje dosyaları (ör. ORN_00, ORN_01, ORN_02, ORN_03) sırasıyla 00_Yonetici.md, 01_Anayasa.md, 02_Defter.md ve 03_Aktif_Video.md'dir; beceri adları (ör. ornek-arastirma) da bu uygulamadaki aşamalardır.
8. Metinde geçerli etiketler yalnız {senaryo}. Seslendirme metninde yalnız {ses}."""


def cerceve() -> str:
    e = kanal.ayar()["etiketler"]
    sinir = e.get("ses_sinir", {})
    ses = " ".join(f"[{t}]" for t in e["ses"] if t not in sinir)
    ses += "".join(f" ve en fazla {n} [{t}]" for t, n in sinir.items())
    return CERCEVE.format(senaryo=" ".join(f"[{x}]" for x in e["senaryo"].values()), ses=ses.strip()) \
        + "\n\n" + kanal.ayarlar_blogu()


def ifade_notu() -> str:
    return (kanal.ayar()["gorsel"].get("ifade_notu") or "").strip()


def belge(ad: str, icerik: str) -> str:
    return f'<belge ad="{ad}">\n{icerik.strip()}\n</belge>'


@dataclass(frozen=True)
class Asama:
    kimlik: str               # "A1"
    no: int                   # 1..6
    ad: str                   # ekranda görünen
    beceri: str               # Beceriler/<beceri>/SKILL.md
    onay: int | None          # ONAY numarası (yoksa None)
    cikti_sonekleri: tuple    # dosya adı sonekleri: "_1_konu_karti.md" … ({dil} = hedef dil kodu)

    def ciktilar(self, kod: str) -> list[str]:
        return [kod + s.replace("{dil}", kanal.hedef_dil()) for s in self.cikti_sonekleri]


ASAMALAR = {
    "A1": Asama("A1", 1, "Konu", "konu", 1, ("_1_konu_karti.md", "_1_defter_degisiklikleri.md")),
    "A2": Asama("A2", 2, "Araştırma", "arastirma", 2, ("_2_arastirma_outline.md",)),
    "A3": Asama("A3", 3, "Senaryo TR", "senaryo", 3, ("_3_senaryo_tr.md",)),
    "A4": Asama("A4", 4, "Hedef dil", "ceviri", 4, ("_4_senaryo_{dil}.md",)),
    # Aşama 5'te ONAY yok: kontroller temizse kendiliğinden Aşama 6'ya geçilir.
    "A5": Asama("A5", 5, "Sahne paketi", "sahne", None,
                ("_5A_elevenlabs.txt", "_5B_gorsel_promptlari.txt", "_5C_veo3.md", "_5D_montaj_plani.tsv")),
    "A6": Asama("A6", 6, "Paketleme", "paketleme", 5, ("_6_paket.md",)),
    # Montaj sonrası Mesaj 2: ONAY yok; kod zaman damgalarını doğrular.
    "A6_2": Asama("A6_2", 6, "Bölümler", "paketleme", None, ("_6_aciklama_final.md",)),
}
# Hazır metinle başlayan üretimin ilk aşaması (1. aşamanın yerine): konu kartı + Defter çakışma kontrolü +
# metni sahne paragraflarına bölme + paragraf etiketleri. Metnin kendisi değişmez (kod denetler).
# HT: metin Türkçe (3. aşamanın dosyası olur) · HI: metin hedef dilde (4. aşamanın dosyası olur, sonra 5).
ASAMALAR["HT"] = Asama("HT", 1, "Hazır metin", "konu", 1,
                       ("_1_konu_karti.md", "_1_defter_degisiklikleri.md", "_3_senaryo_tr.md"))
ASAMALAR["HI"] = Asama("HI", 1, "Hazır metin", "konu", 1,
                       ("_1_konu_karti.md", "_1_defter_degisiklikleri.md", "_4_senaryo_{dil}.md"))
HAZIR = ("HT", "HI")
HAZIR_ORIJINAL = "_0_hazir_metin.txt"  # kullanıcının verdiği metin, aynen (arşivde)

TUM_SIRA = ["A1", "A2", "A3", "A4", "A5", "A6", "FLOW", "STUDIO", "CAPCUT", "A6_2", "SON", "KAPANIS"]
SON_ADIM = "BITTI"
# Kanal ayarındaki onay anahtarı (Onaylar ekranı). Yalnız ONAY 2, 4 ve 5 kapatılabilir; ONAY 1 ve 3 her zaman.
ONAY_ANAHTARI = {"A1": "konu", "A2": "arastirma", "A3": "senaryo", "A4": "ceviri", "A6": "paketleme"}
ONAY_SECILEBILIR = ("A2", "A4", "A6")


def hazir_dil(kimlik: str) -> str:
    return "tr" if kimlik == "HT" else kanal.hedef_dil()


def hazir_diller() -> dict[str, str]:
    """Hazır metnin seçilebilecek dilleri: Türkçe ve kanalın hedef dili (hedef dil Türkçe ise tek seçenek)."""
    d = {"tr": "Türkçe"}
    d[kanal.hedef_dil()] = kanal.dil_adi()
    return d


def sira(d: dict | None = None) -> list[str]:
    """Üretimin adımları: hedef dil Türkçe ise A4 yoktur; hazır metinle başlayan üretimde durum.json → sira."""
    if d and d.get("sira"):
        return d["sira"]
    return [x for x in TUM_SIRA if x != "A4" or kanal.ceviri_var()]


def gorunum_sirasi(d: dict | None = None) -> list[str]:
    return (d or {}).get("gorunum") or sira(d)


def hazir_sira(dil: str) -> tuple[list[str], list[str], list[str]]:
    """Hazır metinli üretim → (çalışma sırası, ekrandaki sıra, atlanan aşamalar)."""
    normal = sira()
    if dil == "tr":
        ilk, atlanan = "HT", ["A2", "A3"]
    else:
        ilk, atlanan = "HI", ["A2", "A3", "A4"]
    atlanan = [k for k in atlanan if k in normal]
    kalan = [k for k in normal if k != "A1" and k not in atlanan]
    return [ilk] + kalan, [ilk] + atlanan + kalan, atlanan


def adim_adlari() -> dict[str, str]:
    return {"A1": "1 · Konu", "A2": "2 · Araştırma", "A3": "3 · Senaryo TR", "A4": f"4 · {kanal.dil_adi()}",
            "A5": "5 · Sahne paketi", "A6": "6 · Paketleme", "FLOW": "Görseller (Flow)", "STUDIO": "Ses ve video",
            "CAPCUT": "CapCut", "A6_2": "Bölümler", "SON": "Son kontrol", "KAPANIS": "Kapanış",
            "HT": "1 · Hazır metin (Türkçe)", "HI": f"1 · Hazır metin ({kanal.dil_adi()})"}


def onay_varsayilan() -> dict:
    o = kanal.ayar()["onaylar"]
    return {k: bool(o.get(ONAY_ANAHTARI[k], True)) for k in ONAY_SECILEBILIR}


def onay_gerekli(asama: Asama, d: dict | None = None) -> bool:
    """ONAY'lı aşama onay bekler mi: ONAY 2/4/5 için önce bu üretimin seçimi, yoksa kanal ayarı; diğerleri her zaman."""
    if asama.onay is None:
        return False
    if asama.kimlik in ONAY_SECILEBILIR:
        secim = (d or {}).get("onaylar") or {}
        if asama.kimlik in secim:
            return bool(secim[asama.kimlik])
        return onay_varsayilan()[asama.kimlik]
    return True


HAZIR_GOREV = """# AŞAMA: HAZIR METİN
Kullanıcı bu videonun metnini hazır verdi. Konu seçimi, araştırma ve senaryo yazımı (metin hedef dildeyse hedef dilde yeniden yazım da) yapılmıyor. Yukarıdaki iki beceri yalnız BİÇİM ve KURAL kaynağıdır: konu kartının biçimi ve Defter değişikliklerinin biçimi `konu` becerisinden, sahne paragrafları ve etiketlerin anlamı `senaryo` becerisinden. O becerilerdeki diğer adımları (Studio verisi, konu seçme, web araştırması, yazım, öz denetim, çeviri, hook güçlendirme) uygulama.

Görevin dört iş:
1. Konu kartı: beceri biçiminde, kanal ayarlarındaki karakter sınırını aşmadan, "KONU KARTI · <KOD> · …" başlığıyla ve Başlık satırıyla. İçeriği yalnız verilen metinden çıkar.
2. Kanal Defteri kontrolü: konu, başlık, açılış ve kapanış 02_Defter.md'deki önceki videolarla çakışıyor mu, aynı kalıp tekrar ediyor mu. Sonucu <ozet> içinde "Çakışma kontrolü: …" satırıyla yaz (çakışma yoksa "yok"). Defter değişikliklerini beceri biçiminde ayrı dosyaya yaz.
3. Sahne paragrafları: metni sahne büyüklüğünde paragraflara böl; paragraflar arasında bir boş satır. Yalnız cümle sonlarından böl. Metin zaten paragraflara bölünmüşse uygun olanları koru.
4. Etiketler: her paragrafın başına senaryo becerisindeki anlamlarına göre, kanal ayarlarındaki senaryo etiketlerinden uygun olanı koy. Metinde zaten etiket varsa koru.

METNE DOKUNMA: tek kelime ekleme, silme, değiştirme, çevirme ya da yerini değiştirme; noktalamayı ve yazımı da koru. Yalnız paragraf araları ve etiketler eklenir. Uygulama, etiketler çıkarılınca metnin kullanıcınınkiyle kelimesi kelimesine aynı olduğunu denetler.
Metnin sonuna teslim satırı (kelime/paragraf/hook) yazma; uygulama ekler. Üç dosyayı da tam adlarıyla <dosya> içinde ver."""


def final_dosya(kod: str) -> str:
    """Seslendirilecek onaylı final metin: hedef dil senaryosu (A4) ya da hedef dil Türkçe ise Türkçe senaryo."""
    return ASAMALAR["A4"].ciktilar(kod)[0] if kanal.ceviri_var() else kod + "_3_senaryo_tr.md"


def sistem(asama: Asama) -> list[str]:
    ortak = "\n\n".join(f"# PROJE DOSYASI: {ad}\n\n{kanal.rit(ad)}" for ad in kanal.PROJE_DOSYALARI[:3])
    if asama.kimlik in HAZIR:
        referans = "\n\n".join(f"# REFERANS BECERİ (yalnız biçim ve kurallar için): {b}\n\n{kanal.beceri(b)}"
                               for b in ("konu", "senaryo"))
        return [ortak, referans, HAZIR_GOREV + "\n\n" + cerceve()]
    return [ortak, f"# AŞAMA BECERİSİ: {asama.beceri}\n\n{kanal.beceri(asama.beceri)}", cerceve()]


def _not(onay_notu: str) -> str:
    return f" Notlar: {onay_notu.strip()}" if onay_notu and onay_notu.strip() else ""


def ilk_mesaj(asama: Asama, kod: str, oku: Callable[[str], str], girdi: dict) -> str:
    """oku(dosya_adı) → arşivdeki onaylı çıktı; girdi: studio_verisi, konu_istegi, onay_notlari."""
    notlar = girdi.get("onay_notlari", {})
    aktif = lambda: belge(kanal.AKTIF, kanal.rit(kanal.AKTIF))
    if asama.kimlik in HAZIR:
        kart, defter_, metin_ = asama.ciktilar(kod)
        parcalar = [f"{kod} için hazır metin. Metnin dili: {kanal.dil_adi(hazir_dil(asama.kimlik))}. "
                    f"Dosyalar: `{kart}` (konu kartı), `{defter_}` (Defter değişiklikleri), `{metin_}` (sahne "
                    "paragraflarına bölünmüş ve etiketlenmiş metin)."]
        if (girdi.get("konu_istegi") or "").strip():
            parcalar.append("Kullanıcının notu:\n" + girdi["konu_istegi"].strip())
        parcalar.append(belge("hazir_metin.txt", oku(kod + HAZIR_ORIJINAL)))
        return "\n\n".join(parcalar)
    if asama.kimlik == "A1":
        parcalar = [f"{kod} için Aşama 1. `konu` becerisini kullan."]
        veri = (girdi.get("studio_verisi") or "").strip()
        parcalar.append("Önceki yayınlanmış videonun Studio verisi:\n" + veri if veri else "Studio verisi yok.")
        if (girdi.get("konu_istegi") or "").strip():
            parcalar.append("Kullanıcının konu isteği:\n" + girdi["konu_istegi"].strip())
        return "\n\n".join(parcalar)
    if asama.kimlik == "A2":
        return "\n\n".join([f"ONAY 1.{_not(notlar.get('A1'))} Aşama 2: `arastirma`.", aktif()])
    if asama.kimlik == "A3":
        outline = kod + "_2_arastirma_outline.md"
        return "\n\n".join([f"ONAY 2.{_not(notlar.get('A2'))} Aşama 3: `senaryo`.", aktif(), belge(outline, oku(outline))])
    if asama.kimlik == "A4":
        tr = kod + "_3_senaryo_tr.md"
        return "\n\n".join([f"ONAY 3.{_not(notlar.get('A3'))} Aşama 4: `ceviri` ({kanal.dil_adi()}).", aktif(),
                            belge(tr, oku(tr))])
    if asama.kimlik == "A5":
        onceki = "A4" if kanal.ceviri_var() else "A3"
        no = 4 if kanal.ceviri_var() else 3
        parcalar = [f"ONAY {no}.{_not(notlar.get(onceki))} {kod} Aşama 5: `sahne`. Final metin 03_Aktif_Video.md'de."]
        if ifade_notu():
            parcalar.append("Görsel promptları için ek not: " + ifade_notu())
        return "\n\n".join(parcalar + [aktif()])
    if asama.kimlik == "A6":
        return "\n\n".join([f"{kod} Aşama 6: `paketleme` (Mesaj 1).", aktif()])
    if asama.kimlik == "A6_2":
        zamanlar = "\n".join(f"{b['zaman']} · {b['bolum']} · {b['ilk_cumle']}" for b in girdi.get("bolumler", []))
        paket = kod + "_6_paket.md"
        return "\n\n".join([
            f"Montaj bitti. {kod} Aşama 6 Mesaj 2: bölümler ve nihai açıklama. Zamanlar kesin:\n{zamanlar}",
            f"ONAY 5 verilen paket aşağıda.{_not(notlar.get('A6'))}", belge(paket, oku(paket)), aktif()])
    raise KeyError(asama.kimlik)


def kontrol(asama: Asama, kod: str, oku: Callable[[str], str]) -> K.Sonuc:
    sonuc = K.Sonuc()
    dosyalar = {}
    for ad in asama.ciktilar(kod):
        try:
            dosyalar[ad] = oku(ad)
        except FileNotFoundError:
            dosyalar[ad] = ""
    sonuc.hatalar += K.eksik_dosyalar(dosyalar, asama.ciktilar(kod))
    if sonuc.hatalar:
        return sonuc
    if asama.kimlik == "A1":
        ek = K.konu_karti(dosyalar[kod + "_1_konu_karti.md"])
    elif asama.kimlik in HAZIR:
        ek = K.konu_karti(dosyalar[kod + "_1_konu_karti.md"])
        hm = K.hazir_metin(oku(kod + HAZIR_ORIJINAL), dosyalar[asama.ciktilar(kod)[2]], hazir_dil(asama.kimlik))
        ek.hatalar += hm.hatalar
        ek.uyarilar += hm.uyarilar
        ek.bilgiler += hm.bilgiler
    elif asama.kimlik == "A3":
        ek = K.senaryo_tr(dosyalar[kod + "_3_senaryo_tr.md"])
    elif asama.kimlik == "A4":
        ek = K.senaryo_it(oku(kod + "_3_senaryo_tr.md"), dosyalar[final_dosya(kod)])
    elif asama.kimlik == "A5":
        a, b, c, d = (dosyalar[x] for x in asama.ciktilar(kod))
        ek = K.sahne_paketi(a, b, c, d, oku(final_dosya(kod)))
        if not ek.hatalar:  # plan_kontrol yalnızca sayılar tutarlıyken anlamlı
            pk = araclar.plan_kontrol(str(kanal.arsiv_klasoru(kod) / (kod + "_5D_montaj_plani.tsv")),
                                      len(K.bloklar(a)))
            ek.bilgiler.append(f"KES %{pk['kes']}" if pk["kes"] else "plan_kontrol çalıştı")
            if pk["temiz"]:
                ek.bilgiler.append("plan_kontrol: TEMIZ")
                ek.ek = {"maskot": pk["maskot"]}
            else:
                ek.hatalar += [f"Montaj planı (plan_kontrol): {h}" for h in pk["hatalar"]]
    elif asama.kimlik == "A6":
        ek = K.paket(dosyalar[kod + "_6_paket.md"])
        _hassas(kod, ek)
    elif asama.kimlik == "A6_2":
        ek = K.aciklama_final(dosyalar[kod + "_6_aciklama_final.md"], girdi_zamanlari(kod))
        _hassas(kod, ek)
    else:
        ek = K.Sonuc()
    sonuc.hatalar += ek.hatalar
    sonuc.uyarilar += ek.uyarilar
    sonuc.bilgiler += ek.bilgiler
    sonuc.ek = ek.ek
    return sonuc


def girdi_zamanlari(kod: str) -> list[str]:
    """CapCut adımında kaydedilen bölüm zamanları (durum.json)."""
    d = A.json_oku(kanal.uygulama_klasoru(kod) / "durum.json", {}) or {}
    return [b["zaman"] for b in d.get("bolumler", [])]


def _hassas(kod: str, ek: K.Sonuc) -> None:
    """hassas kelime kontrolü: DEFTER KAYDI (iç not) ve ilk 30 sn bulguları uyarı, diğerleri hata."""
    hk = araclar.hassas_kelime(kod)
    ic = _defter_kaydi_satirlari(kanal.video_klasoru(kod) / "04_Paketleme_ve_Veo3.md")
    for h in hk["paketleme"]:
        m = re.match(r"paketleme satir (\d+)", h)
        if m and int(m.group(1)) in ic:  # kanal içi not, yayında görünmez
            ek.uyarilar.append(f"Hassas kelime DEFTER KAYDI'nda (iç not, yayında görünmez): {h}")
        else:
            ek.hatalar.append(f"Hassas kelime ({h})")
    ek.uyarilar += [f"İlk 30 sn hassas kelime ({h}); metin onaylı olduğu için yalnızca bilgi." for h in hk["metin"]]
    if hk["temiz"]:
        ek.bilgiler.append("hassas_kelime_kontrol: TEMIZ")


def _defter_kaydi_satirlari(yol) -> set[int]:
    """04 dosyasında DEFTER KAYDI bölümünün satır numaraları (1'den başlar)."""
    satirlar = yol.read_text(encoding="utf-8").splitlines()
    bas = next((i for i, l in enumerate(satirlar) if l.startswith("#") and "DEFTER KAYDI" in l), None)
    if bas is None:
        return set()
    son = next((j for j in range(bas + 1, len(satirlar)) if satirlar[j].startswith("#")), len(satirlar))
    return set(range(bas + 1, son + 1))


def sonuc_dosyalari(asama: Asama, kod: str, oku: Callable[[str], str]) -> dict[str, str]:
    """Aşama çıktısından Videolar/<kod>/ sonuç dosyaları (SKILL D Adım 4.2 ve 4.5).
    İçerik değişmez; yalnızca sondaki boşluk ve TSV'deki boş satırlar temizlenir."""
    if asama.kimlik == "A5":
        tsv = "\n".join(K.tsv_satirlari(oku(kod + "_5D_montaj_plani.tsv"))) + "\n"
        return {"02_ElevenLabs_seslendirme_metni.txt": oku(kod + "_5A_elevenlabs.txt").rstrip() + "\n",
                "03_Gorsel_promptlari.txt": oku(kod + "_5B_gorsel_promptlari.txt").rstrip() + "\n",
                "05_Montaj_plani.tsv": tsv}
    paket = (f"# {kod} · Paketleme ve Veo3\n\n{oku(kod + '_6_paket.md').strip()}\n\n"
             f"## Veo3 hareket promptları\n\n{oku(kod + '_5C_veo3.md').strip()}\n") if asama.kimlik in ("A6", "A6_2") else ""
    if asama.kimlik == "A6":
        return {"04_Paketleme_ve_Veo3.md": paket}
    if asama.kimlik == "A6_2":
        # SKILL 10c: nihai açıklama 04'ün en üstüne "## 0 · YAYIN PAKETİ" olarak eklenir.
        return {"04_Paketleme_ve_Veo3.md":
                "## 0 · YAYIN PAKETİ (montaj sonrası nihai açıklama — YouTube'a bunu yapıştır)\n\n"
                f"{oku(kod + '_6_aciklama_final.md').strip()}\n\n"
                "Başlık, kapak A/B (test edilen hipotez) ve sabit yorum: aşağıdaki paketin 1., 2. ve 4. bölümleri.\n\n"
                f"---\n\n{paket}"}
    return {}


# Arşivdeki alışılmış adlar (SKILL D Adım 4): ham aşama dosyasının bir kopyası.
ARSIV_KOPYALARI = {"A5": {"_5C_veo3.md": "veo3.md"}, "A6": {"_6_paket.md": "proje3_paketleme.md"},
                   "A6_2": {"_6_aciklama_final.md": "proje3_paket_final.md"}}


def rit03_kart_ile(kod: str, kart: str, tarih: str) -> str:
    return (f"# 03 · AKTİF VİDEO\nDurum: {kod} aktif. ONAY 1 verildi ({tarih}).\n\n"
            f"## ONAYLI KONU KARTI\n{kart.strip()}\n")


def rit03_final_ekle(rit03: str, kod: str, final: str, tarih: str) -> str:
    govde = rit03.split("\n## ONAYLI FİNAL METİN", 1)[0].rstrip()
    no = 4 if kanal.ceviri_var() else 3
    govde = govde.replace("ONAY 1 verildi", f"ONAY 1 ve ONAY {no} verildi", 1)
    return (f"{govde}\n\n## ONAYLI FİNAL METİN · {kanal.dil_adi()} (etiketli, teslim satırlarıyla; ONAY {no}: {tarih})\n"
            f"{final.strip()}\n")
