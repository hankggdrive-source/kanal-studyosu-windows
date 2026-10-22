"""Sahne sesinin kenarları: sondaki kesik "dit" ve sondaki izole tık (kullanıcı kararı, 2 Eki 2026).

Hesap, kullanıcının bir videoyu elle düzelttiği ve kulakla onayladığı iki betikten birebir alınmıştır:
  ses_kenar_duzelt.py → analiz() ve filtre()   (tail/tık ve onset, afade değerleri)
  ses_kenar_kontrol.py → kesik() ve sinif()    (1 ms blok tepeleri, sert/orta kesik)
Analiz, sahne sesinin seviyesi ayarlanmış ve sonuna sessizlik eklenmiş hâli (kayıpsız WAV) üzerinde yapılır;
betikler de bitmiş sahne sesini ölçüyordu. Eşikler ayar dosyasında: video.kenar.
"""
from __future__ import annotations

import array
import math
import subprocess

SR = 48000

VARSAYILAN = {
    "ornek_esigi": 8,            # |örnek| > 8 → sesli (son sesli örnek)
    "blok_ms": 5,                # sesli bölüm blokları
    "blok_db": -50,              # blok RMS > -50 dB → sesli
    "bosluk_blok": 12,           # ≤12 blokluk boşluk aynı bölüm
    "tik_ms": 30,                # son bölüm ≤30 ms …
    "tik_sessizlik_ms": 300,     # … ve öncesinde ≥300 ms sessizlik → tık
    "onset_blok_ms": 10,
    "onset_db": -45,
    "onset_pay": 0.025,          # fade-in başı = onset − 25 ms
    "fade_in": 0.010,
    "fade_in_basta": 0.004,      # onset ≈ 0 ise
    "fade_out": 0.030,
    "kontrol_geri_ms": 12,
    "kontrol_tepe": 300,
    "kontrol_taban": 30,
    "sert_db": 25, "sert_dbfs": -35,
    "orta_db": 20, "orta_dbfs": -45,
}


def ayar(kenar: dict | None) -> dict:
    return {**VARSAYILAN, **(kenar or {})}


