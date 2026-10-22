"""Model katmanı. Yazım servisi: Claude Code (abonelik, varsayılan; claude_code.py) ya da OpenRouter.

Claude Code seçiliyse istek claude_code.py'ye gider (ücret abonelikten; maliyet kaydına yalnız tahmini tutar
bilgi olarak yazılır, bütçe sınırı uygulanmaz). Aşağıdaki maddeler OpenRouter (Anthropic Messages biçimi) içindir.
Doğrudan Anthropic API seçeneği 22 Eki 2026'da kaldırıldı; "anthropic" yolu yalnız testlerde sahte istemciyle kullanılır.

- Model, efor, araçlar ve token sınırı iş bazında ayar dosyasından gelir.
- Sistem öneki (proje dosyaları 00–02 + aşama becerisi + uygulama çerçevesi + KANAL AYARLARI) önbelleğe alınır.
- Akış (streaming) ile alınır; ilerleme geri çağrısıyla arayüze karakter sayısı gider.
- Web arama sunucu aracıdır; pause_turn gelirse konuşma otomatik sürdürülür.
- Sonnet/Opus'ta sunucu tarafı yedek model (fallbacks="default") açıktır.
- Geçici hatalarda üstel bekleme: 2, 4, 8, 16, 32 sn.
- Sağlayıcı "openrouter" ise aynı istek OpenRouter'ın Anthropic uyumlu girişine gider: model adı eşlenir,
  sunucu tarafı yedek model (Anthropic'e özgü) gönderilmez; OpenRouter bir alanı kabul etmezse (400) o alan
  çıkarılıp yeniden denenir (sırasıyla efor, web arama) ve kayda yazılır.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Callable

from . import ayarlar as A
from . import kayit
from . import maliyet

YEDEK_BETA = "server-side-fallback-2026-07-01"
BEKLEMELER = (2, 4, 8, 16, 32)
DEVAM_SINIRI = 5


class LLMHatasi(Exception):
    """Kullanıcıya gösterilecek kısa Türkçe mesaj taşır."""


class Reddedildi(LLMHatasi):
    pass


class Durduruldu(LLMHatasi):
    """Kullanıcı Durdur'a bastı."""


@dataclass
class Cevap:
    metin: str
    icerik: list[dict]          # konuşma geçmişine aynen eklenecek asistan blokları (düşünme dahil)
    kullanim: dict
    model: str
    usd: float
    yedek_model: str = ""       # yedek model devreye girdiyse adı
    ek_mesajlar: list[dict] = field(default_factory=list)  # pause_turn ile oluşan ara asistan turları


def _blok_sozluk(b) -> dict:
    return b.model_dump(mode="json", exclude_none=True) if hasattr(b, "model_dump") else dict(b)


