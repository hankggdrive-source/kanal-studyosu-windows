"""Denge testleri için ortak yardımcılar: Örnek ayarlı geçici kanal ve sahte Anthropic istemcisi."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

VERI = Path(__file__).parent / "veri"


def gecici_ortam(test) -> Path:
    """Kurulum klasörünü geçici dizine kurar ve içinde Örnek ayarlı bir kanal açar (öneki ORN-VID; test verisi
    ORN-VID-05 adlarıyla aynen kullanılabilsin). Döner: kanal klasörü (Kanallar/ornek)."""
    import os
    from kanal_studyosu import ayarlar as A
    from kanal_studyosu import kanallar, yollar

    kok = Path(tempfile.mkdtemp(prefix="kanal_parite_"))
    test.addCleanup(shutil.rmtree, kok, True)
    eski = {k: os.environ.get(k) for k in ("KANAL_STUDYOSU_KOK", "KANAL_STUDYOSU_COP")}
    os.environ.update(KANAL_STUDYOSU_KOK=str(kok / "Kurulum"), KANAL_STUDYOSU_COP=str(kok / "Cop"))

    def geri():
        for k, v in eski.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    test.addCleanup(geri)
    yollar.kur()
    (kok / "CapCut").mkdir()
    A.ayar_kaydet({"yollar": {"capcut_taslak": str(kok / "CapCut")}})
    on = json.loads((VERI / "ornek_kanal.json").read_text(encoding="utf-8"))
    on.update(ad="Örnek", kisaltma="ornek", kod_oneki="ORN-VID", test=False)
    on["uzunluk"]["kelime_otomatik"] = False  # gerçek Örnek kanalı gibi: kelime aralıkları elle girilmiş
    kanallar.ekle(on)
    r = kanallar.klasor("ornek")
    proje = r / "Proje_dosyalari"
    (proje / "00_Yonetici.md").write_text("# ORN_00 · YÖNETİCİ\nDüzen.\n", encoding="utf-8")
    (proje / "01_Anayasa.md").write_text("# ORN_01 · ANAYASA\nKurallar.\n", encoding="utf-8")
    shutil.copy(VERI / "ORN_02_Kanal_Defteri_CURRENT.md", proje / "02_Defter.md")
    (proje / "03_Aktif_Video.md").write_text("# ORN_03 · AKTİF VİDEO\nDurum: ORN-VID-05 aktif.\n", encoding="utf-8")
    for b in ("konu", "arastirma", "senaryo", "ceviri", "sahne", "paketleme"):
        (r / "Beceriler" / b / "SKILL.md").write_text(f"# {b}\nBeceri metni.\n", encoding="utf-8")
    for n in range(1, 6):
        (r / "Videolar" / f"ORN-VID-0{n}").mkdir(parents=True)
    return r


def araclari_kopyala(r: Path) -> None:
    """Örnek'de testler Araclar betiklerini kanal klasörüne kopyalardı; Kanal Stüdyosu'nda araçlar uygulamanın
    içindedir (araclar/), kopyalamaya gerek yoktur."""


# --- Sahte Anthropic istemcisi ------------------------------------------------

class _Blok(SimpleNamespace):
    def model_dump(self, **_):
        return {k: v for k, v in vars(self).items() if v is not None}


def mesaj(metin: str, model="claude-sonnet-5-5", durma="end_turn", giris=1000, cikis=500, onbellek_okuma=0,
          arama=0, model_sunulan=None):
    return SimpleNamespace(
        content=[_Blok(type="thinking", thinking="", signature="imza"), _Blok(type="text", text=metin)],
        usage=SimpleNamespace(input_tokens=giris, output_tokens=cikis, cache_creation_input_tokens=0,
                              cache_read_input_tokens=onbellek_okuma,
                              server_tool_use=SimpleNamespace(web_search_requests=arama), iterations=None),
        stop_reason=durma, model=model_sunulan or model)


class _Akis:
    def __init__(self, son):
        self.son = son

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        for b in self.son.content:
            if b.type == "text":
                yield SimpleNamespace(type="content_block_delta", delta=SimpleNamespace(type="text_delta", text=b.text))

    def get_final_message(self):
        return self.son


class SahteIstemci:
    """cevaplar: sırayla döndürülecek mesajlar. Her istek parametreleriyle `istekler`e eklenir."""

    def __init__(self, cevaplar):
        self.cevaplar = list(cevaplar)
        self.istekler = []
        ust = self

        class Mesajlar:
            def stream(self, **p):
                ust.istekler.append(json.loads(json.dumps(p, default=str)))
                c = ust.cevaplar.pop(0)
                return _Akis(c(p) if callable(c) else c)  # cevap isteğe göre de üretilebilir

            def count_tokens(self, **p):
                return SimpleNamespace(input_tokens=2000)

        self.beta = SimpleNamespace(messages=Mesajlar())
        self.models = SimpleNamespace(list=lambda **k: [])
