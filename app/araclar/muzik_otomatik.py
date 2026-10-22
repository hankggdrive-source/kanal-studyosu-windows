#!/usr/bin/env python3
"""Kanalin Varliklar/Muzik klasorunden RASTGELE ve BIRBIRINDEN FARKLI parcalari, videonun tamamini dolduracak
kadar secip muzik yatagi uretir (22 Eki 2026; onceki surum yalniz 2 parca seciyordu).
 - Parcalar arka arkaya, kendi uzunluklarinca calar; gecislerde 3 sn capraz gecis (muzik_yatagi.py).
 - Ayni parca ancak klasordeki butun parcalar kullanildiktan sonra tekrar eder (art arda ayni parca gelmez).
 - Son parca videonun sonunda kesilir ve kisilarak biter; son ekranda muzik hafifce yukselir.
Kullanim: muzik_otomatik.py <KOD> [--cikis dosya.m4a] [--tohum 7] [--son-sn 8] [--ekle]
 Varsayilan cikis: CapCut taslaginin media/muzik_<KOD>.m4a dosyasi. Seviye kanal ayarindan (montaj.muzik_lufs). Secilen parcalari yazdirir.
 --ekle: yayin_hazirla.py'si zaten calismis (son ekranli) bir taslaga muzigi ekler ya da eski muzik kanalini
         yenisiyle degistirir (CapCut KAPALI olmali; kok + Timelines + .bak birlikte yazilir, eski hali Arsiv'e)."""
import argparse, json, os, random, subprocess, shutil, tempfile
from ortak import AYAR, ARACLAR, PY, kod_al, taslak, arsiv, muzik_parcalari, muzik_olc, taslak_oku, taslak_yolu, taslak_yaz
GECIS = 3.0
p = argparse.ArgumentParser(); p.add_argument('x'); p.add_argument('--cikis'); p.add_argument('--tohum', type=int)
p.add_argument('--son-sn', type=float, default=8.0); p.add_argument('--ekle', action='store_true')
a = p.parse_args()
KOD = kod_al(a.x); DR = taslak(KOD)
cikis = a.cikis or f'{DR}/media/muzik_{KOD}.m4a'

d = taslak_oku(DR)
V = [t for t in d['tracks'] if t['type'] == 'video'][0]['segments']
basl = [s['target_timerange']['start'] / 1e6 for s in V]
# anlatim sonu: son ekran zaten eklenmisse onu anlatima sayma
ses_sonu = d['duration'] / 1e6
mats = {m['id']: m for m in d['materials']['videos']}
if V and mats.get(V[-1]['material_id'], {}).get('path', '').endswith('_son.mp4'):
    ses_sonu = basl[-1]; basl = basl[:-1]
toplam = ses_sonu + a.son_sn
if a.ekle: toplam = d['duration'] / 1e6

parcalar = muzik_parcalari()
assert len(parcalar) >= 1, 'Varliklar/Muzik klasorunde parca yok'
rnd = random.Random(a.tohum)
uzunluk = {}


def kullanilir(f):
    if f not in uzunluk:
        _, b, e = muzik_olc(f)
        uzunluk[f] = e - b
    return uzunluk[f]


def sira():
    """Karisik sira; bitince yeniden karistirilir, art arda ayni parca gelmez."""
    onceki = None
    while True:
        k = parcalar[:]
        rnd.shuffle(k)
        if len(k) > 1 and k[0] == onceki:
            k.append(k.pop(0))
        for f in k:
            onceki = f
            yield f


seg, t, atlanan = [], 0.0, 0
for f in sira():
    pay = max(kullanilir(f) - GECIS - 0.5, 1.0)  # parcanin kendi uzunlugu (gecis payi dusulur)
    if pay < 10 and seg and atlanan < len(parcalar):  # cok kisa parca (ses efekti gibi) dolgu olarak kullanilmaz
        atlanan += 1
        continue
    atlanan = 0
    if t + max(pay, 10) >= toplam or len(seg) > 60:
        seg.append((f, t, toplam))
        break
    seg.append((f, t, t + pay))
    t += pay