def _kullanim(u) -> dict:
    d = {k: getattr(u, k, 0) or 0 for k in
         ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
    stu = getattr(u, "server_tool_use", None)
    d["web_search_requests"] = getattr(stu, "web_search_requests", 0) or 0 if stu else 0
    its = getattr(u, "iterations", None)
    if its:
        d["iterations"] = [_blok_sozluk(i) for i in its]
    return d


def _normal(ad: str) -> str:
    """anthropic/claude-sonnet-5.5 → claude-sonnet-5-5 (OpenRouter adları yedek model sanılmasın)."""
    return re.sub(r"\[.*?\]|:.*$", "", str(ad).split("/", 1)[-1]).replace(".", "-").lower()


def dusunceleri_cikar(mesajlar: list[dict]) -> list[dict]:
    """Asistan turlarındaki düşünme bloklarını ve Claude Code oturum işaretlerini çıkarır. Düşünme imzaları onu
    üreten servise bağlıdır; yazım servisi değişince eski imzalar reddedilebilir. Yazılan metinler aynen kalır."""
    yeni = []
    for m in mesajlar:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            m = dict(m, content=[{k: v for k, v in b.items() if k != "oturum"} for b in m["content"]
                                 if b.get("type") not in ("thinking", "redacted_thinking")]
                     or [{"type": "text", "text": "(boş)"}])
        yeni.append(m)
    return yeni


def _topla(a: dict, b: dict) -> dict:
    s = dict(a)
    for k, v in b.items():
        if k == "iterations":
            s["iterations"] = (s.get("iterations") or []) + v
        else:
            s[k] = s.get(k, 0) + v
    return s


def saglayici() -> str:
    return "openrouter" if A.ayarlar().get("saglayici") == "openrouter" else "claude_code"


SAGLAYICI_ADI = {"anthropic": "Anthropic", "openrouter": "OpenRouter", "claude_code": "Claude Code"}
_YONELME = {"anthropic": "Anthropic'e", "openrouter": "OpenRouter'a", "claude_code": "Claude Code'a"}
# OpenRouter bir alanı reddederse çıkarılacak alanlar (sırayla). Yazım sonucu değişmez; yalnız efor/araştırma etkilenir.
AYIKLANABILIR = ("output_config", "tools")


class LLM:
    def __init__(self, istemci=None, saglayici_: str | None = None):
        self._verilen = istemci          # testler için sabit istemci
        self._sabit = saglayici_
        self._istemciler: dict = {}
        self._ayiklanan: set[str] = set()

    @property
    def saglayici(self) -> str:
        """Ayarlardan her istekte okunur: Ayarlar'da değiştirilirse çalışan üretim de sonraki adımda geçer.
        Sahte istemci verilmişse (testler) Anthropic biçimli yol kullanılır."""
        if self._sabit:
            return self._sabit
        s = saglayici()
        return "anthropic" if self._verilen is not None and s == "claude_code" else s

    @property
    def istemci(self):
        if self._verilen is not None:
            return self._verilen
        if self.saglayici not in self._istemciler:
            import anthropic
            if self.saglayici == "openrouter":
                from . import openrouter
                anahtar = A.anahtar("openrouter")
                if not anahtar:
                    raise LLMHatasi("OpenRouter anahtarı kayıtlı değil. Ayarlar'dan ekle.")
                self._istemciler["openrouter"] = openrouter.istemci(anahtar)
            else:
                raise LLMHatasi("Bu yazım servisi istemci kullanmaz.")
        return self._istemciler[self.saglayici]

    def _gonderim(self, p: dict) -> dict:
        """Uygulama parametreleri → sağlayıcıya giden istek."""
        if self.saglayici != "openrouter":
            return p
        from . import openrouter
        g = {k: v for k, v in p.items() if k not in ("betas", "fallbacks") and k not in self._ayiklanan}
        g["model"] = openrouter.model_eslestir(p["model"])
        return g

    def parametreler(self, is_adi: str, sistem: list[str], mesajlar: list[dict]) -> dict:
        ayar = A.ayarlar()
        isa = ayar["isler"][is_adi]
        mod = ayar["modeller"][isa["model"]]
        onbellek = {"type": "ephemeral"}
        if ayar["onbellek_suresi"] == "1h":
            onbellek["ttl"] = "1h"
        sistem_bloklari = [{"type": "text", "text": t} for t in sistem if t]
        if sistem_bloklari:
            sistem_bloklari[-1]["cache_control"] = onbellek
        # İki önbellek noktası: sabit sistem öneki ve (düzeltme turları için) konuşmanın son bloğu.
        p = {"model": isa["model"], "max_tokens": isa["max_token"], "system": sistem_bloklari,
             "messages": mesajlar, "cache_control": dict(onbellek)}
        if not sistem_bloklari:
            del p["system"]
        if mod["efor"] and isa.get("efor"):
            p["output_config"] = {"effort": isa["efor"]}
        if isa.get("web_arama"):
            p["tools"] = [{"type": "web_search_20260209", "name": "web_search", "max_uses": int(isa["web_arama"])}]
        if mod.get("yedek_model") and self.saglayici == "anthropic":
            p["betas"] = [YEDEK_BETA]
            p["fallbacks"] = "default"
        return p

    def tahmin_usd(self, p: dict) -> float:
        """Çağrıdan önce kaba maliyet: giriş token sayımı (ücretsiz uç nokta) + beklenen çıkış."""
        ayar = A.ayarlar()
        f = ayar["modeller"][p["model"]]
        try:
            if self.saglayici != "anthropic":  # sayım uç noktası Anthropic'e özgü
                raise LookupError("sayım yok")
            sayim = {k: p[k] for k in ("model", "system", "messages", "tools") if k in p}
            giris = self.istemci.beta.messages.count_tokens(**sayim).input_tokens
        except Exception as e:  # sayım başarısızsa karakterden tahmin
            if not isinstance(e, LookupError):
                kayit.yaz(f"Token sayımı yapılamadı ({type(e).__name__}); karakterden tahmin ediliyor", "uyari")
            giris = (len(str(p.get("system", ""))) + len(str(p["messages"]))) // 3
        cikis = min(p["max_tokens"], 16000)
        arama = len(p.get("tools") or []) and p["tools"][0].get("max_uses", 0)
        return (giris * f["giris"] + cikis * f["cikis"]) / 1_000_000 + arama * ayar["web_arama_1000_usd"] / 1000

    def istek(self, is_adi: str, video: str, sistem: list[str], mesajlar: list[dict],
              ilerleme: Callable[[int], None] | None = None, butce_onayli: bool = False,
              iptal: Callable[[], bool] | None = None, tur: str = "ilk") -> Cevap:
        if self.saglayici == "claude_code":
            return self._claude_code(is_adi, video, sistem, mesajlar, ilerleme, iptal, tur)
        p = self.parametreler(is_adi, sistem, mesajlar)
        if not butce_onayli:
            maliyet.butce_kontrol(video, self.tahmin_usd(p))
        model = p["model"]
        kullanim: dict = {}
        ara_turlar: list[dict] = []
        metin_parcalari: list[str] = []
        mesajlar_simdi = list(mesajlar)
        yedek = ""
        for devam in range(DEVAM_SINIRI + 1):
            son = self._akis(dict(p, messages=mesajlar_simdi), ilerleme, sum(map(len, metin_parcalari)), iptal)
            kullanim = _topla(kullanim, _kullanim(son.usage))
            bloklar = [_blok_sozluk(b) for b in son.content]
            metin_parcalari += [b.get("text", "") for b in bloklar if b.get("type") == "text"]
            sunulan = getattr(son, "model", model) or model
            # Yedek model yalnız Anthropic'te var; OpenRouter cevapta "unknown" gibi adlar döndürebiliyor.
            if self.saglayici == "anthropic" and sunulan != model and _normal(sunulan) != model:
                yedek = sunulan
            if son.stop_reason in ("refusal", "max_tokens"):
                # Başarısız cevabın da ücreti ödendi: bütçeye ve maliyet kaydına yazılır.
                ayar = A.ayarlar()
                usd = maliyet.hesapla(kullanim, model, ayar, ayar["onbellek_suresi"])
                maliyet.kaydet(video, is_adi, yedek or model, kullanim, usd, tur, son.stop_reason)
                kayit.yaz(f"{is_adi}: {son.stop_reason} · çıkış {kullanim['output_tokens']} · {usd:.4f} $ (kullanılamadı)",
                          "uyari")
            if son.stop_reason == "refusal":
                raise Reddedildi("Model bu adımı yazmayı reddetti (güvenlik). Konu ya da not yumuşatılarak tekrar denenebilir.")
            if son.stop_reason == "max_tokens":
                raise LLMHatasi(f"Cevap çok uzadı ve {p['max_tokens']:,} token sınırında kesildi; yarım metin kullanılamadığı "
                                "için kaydedilmedi. Harcanan tutar bütçeye yazıldı. Tekrar dene bu adımı baştan yazar.".replace(",", "."))
            if son.stop_reason == "pause_turn" and devam < DEVAM_SINIRI:
                ara_turlar.append({"role": "assistant", "content": bloklar})
                mesajlar_simdi = mesajlar_simdi + [ara_turlar[-1]]
                kayit.yaz(f"{is_adi}: web araması sürüyor, konuşma devam ettiriliyor")
                continue
            ayar = A.ayarlar()
            if "tools" in self._ayiklanan and p.get("tools"):
                kayit.yaz(f"{is_adi}: web araması bu sağlayıcıda çalışmadı; araştırma modelin kendi bilgisiyle yapıldı",
                          "uyari")
            usd = maliyet.hesapla(kullanim, model, ayar, ayar["onbellek_suresi"])
            maliyet.kaydet(video, is_adi, yedek or model, kullanim, usd, tur)
            kayit.yaz(f"{is_adi}: {model}{' → ' + yedek if yedek else ''} · giriş {kullanim['input_tokens']} "
                      f"· önbellek okuma {kullanim['cache_read_input_tokens']} · çıkış {kullanim['output_tokens']} "
                      f"· arama {kullanim['web_search_requests']} · {usd:.4f} $")
            return Cevap("".join(metin_parcalari), bloklar, kullanim, model, usd, yedek, ara_turlar)
        raise LLMHatasi("Web araması çok uzun sürdü; adım tekrar denenebilir.")

    def _claude_code(self, is_adi, video, sistem, mesajlar, ilerleme, iptal, tur) -> Cevap:
        from . import claude_code
        try:
            r = claude_code.istek(is_adi, sistem, mesajlar, ilerleme=ilerleme, iptal=iptal)
        except claude_code.ClaudeCodeHatasi as e:
            raise LLMHatasi(str(e))
        k = r["kullanim"]
        maliyet.kaydet(video, is_adi, r["model"], k, 0.0, tur, abonelik=True, tahmini_usd=r["tahmini_usd"])
        kayit.yaz(f"{is_adi}: Claude Code · {r['model']} · giriş {k['input_tokens']} · önbellek okuma "
                  f"{k['cache_read_input_tokens']} · çıkış {k['output_tokens']} · arama {k['web_search_requests']} "
                  f"· abonelik (API karşılığı ~{r['tahmini_usd']:.2f} $)")
        # Oturum kimliği asistan bloğunda saklanır: düzeltme turunda aynı Claude Code oturumu sürdürülür.
        blok = {"type": "text", "text": r["metin"] or "(boş)", "oturum": r["oturum"]}
        return Cevap(r["metin"], [blok], k, r["model"], 0.0)

    def _akis(self, p: dict, ilerleme, onceki: int, iptal=None):
        import anthropic
        ad, ada = SAGLAYICI_ADI[self.saglayici], _YONELME[self.saglayici]
        beklemeler = list(BEKLEMELER) + [None]
        while beklemeler:
            bekle = beklemeler[0]
            try:
                yazilan = onceki
                with self.istemci.beta.messages.stream(**self._gonderim(p)) as akis:
                    for olay in akis:
                        if iptal and iptal():
                            # Akış kapatılır; o ana kadar yazılan kısmın ücreti sağlayıcıda işlenmiş olur.
                            raise Durduruldu("Durduruldu. Tekrar dene ile bu adım baştan yazılır.")
                        if getattr(olay, "type", "") == "content_block_delta" and \
                                getattr(olay.delta, "type", "") == "text_delta":
                            yazilan += len(olay.delta.text)
                            if ilerleme:
                                ilerleme(yazilan)
                    return akis.get_final_message()
            except anthropic.AuthenticationError:
                raise LLMHatasi(f"{ad} anahtarı geçersiz. Ayarlar'dan yeni anahtar gir.")
            except anthropic.PermissionDeniedError as e:
                kayit.yaz(f"403: {e.message}", "hata")
                raise LLMHatasi(f"{ad} hesabı bu işlem için yetkili değil (kredi ya da izin). Ayrıntı kayıt panelinde.")
            except anthropic.BadRequestError as e:
                kayit.yaz(f"400: {e.message}", "hata")
                kalan = [k for k in AYIKLANABILIR if k in p and k not in self._ayiklanan]
                if self.saglayici == "openrouter" and kalan:
                    self._ayiklanan.add(kalan[0])
                    kayit.yaz(f"OpenRouter '{kalan[0]}' alanını kabul etmedi; o alan olmadan yeniden deneniyor", "uyari")
                    continue
                raise LLMHatasi("İstek kabul edilmedi. Ayrıntı kayıt panelinde.")
            except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
                if bekle is None:
                    raise LLMHatasi(f"{ada} şu an ulaşılamıyor ya da yoğun. Biraz sonra Tekrar dene.")
                kayit.yaz(f"Geçici hata ({type(e).__name__}); {bekle} sn sonra tekrar denenecek", "uyari")
                beklemeler.pop(0)
                time.sleep(bekle)
            except anthropic.APIStatusError as e:
                if e.status_code >= 500 and bekle is not None:
                    kayit.yaz(f"Sunucu hatası {e.status_code}; {bekle} sn sonra tekrar", "uyari")
                    beklemeler.pop(0)
                    time.sleep(bekle)
                    continue
                kayit.yaz(f"API hatası {e.status_code}: {e.message}", "hata")
                if e.status_code == 402:
                    raise LLMHatasi(f"{ad} kredisi yetersiz. Hesabına kredi yükleyip Tekrar dene.")
                raise LLMHatasi(f"{ad} bir hata döndürdü. Ayrıntı kayıt panelinde.")
        raise LLMHatasi(f"{ada} şu an ulaşılamıyor ya da yoğun. Biraz sonra Tekrar dene.")
