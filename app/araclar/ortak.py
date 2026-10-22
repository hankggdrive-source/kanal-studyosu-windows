"""Montaj araçlarının ortak yardımcısı: kanal bilgileri Kanal Stüdyosu'nun verdiği ortam değişkenlerinden okunur.

KS_KANAL (kanal klasörü), KS_AYAR (kanal.json), KS_ONEK, KS_URETIM (sahne videolarının kökü), KS_CAPCUT (CapCut
taslak klasörü), KS_ARACLAR (bu klasör), KS_PYTHON. İlk sürümdeki sabit yolların yerine.
"""
import glob
import json
import os
import re

KANAL = os.environ.get('KS_KANAL', '')
ONEK = os.environ.get('KS_ONEK', '')
URETIM = os.environ.get('KS_URETIM', '')
CAPCUT = os.environ.get('KS_CAPCUT', '')
ARACLAR = os.environ.get('KS_ARACLAR', os.path.dirname(os.path.abspath(__file__)))
PY = os.environ.get('KS_PYTHON', 'python3')
AYAR = json.load(open(os.environ['KS_AYAR'], encoding='utf-8')) if os.environ.get('KS_AYAR') else {}
DIL = AYAR.get('dil', {}).get('hedef', 'it')
VIDEO = AYAR.get('montaj', {}).get('video', {})
GEN, YUK, FPS = int(VIDEO.get('width', 1920)), int(VIDEO.get('height', 1080)), int(VIDEO.get('fps', 30))


def kod_al(x):
    """'05' ya da 'BK-05' → 'BK-05' (eski kullanım: yalnız numara)."""
    return x if '-' in x else f'{ONEK}-{x.zfill(int(AYAR.get("kod_hane", 2)))}'


def video(kod):
    return f'{KANAL}/Videolar/{kod}'


def arsiv(kod):
    return f'{KANAL}/Arsiv/{kod}'


def taslak(kod):
    return f'{CAPCUT}/{kod}'


def uretim(kod):
    """Sahne videolarının klasörü: Uretim/<kod>-…-<id8>/ (en yenisi)."""
    adaylar = [p for p in glob.glob(f'{URETIM}/*/video.json') if os.path.basename(os.path.dirname(p)).startswith(kod.lower() + '-')]
    if not adaylar:
        raise SystemExit(f'{kod} için üretim klasörü bulunamadı ({URETIM})')
    return os.path.dirname(max(adaylar, key=os.path.getmtime))


def altyazi(kod):
    return f'{video(kod)}/{kod}_altyazi_{DIL}.srt'


def maskot_dosyasi(no):
    """Maskot numarası (1, 2, …) → Varliklar/Maskot içindeki dosya (kanal ayarındaki sırayla)."""
    d = AYAR.get('montaj', {}).get('maskot', {}).get('dosyalar', [])
    return f'{KANAL}/Varliklar/Maskot/{d[int(no) - 1]}'


TAG = re.compile(r'\[[a-z ]+\]\s*')


MUZIK_UZANTI = ('.mp3', '.m4a', '.wav', '.aac', '.flac')


def muzik_parcalari():
    """Kanalın Varliklar/Muzik klasöründeki parçalar (gizli dosyalar hariç)."""
    k = f'{KANAL}/Varliklar/Muzik'
    if not os.path.isdir(k):
        return []
    return sorted(f'{k}/{f}' for f in os.listdir(k) if f.lower().endswith(MUZIK_UZANTI) and not f.startswith('.'))


def muzik_olc(f):
    """→ (LUFS, kullanılan başlangıç, kullanılan bitiş): baştaki sessizlik ve son 15 sn'deki sessizlik atlanır."""
    import subprocess
    o = subprocess.run(['ffmpeg', '-nostats', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    L = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1])
    s = subprocess.run(['ffmpeg', '-i', f, '-af', 'silencedetect=n=-45dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', s)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', s)]
    bas = en[0] if st and st[0] < 0.05 and en else 0.0
    son = d
    for x in st:
        if x > d - 15:
            son = min(son, x)
            break
    return L, bas, son


# --- CapCut taslak dosyaları (Windows) ---------------------------------------------------------
# Mac'te CapCut taslağı draft_info.json'dan açar; Windows CapCut'ının sürüme göre draft_content.json'u da okuduğu
# bildiriliyor. İkisi birlikte (kök + Timelines/<id> + .bak) aynı içerikle yazılır; okurken hangisi varsa o.
TASLAK_ADLARI = ('draft_info.json', 'draft_content.json')


def taslak_yolu(dr):
    for ad in TASLAK_ADLARI:
        if os.path.exists(f'{dr}/{ad}'):
            return f'{dr}/{ad}'
    return f'{dr}/{TASLAK_ADLARI[0]}'


def taslak_oku(dr):
    return json.load(open(taslak_yolu(dr), encoding='utf-8'))


def taslak_dosyalari(dr):
    """Yazılacak bütün kopyalar: kök ve her Timelines/<id> için iki ad ve .bak'ları."""
    klasorler = [dr] + [p for p in glob.glob(f'{dr}/Timelines/*') if os.path.isdir(p)]
    return [f'{k}/{ad}{ek}' for k in klasorler for ad in TASLAK_ADLARI for ek in ('', '.bak')]


def taslak_yaz(dr, d):
    metin = json.dumps(d, ensure_ascii=False)
    for f in taslak_dosyalari(dr):
        with open(f, 'w', encoding='utf-8') as h:
            h.write(metin)


def capcut_kullanici_verisi():
    """CAPCUT = .../CapCut/User Data/Projects/com.lveditor.draft → .../CapCut/User Data (ileri eğik çizgiyle)."""
    k = os.path.realpath(CAPCUT).replace('\\', '/')
    return k.rsplit('/Projects/', 1)[0] if '/Projects/' in k else k


def win_yolu(p):
    return os.path.realpath(p).replace('\\', '/')
