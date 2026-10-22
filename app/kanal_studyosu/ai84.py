"""AI84.pro API istemcisi (yalnız standart kütüphane). Belge: https://api.ai84.pro (kullanıcının verdiği entegrasyon notu).

Kurallar (belgeden):
- Kimlik: `xi-api-key` başlığı. Gövdeli her POST'ta `Content-Type: application/json`.
- Üretim asenkron: POST → job_id; GET ile durum sorgulanır; 'done' olunca audioUrl hemen indirilir.
- İş durumları KAPALI küme: queued, processing, done, failed. Tanınmayan durum bitmemiş sayılır.
- Sorgu 5xx dönerse iş hâlâ sürüyordur: aynı aralıkla sorgulamaya devam edilir.
- POST'ta 429: Retry-After kadar beklenir (dakikada 60 sınırı).
- HTTP 200 işin başarılı olduğu anlamına gelmez; job.status'a bakılır.
- Başarısız iş: errorMessage (gösterilebilir), errorCategory 1 = girdi hatası (tekrar etme),
  2 = geçici (sonra tekrar), errorMessageKey (dala ayırmak için). Başarısız işten ücret alınmaz.
- Ses URL'leri süreli imzalıdır; saklanmaz, hemen indirilir.

Bağlantı, eski Creator Pipeline Studio'da çalıştığı bilinen yolla Mac'in curl programıyla kurulur (belge
örnekleri de curl). Python'un varsayılan kimliği (Python-urllib) sunucu önündeki koruma katmanınca 403 ile
reddedilebiliyor. curl yoksa urllib tarayıcı benzeri bir User-Agent ile kullanılır.
Anahtar komut satırına yazılmaz (ps'te görünmesin): başlıklar 0600 izinli geçici dosyadan okunur.
"""
from __future__ import annotations

import json
import os
import shutil
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TABAN = "https://api.ai84.pro"
KIMLIK = "KanalStudyosu/0.1 (macOS; curl uyumlu)"


def _curl() -> str | None:
    return "/usr/bin/curl" if Path("/usr/bin/curl").exists() else shutil.which("curl")


def _son_basliklar(ham: str) -> dict:
    """curl -D çıktısında (-L ile birden çok yanıt olabilir) son yanıtın başlıkları."""
    bloklar = [b for b in ham.replace("\r\n", "\n").split("\n\n") if b.strip().startswith("HTTP/")]
    bas = {}
    for satir in (bloklar[-1].splitlines()[1:] if bloklar else []):
        if ":" in satir:
            k, v = satir.split(":", 1)
            bas[k.strip()] = v.strip()
    return bas
BITMIS = {"done", "failed"}


class AI84Hatasi(Exception):
    """kategori: 1 = istek hatası (aynen tekrar etme), 2 = geçici, None = bilinmiyor/ağ."""

    def __init__(self, mesaj: str, kategori: int | None = None, anahtar: str = "", http: int | None = None):
        super().__init__(mesaj)
        self.kategori, self.anahtar, self.http = kategori, anahtar, http


def _ssl_baglami():
    try:  # python.org Python'unda sistem sertifikaları olmayabilir; certifi (anthropic ile gelir) varsa kullan
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _json(ham: bytes) -> dict:
    try:
        j = json.loads(ham or b"{}")
        return j if isinstance(j, dict) else {"data": j}
    except ValueError:
        return {}


