# Sahne videoları + montaj planı + odak + SRT  ->  hazır CapCut taslağı
# (hareket/Ken Burns, geçişler, sahne efektleri, kanal stili altyazı: yazı tipi/renk/kutu kanal ayarından).
# İlk sürümün CapCut betiğinden taşındı; iskelet bu klasördedir.
# Kullanım:
#   python3 capcut_taslak.py --video "<.../Uretim/<kod>-...>" --plan 05_Montaj_plani.tsv \
#       --odak odak.json --srt <KOD>_altyazi_<dil>.srt --ad "<KOD>" [--kuru <klasör>]
import json, uuid, copy, os, shutil, sys, time, csv, glob, subprocess, argparse
from ortak import AYAR, CAPCUT, FPS, capcut_kullanici_verisi, win_yolu
ap = argparse.ArgumentParser()
for a in ('--video', '--plan', '--odak', '--srt', '--ad'): ap.add_argument(a, required=True)
ap.add_argument('--kuru', help='CapCut klasörüne yazmadan, bu klasöre üret (deneme)')
A = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = CAPCUT
MAC_ROOT = win_yolu(CAPCUT)  # CapCut'ın kendi kaydına yazılan gerçek yol (Windows'ta C:/Users/... biçiminde)
U = lambda: str(uuid.uuid4()).upper()
TR = {'KARISIM': ('叠化', '6724845717472416269', 600000), 'KARARMA': ('闪黑', '6724239388189921806', 800000),
      'ANI_GIRIS': ('回忆', '6748220149284737550', 800000), 'ANI_CIKIS': ('转场-模糊', '6916426617455645186', 600000),
      'SAYFA': ('翻页', '6747979085894390279', 700000), 'ICERI': ('推近', '6724226861666144779', 500000)}
