"""Uygulama kaydı: stderr'e (başlatıcı Sistem/kayit.log'a yönlendirir) ve arayüz paneli için son satırlar."""
from __future__ import annotations

import collections
import sys
import threading
from datetime import datetime

_SON = collections.deque(maxlen=1500)
_KILIT = threading.Lock()


def yaz(mesaj: str, duzey: str = "bilgi") -> None:
    satir = f"{datetime.now().strftime('%H:%M:%S')} [{duzey}] {mesaj}"
    with _KILIT:
        _SON.append(satir)
    print(satir, file=sys.stderr, flush=True)


def son(n: int = 1000) -> list[str]:
    with _KILIT:
        return list(_SON)[-n:]
