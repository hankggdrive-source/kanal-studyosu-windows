"""Claude Code (abonelik) üzerinden yazım.

Uygulama `claude` komutunu ekransız (-p) çalıştırır; Claude Code kullanıcının Pro/Max aboneliğiyle giriş yapmış
olmalıdır. Her istekte:
- sistem metni bizimkidir (proje dosyaları + beceri + çerçeve + KANAL AYARLARI): `--system-prompt-file`;
  Claude Code'un kod asistanı talimatları kullanılmaz,
- mesaj `--input-format stream-json` ile verilir (görseller de aynı biçimde gider; araç gerekmez),
- araçlar kapalıdır (`--tools ""`); yalnız web araması olan işlerde (1–2. aşama) `WebSearch` açılır,
- kullanıcının Claude Code ayarları, becerileri, eklentileri ve MCP sunucuları yüklenmez (`--safe-mode`,
  `--strict-mcp-config`); çalışma klasörü boş bir klasördür (Sistem/claude_code), dosyalara dokunamaz,
- ANTHROPIC_API_KEY gibi değişkenler ortamdan çıkarılır: istek API'ye değil aboneliğe gider,
- düzeltme turunda aynı Claude Code oturumu `--resume` ile sürdürülür (model önceki yazdığını hatırlar).
Eski bir Claude Code sürümü bir bayrağı tanımazsa o bayrak çıkarılıp yeniden denenir ve kayda yazılır.
Ücret token başına değil aboneliktir; Claude Code'un verdiği tahmini tutar yalnız bilgi olarak kaydedilir.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

from . import ayarlar as A
from . import kayit
from . import yollar
from .sistem_win import gizli

ZAMAN_ASIMI = 45 * 60          # bir çağrı en fazla (sn)
EN_FAZLA_TUR = 40               # web aramalı işlerde ajan turları
_TEMIZLENECEK_ORTAM = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_USE_BEDROCK",
                       "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY", "ANTHROPIC_MODEL")
_ATILAN_BAYRAKLAR: set[str] = set()  # bu Claude Code sürümünün tanımadığı bayraklar (oturum boyunca)


class ClaudeCodeHatasi(Exception):
    """Kullanıcıya gösterilecek kısa Türkçe mesaj."""


def komut_yolu() -> str | None:
    """`claude` programının yolu (PATH'te yoksa Windows'taki bilinen kurulum yerlerine de bakılır)."""
    ozel = os.environ.get("KANAL_STUDYOSU_CLAUDE")
    if ozel:
        return ozel
    bulunan = shutil.which("claude")
    if bulunan:
        return bulunan
    ev = Path.home()
    appdata = Path(os.environ.get("APPDATA", str(ev / "AppData/Roaming")))
    yerel = Path(os.environ.get("LOCALAPPDATA", str(ev / "AppData/Local")))
    for aday in (ev / ".local/bin/claude.exe", ev / ".claude/local/claude.exe", appdata / "npm/claude.cmd",
                 yerel / "Programs/claude/claude.exe", ev / ".local/bin/claude"):
        if aday.exists():
            return str(aday)
    return None


def _komut(yol: str) -> list[str]:
    """npm kurulumundaki claude.cmd doğrudan çalıştırılamaz; cmd /c ile çağrılır."""
    return ["cmd", "/c", yol] if yol.lower().endswith((".cmd", ".bat")) else [yol]


def calisma_klasoru() -> Path:
    k = yollar.sistem() / "claude_code"
    k.mkdir(parents=True, exist_ok=True)
    return k


def _ortam() -> dict:
    ev = Path.home()
    yol = os.pathsep.join([str(ev / ".local" / "bin"), str(Path(os.environ.get("APPDATA", str(ev / "AppData/Roaming"))) / "npm"),
                           os.environ.get("PATH", "")])
    o = {k: v for k, v in os.environ.items() if k.upper() not in _TEMIZLENECEK_ORTAM}
    o.update(PATH=yol, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1", PYTHONUTF8="1")
    return o


def durum() -> tuple[bool, str]:
    """Kurulu mu, abonelikle giriş yapılmış mı (ücretsiz; model çağrılmaz)."""
    yol = komut_yolu()
    if not yol:
        return False, "Claude Code bulunamadı. Kurmak için: https://claude.com/claude-code (PowerShell'de `claude --version` çalışmalı)."
    try:
        surum = subprocess.run(_komut(yol) + ["--version"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=30, env=_ortam(), **gizli()).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, f"Claude Code çalıştırılamadı ({e})."
    try:
        p = subprocess.run(_komut(yol) + ["auth", "status"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30, env=_ortam(), **gizli())
        j = json.loads(p.stdout or "{}")
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return True, f"Claude Code kurulu ({surum}). Giriş durumu okunamadı; ilk yazımda denenecek."
    yontem = j.get("authMethod", "")
    if p.returncode != 0 or yontem in ("", "none"):
        return False, f"Claude Code kurulu ({surum}) ama giriş yapılmamış. PowerShell'de `claude` yazıp /login ile aboneliğinle giriş yap."
    if yontem != "claude.ai":
        return True, (f"Claude Code kurulu ({surum}); giriş yöntemi '{yontem}'. Abonelik (claude.ai) değilse ücret API "
                      "hesabından düşer.")
    return True, f"Claude Code kurulu ({surum}), abonelikle giriş yapılmış."


# --- mesajlar ----------------------------------------------------------------------

def _icerik_listesi(icerik) -> list[dict]:
    if isinstance(icerik, str):
        return [{"type": "text", "text": icerik}]
    return [b for b in icerik if b.get("type") in ("text", "image")]


def _metin(icerik) -> str:
    return "\n\n".join(b.get("text", "") for b in _icerik_listesi(icerik) if b.get("type") == "text")


def oturum_kimligi(mesaj: dict) -> str:
    if mesaj.get("role") != "assistant" or not isinstance(mesaj.get("content"), list):
        return ""
    return next((b.get("oturum", "") for b in mesaj["content"] if b.get("oturum")), "")


def plan(mesajlar: list[dict]) -> tuple[str, list[dict]]:
    """→ (sürdürülecek oturum kimliği ya da '', gönderilecek kullanıcı içeriği).
    Son asistan turunda Claude Code oturumu varsa yalnız ondan sonraki kullanıcı mesajları gönderilir; yoksa (ilk tur
    ya da yazım servisi sonradan değiştiyse) konuşmanın tamamı tek mesajda verilir."""
    son = max((i for i, m in enumerate(mesajlar) if oturum_kimligi(m)), default=-1)
    if son >= 0 and all(m.get("role") == "user" for m in mesajlar[son + 1:]) and mesajlar[son + 1:]:
        icerik: list[dict] = []
        for m in mesajlar[son + 1:]:
            icerik += _icerik_listesi(m["content"])
        return oturum_kimligi(mesajlar[son]), icerik
    if len(mesajlar) == 1:
        return "", _icerik_listesi(mesajlar[0]["content"])
    # Önceki turlar başka bir servisle yazıldı: konuşma metin olarak aktarılır, son kullanıcı mesajı aynen eklenir.
    gecmis = []
    for m in mesajlar[:-1]:
        kim = "KULLANICI" if m.get("role") == "user" else "SEN (önceki cevabın)"
        gecmis.append(f"<tur kim=\"{kim}\">\n{_metin(m['content'])}\n</tur>")
    on = {"type": "text", "text": "Bu konuşmanın önceki turları aşağıda. Onların devamı olarak cevap ver.\n\n"
          + "\n\n".join(gecmis)}
    return "", [on] + _icerik_listesi(mesajlar[-1]["content"])


# --- çağrı -----------------------------------------------------------------------

def _bayraklar(model: str, efor: str | None, web: bool, oturum: str, sistem_dosyasi: Path) -> list[str]:
    b = ["-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
         "--include-partial-messages", "--model", model, "--system-prompt-file", str(sistem_dosyasi),
         "--safe-mode", "--strict-mcp-config", "--max-turns", str(EN_FAZLA_TUR if web else 3)]
    if web:
        b += ["--tools", "WebSearch", "--allowedTools", "WebSearch"]
    else:
        b += ["--tools", ""]
    if efor:
        b += ["--effort", efor]
    if oturum:
        b += ["--resume", oturum]
    sonuc, i = [], 0
    while i < len(b):  # tanınmayan bayraklar (ve değerleri) çıkarılır
        tek = b[i] in ("-p", "--verbose", "--include-partial-messages", "--safe-mode", "--strict-mcp-config")
        if b[i] in _ATILAN_BAYRAKLAR:
            i += 1 if tek else 2
            continue
        sonuc += [b[i]] if tek else b[i:i + 2]
        i += 1 if tek else 2
    return sonuc


def _hata_mesaji(metin: str) -> str:
    m = metin.lower()
    if re.search(r"usage limit|rate limit|limit reached|limit will reset|resets|5-hour|weekly limit|out of extra usage", m):
        saat = re.search(r"reset[s]?\s*(?:at)?\s*([0-9:apm\s]+(?:\([^)]*\))?)", metin, re.I)
        return ("Claude Code kullanım sınırına ulaşıldı" + (f" (açılış: {saat.group(1).strip()})" if saat else "") +
                ". Sınır açılınca Tekrar dene; adım kaldığı yerden sürer.")
    if re.search(r"not logged in|please run /login|invalid api key|authentication|oauth token|log in", m):
        return "Claude Code'da giriş yapılmamış ya da oturum süresi dolmuş. PowerShell'de `claude` yazıp /login ile aboneliğinle giriş yap, sonra Tekrar dene."
    if re.search(r"credit balance|billing", m):
        return "Claude Code hesabı ücret/kredi hatası verdi. Abonelikle giriş yaptığından emin ol (claude /login)."
    if re.search(r"overloaded|529|internal server error|api error: 5\d\d|connection", m):
        return "Claude şu an yoğun ya da ulaşılamıyor. Biraz sonra Tekrar dene."
    return "Claude Code bir hata verdi. Ayrıntı kayıt panelinde."


def istek(is_adi: str, sistem: list[str], mesajlar: list[dict], ilerleme=None, iptal=None) -> dict:
    """Claude Code'u çalıştırır. Döner: {'metin', 'oturum', 'kullanim', 'model', 'tahmini_usd', 'sunulan'}."""
    yol = komut_yolu()
    if not yol:
        raise ClaudeCodeHatasi("Claude Code bulunamadı. Kurup PowerShell'de `claude` ile aboneliğinle giriş yap.")
    ayar = A.ayarlar()
    isa = ayar["isler"][is_adi]
    model = isa["model"]
    efor = isa.get("efor") if ayar["modeller"].get(model, {}).get("efor") else None
    web = bool(isa.get("web_arama"))
    oturum, icerik = plan(mesajlar)
    kl = calisma_klasoru()
    sistem_dosyasi = kl / f"sistem_{os.getpid()}_{threading.get_ident()}.md"
    sistem_dosyasi.write_text("\n\n".join(t for t in sistem if t) or "Türkçe, kısa ve doğru cevap ver.", encoding="utf-8")
    ortam = _ortam()
    ortam["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(int(isa.get("max_token", 32000)))
    girdi = json.dumps({"type": "user", "message": {"role": "user", "content": icerik}}, ensure_ascii=False) + "\n"
    try:
        for _deneme in range(6):
            komut = _komut(yol) + _bayraklar(model, efor, web, oturum, sistem_dosyasi)
            sonuc = _calistir(komut, girdi, ortam, kl, ilerleme, iptal)
            tanimsiz = re.search(r"unknown option '?(--[\w-]+)", sonuc["stderr"], re.I)
            if sonuc["kod"] != 0 and tanimsiz and tanimsiz.group(1) not in _ATILAN_BAYRAKLAR:
                _ATILAN_BAYRAKLAR.add(tanimsiz.group(1))
                kayit.yaz(f"Claude Code bu sürümde {tanimsiz.group(1)} bayrağını tanımıyor; onsuz deneniyor", "uyari")
                continue
            break
    finally:
        sistem_dosyasi.unlink(missing_ok=True)
    son = sonuc["sonuc"]
    if son is None or son.get("is_error") or son.get("subtype") not in (None, "success"):
        metin = json.dumps(son, ensure_ascii=False)[:1500] if son else ""
        ayrinti = (metin + "\n" + sonuc["stderr"][-1500:]).strip()
        kayit.yaz(f"Claude Code hatası ({is_adi}, çıkış {sonuc['kod']}): {ayrinti}", "hata")
        if son and son.get("subtype") == "error_max_turns":
            raise ClaudeCodeHatasi("Claude Code tur sınırına ulaştı (web araması çok uzadı). Tekrar dene.")
        raise ClaudeCodeHatasi(_hata_mesaji(ayrinti))
    metin = "\n\n".join(t for t in sonuc["metinler"] if t.strip()) or son.get("result", "")
    u = son.get("usage") or {}
    stu = u.get("server_tool_use") or {}
    kullanim = {k: int(u.get(k) or 0) for k in
                ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
    kullanim["web_search_requests"] = int(stu.get("web_search_requests") or 0)
    sunulan = next(iter(son.get("modelUsage") or {}), "") or model
    return {"metin": metin, "oturum": son.get("session_id", ""), "kullanim": kullanim, "model": model,
            "tahmini_usd": float(son.get("total_cost_usd") or 0), "sunulan": sunulan}


def _calistir(komut: list[str], girdi: str, ortam: dict, kl: Path, ilerleme, iptal) -> dict:
    from .llm import Durduruldu
    try:
        p = subprocess.Popen(komut, cwd=str(kl), env=ortam, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", bufsize=1, **gizli())
    except OSError as e:
        raise ClaudeCodeHatasi(f"Claude Code başlatılamadı ({e}).")
    hata_parcalari: list[str] = []
    threading.Thread(target=lambda: hata_parcalari.append(p.stderr.read()), daemon=True).start()
    p.stdin.write(girdi)
    p.stdin.close()
    metinler: list[str] = []
    sonuc = None
    yazilan = 0
    baslangic = time.time()
    satirlar: list[str] = []
    okuyucu_bitti = threading.Event()

    def oku():
        for s in p.stdout:
            satirlar.append(s)
        okuyucu_bitti.set()
    threading.Thread(target=oku, daemon=True).start()
    islenen = 0
    while True:
        bitti = okuyucu_bitti.wait(0.3)
        while islenen < len(satirlar):
            s = satirlar[islenen].strip()
            islenen += 1
            if not s.startswith("{"):
                continue
            try:
                o = json.loads(s)
            except ValueError:
                continue
            tur = o.get("type")
            if tur == "stream_event":
                ol = o.get("event") or {}
                if ol.get("type") == "content_block_delta" and (ol.get("delta") or {}).get("type") == "text_delta":
                    yazilan += len(ol["delta"].get("text", ""))
                    if ilerleme:
                        ilerleme(yazilan)
            elif tur == "assistant" and not o.get("parent_tool_use_id"):
                metin = "".join(b.get("text", "") for b in (o.get("message") or {}).get("content", [])
                                if b.get("type") == "text")
                if metin:
                    metinler.append(metin)
            elif tur == "result":
                sonuc = o
        if bitti:
            break
        if iptal and iptal():
            p.terminate()
            raise Durduruldu("Durduruldu. Tekrar dene ile bu adım baştan yazılır.")
        if time.time() - baslangic > ZAMAN_ASIMI:
            p.terminate()
            raise ClaudeCodeHatasi(f"Claude Code {ZAMAN_ASIMI // 60} dakikada bitmedi. Tekrar dene.")
    try:
        kod = p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        kod = -9
    time.sleep(0.05)
    return {"kod": kod, "sonuc": sonuc, "metinler": metinler, "stderr": "".join(hata_parcalari)}