# EFEKTLER: yalnızca CapCut Global (İngilizce) kimlikleri. Çince/Jianying kimlikleri CapCut Global'de
# çözülmez ve klipte kırmızı hata simgesi çıkar (ilk videolarda yaşandı). Kimlik/yol capcut_efekt_verisi.json'dan gelir;
# yeni efekt gerekirse CapCut'ta bir kez elle ekle, taslaktan verisini bu dosyaya kaydet.
# Efekt ve yazı tipi önbellek yolları şablonun kaydedildiği Mac'in ev klasörüyle yazılı: bu Mac'inkiyle değiştirilir.
_EV_ESKI = '/Users/kullanici'
_MAC_VERI = _EV_ESKI + '/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data'
# Windows: şablondaki Mac CapCut önbellek yolları (efekt, yazı tipi) bu bilgisayarın CapCut\User Data klasörüne çevrilir.
def _ev(t): return t.replace(_MAC_VERI, capcut_kullanici_verisi()).replace(_EV_ESKI, win_yolu(os.path.expanduser('~')))
_EV = json.loads(_ev(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capcut_efekt_verisi.json'), encoding='utf-8').read()))
FX = {'ESKI_FOTO': ('Vintage Grain', [('effects_adjust_speed', 0.0, 1.0, 0.33333333333333), ('effects_adjust_background_animation', 0.0, 1.0, 0.35)]),
      'VINYET': ('Vignette', [('effects_adjust_texture', 0.0, 1.0, 0.45)]),
      'YUMUSAK_ISIK': ('Dreamy Light', [('effects_adjust_intensity', 0.0, 1.0, 0.3)])}
assert all(not any('\u4e00' <= ch <= '\u9fff' for ch in v[0]) and v[0] in _EV for v in FX.values()), 'Efekt adı Global CapCut verisinde yok / Çince'
dur = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
vids = sorted(glob.glob(os.path.join(A.video, 'scene-videos', 'sahne*.mp4')))
plan = {r['sahne']: r for r in csv.DictReader(open(A.plan, encoding='utf-8'), delimiter='\t') if r.get('sahne')}
odak = json.load(open(A.odak))
assert len(vids) == len(plan), f'video {len(vids)} != plan {len(plan)}'
dst = os.path.join(A.kuru or ROOT, A.ad); assert not os.path.exists(dst), 'hedef zaten var: ' + dst
shutil.copytree(os.path.join(HERE, 'capcut_iskelet'), dst)
os.makedirs(os.path.join(dst, 'media'), exist_ok=True)
d = json.load(open(os.path.join(dst, 'draft_info.json'))); tid = d['id']
vt = [t for t in d['tracks'] if t['type'] == 'video'][0]; seg0 = vt['segments'][0]
mats = d['materials']; vm0 = [m for m in mats['videos'] if m['id'] == seg0['material_id']][0]
ph = vm0['path'].split('/media/')[0]
aux0 = {}  # yardımcı malzemeler (hız, tuval, ...)
for k, v in mats.items():
    if isinstance(v, list):
        for x in v:
            if isinstance(x, dict) and x.get('id') in seg0['extra_material_refs']: aux0[k] = x
for k in list(mats.keys()):
    if isinstance(mats[k], list): mats[k] = []
segs = []; t = 0
for i, v in enumerate(vids):
    name = os.path.basename(v); shutil.copy(v, os.path.join(dst, 'media', name))
    nf = int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_packets','-show_entries','stream=nb_read_packets','-of','csv=p=0',v]).decode().strip().strip(','))
    du = nf * 1_000_000 // FPS   # video kare sayısına göre
    vm = copy.deepcopy(vm0); vm.update(id=U(), duration=du, path=f'{ph}/media/{name}', material_name=name); mats['videos'].append(vm)
    s = copy.deepcopy(seg0); s.update(id=U(), material_id=vm['id'], extra_material_refs=[], common_keyframes=[])
    s['source_timerange'] = {'start': 0, 'duration': du}; s['target_timerange'] = {'start': t, 'duration': du}
    for k, x in aux0.items():
        y = copy.deepcopy(x); y['id'] = U(); mats[k].append(y); s['extra_material_refs'].append(y['id'])
    segs.append(s); t += du
vt['segments'] = segs; d['tracks'] = [vt]; d['duration'] = t
clamp = lambda v, a, b: max(a, min(b, v))
def kfl(prop, pts):
    return {"id": U(), "keyframe_list": [{"curveType": "Line", "graphID": "", "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "id": U(), "time_offset": tt, "values": [vv]} for tt, vv in pts], "material_id": "", "property_type": prop}
stats = {}
for i, s in enumerate(segs):
    n = f'{i+1:04d}'; p = plan[n]; D = s['target_timerange']['duration']; sec = D / 1e6
    fx_, fy_ = odak.get(n, [0.5, 0.5]); u, v = 2*fx_ - 1, 1 - 2*fy_
    mv = p['hareket'].strip().upper(); stats[mv] = stats.get(mv, 0) + 1
    z = clamp(0.03 + 0.004*sec, 0.04, 0.12); zp = clamp(0.05 + 0.003*sec, 0.06, 0.12)
    if mv in ('YAKINLAS', 'UZAKLAS', 'NEFES'):
        zz = 0.02 if mv == 'NEFES' else z
        s0, s1 = (1+zz, 1.0) if mv == 'UZAKLAS' else (1.0, 1+zz)
        k = [kfl('KFTypeScaleX', [(0, s0), (D, s1)]), kfl('KFTypePositionX', [(0, u*(1-s0)), (D, u*(1-s1))]), kfl('KFTypePositionY', [(0, v*(1-s0)), (D, v*(1-s1))])]
    elif mv in ('SAGA', 'SOLA', 'ASAGI', 'YUKARI'):
        sc = 1 + zp; a = zp*0.85; ty = clamp(v*(1-sc), -zp, zp); tx = clamp(u*(1-sc), -zp, zp)
        if mv in ('SAGA', 'SOLA'):
            x0, x1 = (a, -a) if mv == 'SAGA' else (-a, a)
            k = [kfl('KFTypeScaleX', [(0, sc), (D, sc)]), kfl('KFTypePositionX', [(0, x0), (D, x1)]), kfl('KFTypePositionY', [(0, ty), (D, ty)])]
        else:
            y0, y1 = (-a, a) if mv == 'ASAGI' else (a, -a)
            k = [kfl('KFTypeScaleX', [(0, sc), (D, sc)]), kfl('KFTypePositionX', [(0, tx), (D, tx)]), kfl('KFTypePositionY', [(0, y0), (D, y1)])]
    else: k = []
    s['uniform_scale'] = {"on": True, "value": 1.0}; s['common_keyframes'] = k
    ef = p['efekt'].strip().upper()
    if ef in FX:
        nm, prm = FX[ef]; ev = _EV[nm]; eid = ev['effect_id']
        m = {"adjust_params": [{"default_value": dv, "max_value": mx, "min_value": mn, "name": pn, "parameterIndex": j, "portIndex": 0, "value": dv} for j, (pn, mn, mx, dv) in enumerate(prm)],
             "apply_target_type": 0, "apply_time_range": None, "category_id": ev["category_id"], "category_name": ev["category_name"], "path": ev["path"], "common_keyframes": [], "disable_effect_faces": [],
             "effect_id": eid, "formula_id": "", "id": U(), "name": nm, "platform": "all", "render_index": 11000, "resource_id": ev["resource_id"],
             "source_platform": ev["source_platform"], "time_range": None, "track_render_index": 0, "type": "video_effect", "value": 1.0, "version": ""}
        mats.setdefault('video_effects', []).append(m); s['extra_material_refs'].append(m['id']); stats['efekt:'+ef] = stats.get('efekt:'+ef, 0) + 1
    g = p['sonraki_gecis'].strip().upper(); stats['gecis:'+g] = stats.get('gecis:'+g, 0) + 1
    if g in TR and i < len(segs) - 1:
        nm, eid, td = TR[g]; td = min(td, int(D*0.4), int(segs[i+1]['target_timerange']['duration']*0.4))
        tr = {"category_id": "", "category_name": "", "duration": td, "effect_id": eid, "id": U(), "is_overlap": True, "name": nm, "platform": "all", "resource_id": eid, "type": "transition"}
        mats.setdefault('transitions', []).append(tr); s['extra_material_refs'].append(tr['id'])
# altyazı (normal metin; Pro istemez) — kanal stili şablondan
S = json.loads(_ev(open(os.path.join(HERE, 'sablon_altyazi.json'), encoding='utf-8').read()))
_AY = AYAR.get('montaj', {}).get('altyazi', {})
def _rgb(h): return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
if _AY:  # kanal stili: yazı rengi, kutu rengi/opaklığı, boyut, yazı tipi
    _m = S['material']; _c = json.loads(_m['content']); _st = _c['styles'][0]
    _m['text_color'] = _AY.get('yazi', _m['text_color']); _st['fill']['content']['solid']['color'] = _rgb(_m['text_color'])
    _m['background_color'] = _AY.get('kutu', _m['background_color']); _m['background_alpha'] = float(_AY.get('kutu_opaklik', _m['background_alpha']))
    _m['font_size'] = _st['size'] = float(_AY.get('boyut', _m['font_size']))
    if _AY.get('yazi_tipi') and _AY['yazi_tipi'] != _m['font_name']:  # CapCut kaynak kimliği yalnız şablondaki yazı tipi için bilinir
        _m['font_name'] = _m['font_title'] = _AY['yazi_tipi']; _m['font_resource_id'] = ''; _st['font'] = {'id': '', 'path': ''}
    _m['content'] = json.dumps(_c, ensure_ascii=False)
def t2us(x):
    h, m_, r = x.split(':'); s_, ms = r.split(','); return ((int(h)*60+int(m_))*60+int(s_))*1_000_000+int(ms)*1000
tsegs = []
for blk in open(A.srt, encoding='utf-8').read().strip().split('\n\n'):
    L = blk.split('\n'); a, b = L[1].split(' --> '); st, en = t2us(a), min(t2us(b), t); txt = '\n'.join(L[2:])
    if en - st < 100000: continue
    m = copy.deepcopy(S['material']); m['id'] = U(); c = json.loads(m['content']); c['text'] = txt; c['styles'][0]['range'] = [0, len(txt)]
    m['content'] = json.dumps(c, ensure_ascii=False)
    an = copy.deepcopy(S['animation']); an['id'] = U()
    sg = copy.deepcopy(S['segment']); sg.update(id=U(), material_id=m['id'], extra_material_refs=[an['id']]); sg['target_timerange'] = {"start": st, "duration": en - st}
    mats.setdefault('texts', []).append(m); mats.setdefault('material_animations', []).append(an); tsegs.append(sg)
tt = copy.deepcopy(S['track']); tt['id'] = U(); tt['segments'] = tsegs; d['tracks'].append(tt)
out = json.dumps(d, ensure_ascii=False)
for f in ['draft_info.json', 'draft_info.json.bak', 'template-2.tmp', f'Timelines/{tid}/draft_info.json', f'Timelines/{tid}/draft_info.json.bak', f'Timelines/{tid}/template-2.tmp']:
    pth = os.path.join(dst, f)
    if os.path.exists(pth): open(pth, 'w', encoding='utf-8').write(out)
# Windows CapCut'ı için aynı içerik draft_content.json adıyla da yazılır (kök ve Timelines/<id>, .bak'larıyla).
for f in ['draft_content.json', 'draft_content.json.bak', f'Timelines/{tid}/draft_content.json', f'Timelines/{tid}/draft_content.json.bak']:
    if os.path.isdir(os.path.dirname(os.path.join(dst, f)) or dst): open(os.path.join(dst, f), 'w', encoding='utf-8').write(out)
# kapak, meta, kayıt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.5', '-i', vids[0], '-frames:v', '1', os.path.join(dst, 'draft_cover.jpg')])
for c_ in glob.glob(os.path.join(dst, 'Timelines', tid, 'draft_cover.jpg')): shutil.copy(os.path.join(dst, 'draft_cover.jpg'), c_)
new_id = U(); now = int(time.time()*1_000_000)
mp = os.path.join(dst, 'draft_meta_info.json'); meta = json.load(open(mp))
dm = [x for x in meta['draft_materials'] if x['type'] == 0][0]; it0 = dm['value'][0]; dm['value'] = []
for v, vm in zip(vids, mats['videos']):
    it = copy.deepcopy(it0); nm = os.path.basename(v)
    it.update(id=str(uuid.uuid4()), duration=vm['duration'], extra_info=nm, file_Path=f'./media/{nm}', create_time=int(time.time()), import_time=int(time.time()), import_time_ms=now)
    it['roughcut_time_range'] = {"duration": vm['duration'], "start": 0}; dm['value'].append(it)
meta.update(draft_id=new_id, draft_name=A.ad, draft_fold_path=f'{MAC_ROOT}/{A.ad}', draft_root_path=MAC_ROOT, tm_duration=t, tm_draft_create=now, tm_draft_modified=now,
            draft_timeline_materials_size_=sum(os.path.getsize(v) for v in vids))
json.dump(meta, open(mp, 'w'), ensure_ascii=False)
pj = os.path.join(dst, 'Timelines/project.json'); pr = json.load(open(pj)); pr['id'] = U(); json.dump(pr, open(pj, 'w'))
if not A.kuru:
    rp = os.path.join(ROOT, 'root_meta_info.json'); shutil.copy(rp, rp + '.claude-yedek')   # tek yedek, her seferinde yenilenir
    r = json.load(open(rp)); e = copy.deepcopy(r['all_draft_store'][0])
    old = e['draft_name']
    for kk, vv in list(e.items()):
        if isinstance(vv, str) and old and old in vv: e[kk] = vv.replace(old, A.ad)
    e.update(draft_id=new_id, draft_name=A.ad, draft_fold_path=f'{MAC_ROOT}/{A.ad}', draft_json_file=f'{MAC_ROOT}/{A.ad}/draft_content.json',
             draft_cover=f'{MAC_ROOT}/{A.ad}/draft_cover.jpg', draft_root_path=MAC_ROOT, tm_duration=t, tm_draft_create=now, tm_draft_modified=now)
    r['all_draft_store'].insert(0, e)
    if isinstance(r.get('draft_ids'), int): r['draft_ids'] += 1
    json.dump(r, open(rp, 'w'), ensure_ascii=False)
print('ok', A.ad, f'{t/1e6:.1f} sn', 'sahne', len(segs), 'altyazi', len(tsegs)); print(json.dumps(stats, ensure_ascii=False))