def pcm(yol, ffmpeg: str = "ffmpeg") -> array.array:
    """Mono 48 kHz 16 bit örnekler (betiklerdeki pcm())."""
    r = subprocess.run([ffmpeg, "-v", "error", "-i", str(yol), "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                       capture_output=True, timeout=600)
    a = array.array("h")
    a.frombytes(r.stdout[:len(r.stdout) // 2 * 2])
    return a


def _rms_db(s, n: int) -> float:
    r = math.sqrt(sum(x * x for x in s) / n) / 32768
    return -99 if r <= 1e-5 else 20 * math.log10(r)


def _son_sesli(a, esik: int) -> int | None:
    for i in range(len(a) - 1, -1, -1):
        if abs(a[i]) > esik:
            return i
    return None


def analiz(a, k: dict) -> dict | None:
    """→ {tik, tail, onset, hc} (saniye); ses tamamen sessizse None."""
    son = _son_sesli(a, k["ornek_esigi"])
    if son is None:
        return None
    e = son / SR
    n5 = int(SR * k["blok_ms"] / 1000)
    bloklar = [_rms_db(a[i:i + n5], n5) for i in range(0, len(a) - n5, n5)]
    sp = [i for i, x in enumerate(bloklar) if x > k["blok_db"]]
    tik, tail = False, e
    if sp:
        bolumler, s, p = [], sp[0], sp[0]
        for i in sp[1:]:
            if i - p > k["bosluk_blok"]:
                bolumler.append((s, p))
                s = i
            p = i
        bolumler.append((s, p))
        if len(bolumler) > 1:
            ls, le = bolumler[-1]
            _, pe = bolumler[-2]
            if (le - ls + 1) * k["blok_ms"] <= k["tik_ms"] and (ls - pe) * k["blok_ms"] >= k["tik_sessizlik_ms"]:
                tik, tail = True, (pe + 1) * k["blok_ms"] / 1000
    n10 = int(SR * k["onset_blok_ms"] / 1000)
    esik = 10 ** (k["onset_db"] / 20)
    onset = None
    for i in range(0, len(a) - n10, n10):
        if math.sqrt(sum(x * x for x in a[i:i + n10]) / n10) / 32768 > esik:
            onset = i / SR
            break
    onset = onset or 0
    hc = max(0.0, onset - k["onset_pay"])
    return {"tik": tik, "tail": round(tail, 4), "onset": round(onset, 4), "hc": round(hc, 4)}


def filtre(an: dict | None, k: dict) -> str:
    """afade zinciri; sessiz seste boş."""
    if not an:
        return ""
    d1 = k["fade_in"] if an["hc"] > 0 else k["fade_in_basta"]
    fo = max(0.0, an["tail"] - k["fade_out"])
    return (f"afade=t=in:st={an['hc']:.4f}:d={d1}:curve=hsin,"
            f"afade=t=out:st={fo:.4f}:d={k['fade_out']}:curve=hsin")


def kesik(a, k: dict) -> tuple[float, float]:
    """(düşüş dB, tepe dBFS): son sesli örnekten 12 ms geriye 1 ms blok tepeleri (betikteki cut())."""
    ms = SR // 1000

    def tepe(i):
        return max((abs(x) for x in a[i * ms:(i + 1) * ms]), default=0)

    son = _son_sesli(a, k["ornek_esigi"])
    if son is None:
        return (0, -99)
    ke, en = son // ms, (0, -99)
    for i in range(max(0, ke - k["kontrol_geri_ms"]), ke + 1):
        hi = tepe(i)
        lo = max(tepe(i + 1), tepe(i + 2), k["kontrol_taban"])
        dr = 20 * math.log10(max(hi, 1) / lo)
        if hi >= k["kontrol_tepe"] and dr > en[0]:
            en = (dr, -99 if hi <= 0 else 20 * math.log10(hi / 32768))
    return en


def sinif(c: tuple[float, float], k: dict) -> str:
    if c[0] >= k["sert_db"] and c[1] >= k["sert_dbfs"]:
        return "sert"
    if c[0] >= k["orta_db"] and c[1] >= k["orta_dbfs"]:
        return "orta"
    return ""


def rms_toplam(a) -> float:
    return 20 * math.log10(max(1e-9, math.sqrt(sum(x * x for x in a) / max(1, len(a))) / 32768))


def ozet(kayitlar: list[dict]) -> dict:
    """Sahne kayıtlarından (scene['kenar']) video özeti; temiz = sonra 0 sert, 0 orta."""
    say = {"sahne": len(kayitlar), "once_sert": 0, "once_orta": 0, "sonra_sert": 0, "sonra_orta": 0, "tik": 0,
           "seviye_db": 0.0, "kalan": []}
    for x in kayitlar:
        if x.get("once"):
            say["once_" + x["once"]] += 1
        if x.get("sonra"):
            say["sonra_" + x["sonra"]] += 1
            say["kalan"].append(f"sahne {x['sahne']:04d} ({x['sonra']}, {x['sonra_db']:.0f} dB)")
        say["tik"] += 1 if x.get("tik") else 0
        say["seviye_db"] = max(say["seviye_db"], abs(x.get("seviye_farki", 0)))
    say["seviye_db"] = round(say["seviye_db"], 2)
    say["temiz"] = say["sonra_sert"] == say["sonra_orta"] == 0
    say["metin"] = (f"{say['sahne']} sahne · düzeltme öncesi sert {say['once_sert']} / orta {say['once_orta']} → "
                    f"sonrası {say['sonra_sert']}/{say['sonra_orta']} · sonda susturulan tık {say['tik']} · "
                    f"en büyük seviye değişimi {say['seviye_db']} dB")
    return say