dk = lambda x: f'{int(x // 60)}:{int(x % 60):02d}'
print('secilen: ' + ' · '.join(f'{i}) {os.path.basename(f)} ({dk(b)}-{dk(e)})' for i, (f, b, e) in enumerate(seg, 1)))

tmpd = tempfile.mkdtemp(); gecici = os.path.join(tmpd, 'muzik.m4a')
subprocess.run([PY, f'{ARACLAR}/muzik_yatagi.py', gecici, '--toplam', f'{toplam:.2f}', '--son', f'{ses_sonu:.2f}',
                '--hedef', str(AYAR.get('montaj', {}).get('muzik_lufs', -38)),
                *[x for f, b, e in seg for x in ('--parca', f'{f}@{b:.2f}-{e:.2f}')]], check=True)
if os.path.exists(cikis):  # ustune yazmadan once yedek
    os.makedirs(arsiv(KOD), exist_ok=True); shutil.copy(cikis, f'{arsiv(KOD)}/eski_' + os.path.basename(cikis))
shutil.move(gecici, cikis); shutil.rmtree(tmpd, ignore_errors=True)
print('tamam', cikis, f'toplam {toplam:.1f} sn')

if a.ekle:
    import uuid, glob
    U = lambda: str(uuid.uuid4()).upper()
    M = d['materials']
    PH = [m['path'] for m in M['videos'] if '/media/' in m['path']][0].rsplit('/media/', 1)[0] + '/media/'
    eski = [t for t in d['tracks'] if t['type'] == 'audio' and t.get('name') == 'muzik']
    for t in eski:
        ids = {sg['material_id'] for sg in t['segments']}; M['audios'] = [m for m in M['audios'] if m['id'] not in ids]
    d['tracks'] = [t for t in d['tracks'] if t not in eski]
    md = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', cikis], capture_output=True, text=True).stdout)
    aid = U(); sid = U(); spid = U(); AD = min(int(md * 1e6) - 1000, d['duration'])
    M['audios'].append({"app_id": 0, "category_id": "", "category_name": "local", "check_flag": 3, "copyright_limit_type": "none", "duration": int(md * 1e6), "effect_id": "", "formula_id": "", "id": aid, "local_material_id": aid, "music_id": aid, "name": os.path.basename(cikis), "path": PH + os.path.basename(cikis), "source_platform": 0, "type": "extract_music", "wave_points": []})
    M.setdefault('speeds', []).append({"curve_speed": None, "id": spid, "mode": 0, "speed": 1.0, "type": "speed"})
    seg = {"enable_adjust": True, "enable_color_correct_adjust": False, "enable_color_curves": True, "enable_color_match_adjust": False, "enable_color_wheels": True, "enable_lut": True, "enable_smart_color_adjust": False, "last_nonzero_volume": 1.0, "reverse": False, "track_attribute": 0, "track_render_index": 0, "visible": True, "id": sid, "material_id": aid, "target_timerange": {"start": 0, "duration": AD}, "common_keyframes": [], "keyframe_refs": [], "source_timerange": {"start": 0, "duration": AD}, "speed": 1.0, "volume": 1.0, "extra_material_refs": [spid], "clip": None, "hdr_settings": None, "render_index": 0}
    d['tracks'].append({"attribute": 0, "flag": 0, "id": U(), "is_default_name": False, "name": "muzik", "type": "audio", "segments": [seg]})
    X = arsiv(KOD); os.makedirs(X, exist_ok=True)
    shutil.copy(taslak_yolu(DR), f'{X}/draft_info_muzik_oncesi.json')
    taslak_yaz(DR, d)  # draft_info.json ve draft_content.json, kök + Timelines, .bak'larıyla
    print('taslaga eklendi:', 'eski muzik degistirildi' if eski else 'yeni muzik kanali')
