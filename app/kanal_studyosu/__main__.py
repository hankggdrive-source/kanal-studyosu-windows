"""Başlatma: python3 -m kanal_studyosu [--no-browser] [--port N]"""
from __future__ import annotations

import argparse
import atexit
import threading
import webbrowser

from . import ayarlar as A
from . import kanal_sablonu
from . import kayit
from . import sunucu
from . import tek_kopya
from . import yollar


def main() -> None:
    from .sistem_win import alt_surecleri_gizle
    alt_surecleri_gizle()
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--port", type=int, default=0)
    z = ap.parse_args()
    for k in yollar.kur():
        kayit.yaz(f"Klasör oluşturuldu: {k}")
    try:
        kanal_sablonu.sablon_dosyasi_yaz()
    except OSError as e:
        kayit.yaz(f"Yeni kanal şablonu yazılamadı: {e}", "uyari")
    acik = tek_kopya.calisan(yollar.calisan_dosyasi())
    if acik:  # uygulama zaten açık: ikinci kopya başlamaz, açık olan gösterilir
        kayit.yaz(f"{A.UYGULAMA} zaten açık; tarayıcıda o gösteriliyor")
        if not z.no_browser:
            webbrowser.open(acik)
        return
    s = sunucu.baslat(z.port)
    adres = f"http://127.0.0.1:{sunucu.PORT[0]}/?token={sunucu.TOKEN}"
    tek_kopya.kaydet(yollar.calisan_dosyasi(), sunucu.PORT[0], sunucu.TOKEN)
    atexit.register(tek_kopya.sil, yollar.calisan_dosyasi())
    kayit.yaz(f"{A.UYGULAMA} {A.SURUM} açıldı: {adres} · kurulum klasörü {yollar.kok()}")
    sunucu.onkontrol_baslat()
    if not z.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(adres)).start()
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