class AI84:
    def __init__(self, anahtar: str, taban: str = TABAN, bekle=time.sleep):
        self.anahtar, self.taban, self._bekle = anahtar.strip(), taban.rstrip("/"), bekle
        self._ssl = _ssl_baglami() if taban.startswith("https") else None

    # --- HTTP ---
    def _istek(self, yontem: str, yol: str, govde=None, zaman_asimi: int = 60) -> tuple[int, dict, dict]:
        if not self.anahtar:
            raise AI84Hatasi("AI84 anahtarı kayıtlı değil. Ayarlar'dan ekle.", 1)
        veri = json.dumps(govde, ensure_ascii=False).encode() if govde is not None else None
        basliklar = {"xi-api-key": self.anahtar, "Accept": "application/json",
                     **({"Content-Type": "application/json"} if veri is not None else {})}
        if _curl():
            return self._curl_istek(yontem, self.taban + yol, basliklar, veri, zaman_asimi)
        r = urllib.request.Request(self.taban + yol, data=veri, method=yontem, headers={**basliklar, "User-Agent": KIMLIK})
        try:
            with urllib.request.urlopen(r, timeout=zaman_asimi, context=self._ssl) as c:
                return c.status, _json(c.read()), dict(c.headers)
        except urllib.error.HTTPError as e:
            return e.code, _json(e.read()), dict(e.headers or {})
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise AI84Hatasi(f"AI84'e ulaşılamadı ({getattr(e, 'reason', e)}).", 2)

    @staticmethod
    def _curl_istek(yontem, url, basliklar, veri, zaman_asimi) -> tuple[int, dict, dict]:
        with tempfile.TemporaryDirectory() as td:
            hp, cikti, bd = Path(td) / "h", Path(td) / "o", Path(td) / "d"
            hp.write_text("\n".join(f"{k}: {v}" for k, v in basliklar.items()))
            os.chmod(hp, 0o600)
            komut = [_curl(), "-sS", "-L", "--max-time", str(zaman_asimi), "-X", yontem, "-H", "@" + str(hp),
                     "-D", str(bd), "-o", str(cikti), "-w", "%{http_code}", url]
            if veri is not None:
                komut += ["--data-binary", "@-"]
            try:
                q = subprocess.run(komut, input=veri, capture_output=True, timeout=zaman_asimi + 15)
            except subprocess.TimeoutExpired:
                raise AI84Hatasi("AI84 yanıt vermedi (zaman aşımı).", 2)
            if q.returncode:
                raise AI84Hatasi(f"AI84'e ulaşılamadı ({q.stderr.decode(errors='replace').strip()[:200]}).", 2)
            ham = cikti.read_bytes() if cikti.exists() else b""
            bas = _son_basliklar(bd.read_text(errors="replace")) if bd.exists() else {}
            j = _json(ham)
            if not j and ham:
                j = {"_ham": ham[:300].decode(errors="replace")}
            return int(q.stdout or 0), j, bas

    @staticmethod
    def _hata(kod: int, j: dict) -> AI84Hatasi:
        """Sunucunun kendi mesajı her zaman gösterilir (tahmin yürütmeden)."""
        msg = str(j.get("message") or j.get("error") or j.get("detail") or "").strip()
        if not msg and j.get("_ham"):
            ham = j["_ham"].lower()
            msg = ("istek sunucunun güvenlik katmanınca engellendi (Cloudflare)" if "cloudflare" in ham or "<html" in ham
                   else j["_ham"][:120])
        ek = f" Sunucu: {msg}" if msg else ""
        if kod == 401:
            return AI84Hatasi(f"AI84 anahtarı geçersiz ya da süresi dolmuş (HTTP 401).{ek}", 1, http=kod)
        if kod == 403:
            return AI84Hatasi(f"AI84 isteği reddetti (HTTP 403).{ek} Belgeye göre seslendirme ücretli hesap ister; "
                              "anahtarın aktif olduğunu ai84.pro panelinden kontrol et.", 1, http=kod)
        if kod >= 500:
            return AI84Hatasi(f"AI84 geçici bir hata verdi (HTTP {kod}); biraz sonra tekrar dene.", 2, http=kod)
        if kod == 0:
            return AI84Hatasi("AI84'ten yanıt alınamadı.", 2)
        return AI84Hatasi(f"AI84 hatası (HTTP {kod}).{ek}", 1, http=kod)

    # --- uç noktalar ---
    def krediler(self) -> int:
        kod, j, _ = self._istek("GET", "/v1/credits", zaman_asimi=20)
        if kod != 200:
            raise self._hata(kod, j)
        return int(j.get("credits", 0))

    def tts_gonder(self, govde: dict, deneme: int = 4) -> dict:
        """POST /v2/text-to-speech/async → {'job_id', 'credit_cost', …}. 429'da Retry-After kadar bekler."""
        for i in range(deneme):
            kod, j, bas = self._istek("POST", "/v2/text-to-speech/async", govde)
            if kod in (200, 201):
                if not (j.get("job_id") or j.get("task_id")):
                    raise AI84Hatasi("AI84 iş numarası döndürmedi.", 2)
                return j
            if kod == 429 and i + 1 < deneme:
                self._bekle(float(bas.get("Retry-After") or bas.get("retry-after") or 10))
                continue
            raise self._hata(kod, j)
        raise AI84Hatasi("AI84 istek sınırı (429) aşıldı; biraz sonra tekrar dene.", 2, http=429)

    def tts_durum(self, job_id: str) -> dict | None:
        """GET /v2/text-to-speech/async/:id → job sözlüğü; 5xx ya da ağ hatasında None (iş sürüyor sayılır)."""
        try:
            kod, j, _ = self._istek("GET", "/v2/text-to-speech/async/" + urllib.parse.quote(str(job_id), safe=""),
                                    zaman_asimi=45)
        except AI84Hatasi:
            return None
        if kod >= 500:
            return None
        if kod != 200:
            raise self._hata(kod, j)
        return j.get("job", j)

    def tts_bekle(self, job_id: str, sure: int = 600, aralik: float = 3, durum_cb=None) -> dict:
        """Bitene kadar sorgular. done → job; failed → AI84Hatasi (kategori ile); süre dolarsa kategori None."""
        son = time.time() + sure
        while time.time() < son:
            job = self.tts_durum(job_id)
            st = (job or {}).get("status", "")
            if durum_cb and st:
                durum_cb(st)
            if st == "done":
                if not job.get("audioUrl"):
                    raise AI84Hatasi("İş bitti ama ses adresi yok.", 2)
                return job
            if st == "failed":
                raise AI84Hatasi(job.get("errorMessage") or "Seslendirme başarısız.", job.get("errorCategory"),
                                 job.get("errorMessageKey") or "")
            self._bekle(aralik)
        raise AI84Hatasi("10 dakikada tamamlanmadı; AI84 işi hâlâ sürüyor olabilir. Tekrar dene aynı işi "
                         "ücretsiz sorgular.", None)

    def indir(self, url: str, zaman_asimi: int = 120) -> bytes:
        """İmzalı ses adresi: anahtarsız indirilir."""
        if urllib.parse.urlparse(url).scheme not in ("http", "https"):
            raise AI84Hatasi("Geçersiz ses adresi.", 2)
        if _curl():
            try:
                q = subprocess.run([_curl(), "-sS", "-L", "--fail", "--max-time", str(zaman_asimi), url],
                                   capture_output=True, timeout=zaman_asimi + 15)
            except subprocess.TimeoutExpired:
                raise AI84Hatasi("Ses indirilemedi (zaman aşımı).", 2)
            if q.returncode:
                raise AI84Hatasi(f"Ses indirilemedi ({q.stderr.decode(errors='replace').strip()[:200]}).", 2)
            return q.stdout
        try:
            r = urllib.request.Request(url, headers={"User-Agent": KIMLIK})
            with urllib.request.urlopen(r, timeout=zaman_asimi, context=self._ssl if url.startswith("https") else None) as c:
                return c.read()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise AI84Hatasi(f"Ses indirilemedi ({getattr(e, 'reason', e)}).", 2)
