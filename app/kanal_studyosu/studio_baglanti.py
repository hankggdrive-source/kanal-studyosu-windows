"""Ses (AI84 → ElevenLabs) ve sahne videosu (ffmpeg) üretimi.

Dosya düzeni (kanal klasörünün içinde; araçlar bu düzeni bekler):
  Kanallar/<kanal>/Uretim/<kod-…-id8>/
      video.json  script.txt  visuals/sahneNNNN.jpg  audio/sahneNNNN.mp3  scene-videos/sahneNNNN.mp4

Korumalar (eski motordan aynen):
- Aynı metin + aynı ses ayarı (hash) için ses yeniden üretilmez; aynı görsel+ses+ayar için video yeniden üretilmez.
- AI84 iş numarası video.json'a yazılır; bağlantı koparsa "Tekrar dene" yeni ücretli istek yerine aynı işi sorgular.
- Gönderim anında uygulama kapanmışsa (iş numarası alınamadan) sahne 'belirsiz' işaretlenir; yalnız Tekrar dene'de
  yeniden gönderilir (en fazla o sahne için çift ücret riski).
- Ses YouTube seviyesine (−14 LUFS, iki geçişli loudnorm) getirilir; görselin bulanık hâli arka plan olur;
  her sahne sesten 0,4 sn uzundur (nefes payı; senk_kontrol bunu hata saymaz).
Ses ayarı kanal ayarından (kanal.json → ses) gelir ve uygulama tarafından değiştirilmez.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import ai84 as AI
from . import ayarlar as A
from . import kayit
from . import kanal
from . import kontroller
from . import ses_kenar as SK

KILIT = ".kanal_studyosu_kilit"
GORSEL = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
LOUD = {"youtube": {"I": -14, "TP": -1.5, "LRA": 11}}


class StudioHatasi(Exception):
    pass


def _simdi() -> str:
    return datetime.now(timezone.utc).isoformat()


def _program(ad: str) -> str:
    from .onkontrol import _program as bul
    return bul(ad) or ad


def _istemci() -> AI.AI84:
    return AI.AI84(A.anahtar("ai84"))


# --- kanal ve video kayıtları ------------------------------------------------------

def ses_ayari() -> dict:
    return dict(A.ayarlar()["ses"])


def ses_dogrula(ses: dict) -> list[str]:
    """Ses ayarı kanal ayarındaki gibi kullanılır; eksikse üretim durur (uygulama düzeltmez)."""
    sorun = []
    if not ses.get("voice_id"):
        sorun.append("ses (voice_id) seçilmedi")
    if not ses.get("model_id"):
        sorun.append("ses modeli yok")
    return sorun


def kanal_klasoru() -> Path:
    return kanal.uretim_klasoru()


def kanal_bilgisi() -> dict:
    k = kanal.ayar()
    return {"id": k["kimlik"], "name": k["ad"]}


def kisa_konu(kart: str) -> str:
    m = re.search(r"KONU KARTI\s*·\s*[A-Z0-9-]+-\d+\s*·\s*(.+)", kart)
    return m.group(1).strip()[:40] if m else ""


def _slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ]+", "-", s).strip("-").lower()[:50] or "kayit"


def _videolar():
    for f in kanal_klasoru().glob("*/video.json"):
        yield f.parent, json.loads(f.read_text(encoding="utf-8"))


def _video(vid: str) -> tuple[Path, dict]:
    for p, d in _videolar():
        if d.get("id") == vid:
            return p, d
    raise StudioHatasi("Video kaydı bulunamadı.")


def _kaydet(p: Path, d: dict) -> None:
    d["updated_at"] = _simdi()
    A.json_yaz(p / "video.json", d)


def video_bul_ya_da_olustur(kod: str, ad: str, vid: str | None) -> tuple[str, str]:
    """→ (kanal_id, video_id). Kayıtlı video varsa o kullanılır (kaldığı yerden devam)."""
    sorun = ses_dogrula(ses_ayari())
    if sorun:
        raise StudioHatasi("Ses ayarı eksik: " + "; ".join(sorun) + ". Kanal ayarları › Ses'ten tamamla.")
    k = kanal_bilgisi()
    if vid:
        try:
            _video(vid)
            return k["id"], vid
        except StudioHatasi:
            kayit.yaz(f"Kayıtlı video bulunamadı ({vid}); yeni video açılıyor", "uyari")
    if not _slug(ad).startswith(kod.lower()):
        raise StudioHatasi("Video adı video koduyla başlamalı.")
    vid = uuid.uuid4().hex
    p = kanal_klasoru() / f"{_slug(ad)}-{vid[:8]}"
    for x in ("visuals", "audio", "scene-videos", "temp", "logs"):
        (p / x).mkdir(parents=True, exist_ok=True)
    d = {"id": vid, "channel_id": k["id"], "name": ad.strip(), "stage": "script", "voice_snapshot": ses_ayari(),
         "video_settings": A.ayarlar()["video"], "script_approved": False, "media_approved": False, "scenes": [],
         "created_at": _simdi(), "updated_at": _simdi(), "olusturan": "Kanal Stüdyosu"}
    _kaydet(p, d)
    (p / "script.txt").write_text("", encoding="utf-8")
    return k["id"], vid


def video_klasoru(cid: str, vid: str) -> Path:
    return _video(vid)[0]


def _ayristir(t: str) -> list[str]:
    return [re.sub(r"\s*\n\s*", " ", x).strip() for x in
            re.split(r"\n\s*\n+", t.replace("\r\n", "\n").replace("\r", "\n").strip()) if x.strip()]


def metin_ver(cid: str, vid: str, metin: str, beklenen: int) -> None:
    p, d = _video(vid)
    parcalar, eski, sahneler = _ayristir(metin), d["scenes"], []
    for i, x in enumerate(parcalar, 1):
        s = eski[i - 1] if i <= len(eski) and eski[i - 1].get("text") == x else \
            {"id": uuid.uuid4().hex, "audio_status": "pending", "video_status": "pending"}
        s.update(number=i, text=x)
        sahneler.append(s)
    d.update(scenes=sahneler, script_approved=True, stage="visuals", voice_snapshot=ses_ayari())
    A.atomik_yaz(p / "script.txt", metin)
    _kaydet(p, d)
    if len(sahneler) != beklenen:
        raise StudioHatasi(f"{len(sahneler)} sahne algılandı, beklenen {beklenen}.")


def _sure(f: Path) -> float | None:
    if not f.exists():
        return None
    q = subprocess.run([_program("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", str(f)], capture_output=True, text=True)
    try:
        return round(float(q.stdout.strip()), 3) if q.returncode == 0 else None
    except ValueError:
        return None


def _numara(ad: str) -> int | None:
    m = re.match(r"(?i)^sahne-?(\d{4})(?:[^0-9].*)?\.[^.]+$", ad)
    return int(m.group(1)) if m else None


def tara(p: Path, d: dict, tam: bool = False) -> dict:
    """visuals/ (ve tam=True ise audio/) eşleşmesi; sahne kayıtlarını günceller."""
    by: dict[int, list[Path]] = {}
    for f in (p / "visuals").iterdir():
        if f.is_file() and f.suffix.lower() in GORSEL | VIDEO and _numara(f.name):
            by.setdefault(_numara(f.name), []).append(f)
    say = {"matched": 0, "missing": 0, "conflicts": 0, "audio_missing": 0, "audio_invalid": 0}
    satirlar = []
    for s in d["scenes"]:
        fs, r = by.get(s["number"], []), {"scene": s["number"]}
        if not fs:
            say["missing"] += 1
            s["media_file"] = None
        elif len(fs) > 1:
            say["conflicts"] += 1
            s["media_file"] = None
        else:
            f = fs[0]
            tur = "image" if f.suffix.lower() in GORSEL else "video"
            say["matched"] += 1
            s.update(media_file="visuals/" + f.name, media_type=tur)
            r["type"] = tur
            if tur == "video":
                r["media_duration"] = _sure(f)
        if tam:
            a = p / "audio" / f"sahne{s['number']:04d}.mp3"
            sure = _sure(a)
            if not a.exists():
                say["audio_missing"] += 1
            elif not sure:
                say["audio_invalid"] += 1
            else:
                s.update(audio_file="audio/" + a.name, audio_duration=sure)
                r["audio_duration"] = sure
                if r.get("type") == "video" and r.get("media_duration") is not None:
                    z = r["media_duration"] - sure
                    tol = float(d["video_settings"].get("tolerance_seconds", .3))
                    r["duration_kind"] = "video_long" if z > tol else "video_short" if z < -tol else "matched"
        satirlar.append(r)
    ok = say["missing"] == say["conflicts"] == 0 and (not tam or say["audio_missing"] == say["audio_invalid"] == 0)
    rapor = {"ok": ok, "counts": say, "rows": satirlar}
    d["last_media_scan"] = rapor
    _kaydet(p, d)
    return rapor


def gorselleri_koy(cid: str, vid: str, kaynak: dict[int, Path]) -> dict:
    """kaynak: sahne no → görsel. visuals/sahneNNNN.jpg olarak kopyalanır, kontrol edilip onaylanır."""
    p, d = _video(vid)
    (p / "visuals").mkdir(exist_ok=True)
    for n, yol in sorted(kaynak.items()):
        hedef = p / "visuals" / f"sahne{n:04d}{Path(yol).suffix.lower() or '.jpg'}"
        if not hedef.exists() or hedef.stat().st_size != Path(yol).stat().st_size:
            shutil.copy2(yol, hedef)
    r = tara(p, d)
    c = r["counts"]
    if not r["ok"]:
        raise StudioHatasi(f"Görsel eşleşmesi: {c['matched']} eşleşen, {c['missing']} eksik, {c['conflicts']} çakışan.")
    d.update(media_approved=True, stage="tts")
    _kaydet(p, d)
    return c


# --- ses ---------------------------------------------------------------------------

def _ses_hash(metin: str, ses: dict) -> str:
    # Eski motorla aynı formül: önceden üretilmiş sesler de tanınır.
    return hashlib.sha256((metin + "\0" + json.dumps(ses, sort_keys=True)).encode()).hexdigest()


# Kullanıcı kararı (2 Eki 2026): yalnız ses servisine giden kopyada kıvrık apostrof/tırnak düzleştirilir.
DUZ = str.maketrans({"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'})


def _tts_govde(ses: dict, metin: str) -> dict:
    b = {"text": metin.translate(DUZ), "voice_id": ses["voice_id"], "model_id": ses["model_id"],
         "output_format": ses.get("output_format", "mp3_44100_128"), "with_transcript": False,
         "voice_settings": {k: ses[k] for k in ("stability", "similarity_boost", "style", "speed", "use_speaker_boost")}}
    if ses.get("language_code"):
        b["language_code"] = ses["language_code"]
    return b


def _log(p: Path, olay: str, mesaj: str, n=None) -> None:
    (p / "logs").mkdir(exist_ok=True)
    with open(p / "logs" / "events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": _simdi(), "event": olay, "message": mesaj, "scene": n}, ensure_ascii=False) + "\n")


def _istek_kaydi(p: Path, n: int, govde: dict, jid, dosya: str) -> None:
    """logs/tts_istekleri.jsonl: sahneye ait TAM istek (anahtar başlıkta gider, burada yok) → birebir tekrar."""
    (p / "logs").mkdir(exist_ok=True)
    satir = {"time": _simdi(), "scene": n, "audio_file": "audio/" + dosya, "job_id": jid, **govde,
             "apply_text_normalization": govde.get("apply_text_normalization", "gönderilmedi"),
             "seed": govde.get("seed", "gönderilmedi")}
    with open(p / "logs" / "tts_istekleri.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(satir, ensure_ascii=False) + "\n")


def seslendir(vid: str, ilerleme, tekrar: bool = False, iptal=None, api: AI.AI84 | None = None) -> dict:
    p, d = _video(vid)
    sorun = kontroller.elevenlabs_metni("\n\n".join(x["text"] for x in d["scenes"]))
    if sorun:  # ikinci güvence: AI84'e izinsiz köşeli not gitmesin
        raise StudioHatasi("Seslendirme başlatılmadı; metinde izin verilmeyen köşeli not var: " + "; ".join(sorun[:8]))
    ses = d.get("voice_snapshot") or ses_ayari()
    api = api or _istemci()
    toplam, ok, hatali, kredi = len(d["scenes"]), 0, 0, 0
    for s in d["scenes"]:
        if iptal and iptal():
            return {"durum": "durdu", "ok": ok, "failed": hatali, "total": toplam}
        h, a, st = _ses_hash(s["text"], ses), p / "audio" / f"sahne{s['number']:04d}.mp3", s.get("audio_status")
        if st == "completed" and s.get("generated_hash") == h and a.exists():
            ok += 1
            continue
        if st == "submitting" and not s.get("job_id"):
            s.update(audio_status="unknown",
                     audio_error="Önceki gönderimin sonucu belirsiz (uygulama gönderim anında kapanmış olabilir).")
            _kaydet(p, d)
            st = "unknown"
        if st == "unknown" and not s.get("job_id") and not tekrar:
            hatali += 1
            continue
        if st == "failed" and not tekrar:
            hatali += 1
            continue
        ilerleme(f"Ses {s['number']}/{toplam} · {ok} tamam" + (f", {hatali} hatalı" if hatali else ""))
        try:
            jid = s.get("job_id") if s.get("job_hash", h) == h else None
            if not jid:
                s.update(audio_status="submitting", job_id=None, job_hash=h)
                _kaydet(p, d)
                govde = _tts_govde(ses, s["text"])
                q = api.tts_gonder(govde)
                jid = q.get("job_id") or q.get("task_id")
                _istek_kaydi(p, s["number"], govde, jid, a.name)
                s.update(job_id=jid, job_hash=h, audio_status="queued")
                _kaydet(p, d)
            job = api.tts_bekle(jid)
            ham = api.indir(job["audioUrl"])
            if len(ham) < 128:
                raise AI.AI84Hatasi("İndirilen ses geçersiz.", 2)
            gecici = p / "temp" / (a.name + ".part")
            gecici.parent.mkdir(exist_ok=True)
            gecici.write_bytes(ham)
            os.replace(gecici, a)
            kredi += int(job.get("credit_cost") or 0)
            s.update(audio_status="completed", audio_file="audio/" + a.name, audio_duration=_sure(a), generated_hash=h,
                     job_id=None, job_hash=None, audio_error=None, credit_cost=job.get("credit_cost"))
            ok += 1
            _log(p, "tts_completed", "Ses üretildi", s["number"])
        except AI.AI84Hatasi as e:
            # İş başarısız bittiyse (failed) iş numarası silinir; zaman aşımında korunur (Tekrar dene aynı işi sorgular).
            sakla = e.kategori is None and s.get("job_id")
            s.update(audio_status="failed", audio_error=str(e), **({} if sakla else {"job_id": None, "job_hash": None}))
            hatali += 1
            _log(p, "tts_failed", str(e), s["number"])
            if e.http in (401, 403):  # anahtar/hesap sorunu: diğer sahneleri denemenin anlamı yok
                _kaydet(p, d)
                raise StudioHatasi(str(e))
        _kaydet(p, d)
    if hatali == 0:
        d["stage"] = "check"
        _kaydet(p, d)
    kayit.yaz(f"Ses: {ok} başarılı, {hatali} hatalı · AI84 kredi {kredi}")
    return {"durum": "bitti", "ok": ok, "failed": hatali, "total": toplam, "kredi": kredi}


def ses_olcumu(vid: str) -> tuple[int, float] | None:
    """Konuşma hızı ölçümü için → (kelime, süre sn). Süre bütün sahne seslerinin toplamı + sahne arası duraklar
    (videodaki gibi); ses tag'leri ([calm] gibi) kelime sayılmaz. Bir sahnenin süresi bilinmiyorsa None."""
    p, d = _video(vid)
    sahneler = d.get("scenes") or []
    if not sahneler or any(not isinstance(s.get("audio_duration"), (int, float)) for s in sahneler):
        return None
    kelime = sum(len([w for w in re.sub(r"\[[^\]\n]*\]", " ", s["text"]).split() if re.search(r"\w", w)])
                 for s in sahneler)
    ara = float((d.get("video_settings") or {}).get("pause_seconds", .4))
    return kelime, sum(s["audio_duration"] for s in sahneler) + ara * len(sahneler)


# --- sahne videosu -------------------------------------------------------------------

def _vf(w: int, h: int, fps: int, fit: str) -> str:
    if fit == "crop":
        return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps},format=yuv420p"
    if fit == "blur":
        # Arka plan: görselin kendisi, ekranı dolduracak şekilde büyütülüp bulanıklaştırılır (hız için küçük boyutta).
        bw, bh = max(2, w // 8 // 2 * 2), max(2, h // 8 // 2 * 2)
        return (f"split=2[bg][fg];[bg]scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},gblur=sigma=6,"
                f"eq=brightness=-0.06,scale={w}:{h},setsar=1[bgb];[fg]scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"setsar=1[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2,fps={fps},format=yuv420p")
    return f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={fps},format=yuv420p"


def _loudnorm(a: Path, mod: str) -> str:
    """İki geçişli loudnorm: önce ölç, sonra ölçülen değerlerle doğrusal normalizasyon filtresi."""
    t = LOUD.get(mod)
    if not t:
        return ""
    q = subprocess.run([_program("ffmpeg"), "-hide_banner", "-nostats", "-i", str(a), "-af",
                        f"loudnorm=I={t['I']}:TP={t['TP']}:LRA={t['LRA']}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=600)
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', q.stderr)
    if q.returncode or not m:
        raise StudioHatasi("Ses seviyesi ölçülemedi.")
    x = json.loads(m.group(0))
    if any(not re.fullmatch(r"-?\d+(\.\d+)?", str(x.get(k, ""))) for k in
           ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")):
        return ""  # sessiz/çok kısa ses: dokunma
    return (f"loudnorm=I={t['I']}:TP={t['TP']}:LRA={t['LRA']}:measured_I={x['input_i']}:measured_TP={x['input_tp']}:"
            f"measured_LRA={x['input_lra']}:measured_thresh={x['input_thresh']}:offset={x['target_offset']}:"
            "linear=true,aresample=48000,")


def _dosya_hash(f: Path) -> str:
    h = hashlib.sha256()
    with open(f, "rb") as x:
        for b in iter(lambda: x.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def videolari_uret(vid: str, ilerleme, tekrar: bool = False, iptal=None) -> dict:
    p, d = _video(vid)
    rapor = tara(p, d, True)
    if not rapor["ok"]:
        raise StudioHatasi("Son kontrolde eksik veya çakışan dosya var.")
    satir = {x["scene"]: x for x in rapor["rows"]}
    s0 = {"loudness": "youtube", **d["video_settings"]}
    w, h, fps = int(s0.get("width", 1920)), int(s0.get("height", 1080)), int(s0.get("fps", 30))
    ara = float(s0.get("pause_seconds", .4))
    toplam, ok, hatali = len(d["scenes"]), 0, 0
    for s in d["scenes"]:
        if iptal and iptal():
            return {"durum": "durdu", "ok": ok, "failed": hatali, "total": toplam}
        r = satir[s["number"]]
        m, a = p / s["media_file"], p / s["audio_file"]
        tur = r.get("duration_kind", "image")
        ek = "-video-uzun" if tur == "video_long" else "-video-kisa" if tur == "video_short" else ""
        cikti = p / "scene-videos" / f"sahne{s['number']:04d}{ek}.mp4"
        hedef = max(r.get("media_duration") or 0, (r["audio_duration"] or 0) + ara)
        imza = hashlib.sha256((_dosya_hash(m) + _dosya_hash(a) + json.dumps(s0, sort_keys=True)).encode()).hexdigest()
        if s.get("video_status") == "completed" and s.get("video_signature") == imza and cikti.exists():
            ok += 1
            continue
        if s.get("video_status") == "failed" and not tekrar:
            hatali += 1
            continue
        ilerleme(f"Sahne videosu {s['number']}/{toplam} · {ok} tamam" + (f", {hatali} hatalı" if hatali else ""))
        s["video_status"] = "processing"
        _kaydet(p, d)
        try:
            filtre = _vf(w, h, fps, s0.get("fit", "blur"))
            komut = [_program("ffmpeg"), "-y"] + (["-loop", "1"] if s["media_type"] == "image" else []) + \
                ["-i", str(m), "-i", str(a)]
            if s["media_type"] == "video":
                filtre += f",tpad=stop_mode=clone:stop_duration={max(0, hedef - (r.get('media_duration') or 0)):.3f}"
            gecici = str(cikti) + ".part.mp4"
            ses_filtresi = _loudnorm(a, s0.get("loudness")) + f"apad=pad_dur={max(0, hedef - r['audio_duration']):.3f}"
            kenar, wav = None, None
            if s0.get("kenar"):  # kenar yumuşatma: yalnız bu ayarla açılmış (yeni) videolarda
                k = SK.ayar(s0["kenar"])
                wav = p / "temp" / f"sahne{s['number']:04d}.kenar.wav"
                wav.parent.mkdir(exist_ok=True)
                q = subprocess.run([_program("ffmpeg"), "-y", "-v", "error", "-i", str(a), "-af", ses_filtresi,
                                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", "-t", f"{hedef:.3f}", str(wav)],
                                   capture_output=True, text=True, timeout=600)
                if q.returncode:
                    raise StudioHatasi(q.stderr[-800:])
                a0 = SK.pcm(wav, _program("ffmpeg"))
                kenar = SK.analiz(a0, k)
                komut[-1] = str(wav)  # ses girişi: seviyesi ayarlı kayıpsız WAV (ses tek kez kodlanır)
                ses_filtresi = SK.filtre(kenar, k) or "anull"
            komut += ["-vf", filtre, "-af", ses_filtresi, "-map", "0:v:0", "-map", "1:a:0",
                      "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a",
                      "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", "-t", f"{hedef:.3f}", gecici]
            q = subprocess.run(komut, capture_output=True, text=True, timeout=1800)
            if q.returncode:
                raise StudioHatasi(q.stderr[-800:])
            if wav:
                a1 = SK.pcm(gecici, _program("ffmpeg"))
                once, sonra = SK.kesik(a0, k), SK.kesik(a1, k)
                s["kenar"] = {"sahne": s["number"], **(kenar or {"sessiz": True}),
                              "once": SK.sinif(once, k), "once_db": round(once[0], 1),
                              "sonra": SK.sinif(sonra, k), "sonra_db": round(sonra[0], 1),
                              "seviye_farki": round(SK.rms_toplam(a0) - SK.rms_toplam(a1), 3)}
                wav.unlink(missing_ok=True)  # uygulamanın kendi ara dosyası; ham mp3 audio/ içinde aynen durur
            os.replace(gecici, cikti)
            s.update(video_status="completed", video_file="scene-videos/" + cikti.name, video_signature=imza,
                     output_duration=_sure(cikti), duration_kind=tur, video_error=None)
            ok += 1
            _log(p, "render_completed", "Video üretildi", s["number"])
        except (StudioHatasi, subprocess.TimeoutExpired, OSError) as e:
            s.update(video_status="failed", video_error=str(e)[-800:])
            hatali += 1
            _log(p, "render_failed", str(e)[-300:], s["number"])
        _kaydet(p, d)
    d["stage"] = "render"
    _kaydet(p, d)
    return {"durum": "bitti", "ok": ok, "failed": hatali, "total": toplam}


def kenar_ozeti(vid: str) -> dict | None:
    """Sahne seslerinin kenar kontrolü özeti (kenar ayarı olmayan eski videolarda None)."""
    _, d = _video(vid)
    if not d.get("video_settings", {}).get("kenar"):
        return None
    return SK.ozet([s["kenar"] for s in d["scenes"] if s.get("kenar")])


def is_calistir(tur: str, cid: str, vid: str, ilerleme, tekrar: bool = False, iptal=None) -> dict:
    """tts: seslendirme, render: sahne videoları. Durdur o anki sahne bitince etkili olur."""
    j = seslendir(vid, ilerleme, tekrar, iptal) if tur == "tts" else videolari_uret(vid, ilerleme, tekrar, iptal)
    ad = "Ses" if tur == "tts" else "Sahne videosu"
    if j["durum"] == "durdu":
        raise StudioHatasi(f"Durduruldu ({j['ok']}/{j['total']} sahne hazır). Tekrar dene kaldığı yerden sürer; "
                           "biten sahneler yeniden üretilmez.")
    kayit.yaz(f"{ad}: {j['ok']} başarılı, {j['failed']} hatalı")
    return j


def son_kontrol(cid: str, vid: str) -> None:
    p, d = _video(vid)
    r = tara(p, d, True)
    c = r["counts"]
    if not r["ok"]:
        raise StudioHatasi(f"Son kontrol: {c['audio_missing']} ses eksik, {c['audio_invalid']} ses bozuk, "
                           f"{c['missing']} görsel eksik.")
    d["stage"] = "render"
    _kaydet(p, d)


def videolari_dogrula(klasor: Path, beklenen: int) -> dict:
    """ffprobe: hepsi 1920x1080, 30 fps, sesli. → {'sure': sn, 'sorunlar': [...]}"""
    dosyalar = [f for f in sorted((klasor / "scene-videos").glob("sahne*.mp4"))
                if re.fullmatch(r"sahne\d{4}(-video-(uzun|kisa))?\.mp4", f.name)]
    sorun, toplam = [], 0.0
    if len(dosyalar) != beklenen:
        sorun.append(f"{len(dosyalar)} sahne videosu var, beklenen {beklenen}.")
    for f in dosyalar:
        q = subprocess.run([_program("ffprobe"), "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", str(f)],
                           capture_output=True, text=True)
        try:
            j = json.loads(q.stdout)
            v = next(x for x in j["streams"] if x["codec_type"] == "video")
            toplam += float(j["format"]["duration"])
        except (ValueError, KeyError, StopIteration):
            sorun.append(f"{f.name} okunamadı")
            continue
        if (v.get("width"), v.get("height")) != (1920, 1080):
            sorun.append(f"{f.name} boyut {v.get('width')}x{v.get('height')}")
        if v.get("r_frame_rate") not in ("30/1", "30000/1000"):
            sorun.append(f"{f.name} kare hızı {v.get('r_frame_rate')}")
        if not any(x["codec_type"] == "audio" for x in j["streams"]):
            sorun.append(f"{f.name} ses yok")
    return {"sure": round(toplam, 2), "sorunlar": sorun}


def sure_metni(sn: float) -> str:
    m, s = divmod(int(round(sn)), 60)
    return f"{m}:{s:02d}"


# --- aynı videoda iki süreç çalışmasın ----------------------------------------------------

def kilit_al(klasor: Path, kod: str) -> None:
    """Video klasörüne kilit dosyası; başka bir Kanal Stüdyosu süreci aynı videoda çalışıyorsa durur."""
    k = klasor / KILIT
    if k.exists():
        try:
            pid = int(json.loads(k.read_text(encoding="utf-8")).get("pid", 0))
            from .sistem_win import surec_yasiyor  # Windows'ta os.kill(pid, 0) süreci sonlandırır
            if surec_yasiyor(pid) and pid != os.getpid():
                raise StudioHatasi("Bu video başka bir Kanal Stüdyosu penceresinde işleniyor.")
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass  # eski/yarım kalmış kilit: üzerine yazılır
    k.write_text(json.dumps({"pid": os.getpid(), "kod": kod, "zaman": time.strftime("%Y-%m-%d %H:%M:%S")}),
                 encoding="utf-8")


def kilit_birak(klasor: Path) -> None:
    k = klasor / KILIT
    if k.exists():
        k.unlink()  # yalnız uygulamanın kendi kilit dosyası; kullanıcı dosyası değil
