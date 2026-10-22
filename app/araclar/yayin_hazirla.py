#!/usr/bin/env python3
"""CapCut taslagina yayin oncesi son dokunuslar (CapCut KAPALI olmali):
 - secilen sahnelere maskot gomer (maskot_gom.py), o sahnelerin anahtar karelerini siler
 - son sahnenin son karesiyle 8 sn son ekran (hafif yakinlasma, altyazisiz)
 - altyazilari y=-0.68'e alir
 - muzik yatagini (media/muzik_<KOD>.m4a) ses kanalina ekler. Dosya yoksa muzik_otomatik.py
   Varliklar/Muzik'ten RASTGELE 2 parca secip uretir. --muziksiz ile muzik eklenmez.
Kullanim: yayin_hazirla.py <KOD> --maskot 7:1:2 --maskot 20:2:2 ...   (sahne:maskotNo:baslangicSn)"""
import json, uuid, copy, sys, os, subprocess, argparse, tempfile
from ortak import kod_al, taslak, arsiv, maskot_dosyasi, ARACLAR, CAPCUT, PY, taslak_oku, taslak_yolu, taslak_yaz
p=argparse.ArgumentParser(); p.add_argument('x'); p.add_argument('--maskot',action='append',default=[]); p.add_argument('--son-sn',type=float,default=8.0); p.add_argument('--muziksiz',action='store_true'); p.add_argument('--tohum')
a=p.parse_args()
KOD=kod_al(a.x); DR=taslak(KOD); MD=f'{DR}/media'
U=lambda: str(uuid.uuid4()).upper()
d=taslak_oku(DR); M=d['materials']
PH=[m['path'] for m in M['videos'] if 'placeholder' in m['path']][0].rsplit('/media/',1)[0]+'/media/'
idx={x.get('id'):k for k,v in M.items() if isinstance(v,list) for x in v}
getm=lambda i:[x for x in M[idx[i]] if x['id']==i][0]
V=[t for t in d['tracks'] if t['type']=='video'][0]; S=V['segments']
T=[t for t in d['tracks'] if t['type']=='text'][0]
assert not any(t['type']=='audio' for t in d['tracks']), 'zaten muzik var'
voice_end=d['duration']
def vmat(tmpl,name,dur):
    m=copy.deepcopy(tmpl); m['id']=U(); m['path']=PH+name; m['material_name']=name; m['duration']=dur; m['local_material_id']=str(uuid.uuid4()); M['videos'].append(m); return m
def kfval(seg,prop,t,default):
    for k in seg['common_keyframes']:
        if k['property_type']==prop:
            L=sorted((x['time_offset']/1e6,x['values'][0]) for x in k['keyframe_list'])
            if t<=L[0][0]: return L[0][1]
            if t>=L[-1][0]: return L[-1][1]
            for (t0,v0),(t1,v1) in zip(L,L[1:]):
                if t0<=t<=t1: return v0+(v1-v0)*(t-t0)/(t1-t0)
    return default
# 1) maskot
for spec in a.maskot:
    n,mk,bas=spec.split(':'); n=int(n); s=S[n-1]; m=getm(s['material_id'])
    src=f"{MD}/{os.path.basename(m['path'])}"; out=f"{MD}/sahne{n:04d}_maskot.mp4"
    dur=s['target_timerange']['duration']/1e6
    ts=sorted({0.0,dur}|{x['time_offset']/1e6 for k in s['common_keyframes'] for x in k['keyframe_list']})
    c=s['clip']; kf=';'.join(f"{t:.6f},{kfval(s,'KFTypeScaleX',t,c['scale']['x']):.6f},{kfval(s,'KFTypePositionX',t,c['transform']['x']):.6f},{kfval(s,'KFTypePositionY',t,c['transform']['y']):.6f}" for t in ts)
    dur_=lambda f: float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout or 0)
    if not (os.path.exists(out) and abs(dur_(out)-dur_(src))<0.05):  # onceden tam uretildiyse atla
        subprocess.run([PY,f'{ARACLAR}/maskot_gom.py',src,maskot_dosyasi(mk),out,'--basla',bas,'--kf',kf],check=True)
    fd=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout)
    nm=vmat(m,os.path.basename(out),int(round(fd*1e6)))
    s['material_id']=nm['id']; s['common_keyframes']=[]
    s['clip']['scale']={'x':1.0,'y':1.0}; s['clip']['transform']={'x':0.0,'y':0.0}; s['uniform_scale']={'on':True,'value':1.0}
    print('maskot', n, 'kf', kf)
# 2) son ekran
last=S[-1]; lm=getm(last['material_id']); lsrc=f"{MD}/{os.path.basename(lm['path'])}"
son=f"{MD}/{os.path.splitext(os.path.basename(lm['path']))[0]}_son.mp4"
TMP=tempfile.mkdtemp(); SP=os.path.join(TMP,'son.png')  # oturuma ozel gecici klasor (ortak /tmp cakismasi olmaz)
subprocess.run(f'ffmpeg -v error -y -sseof -0.1 -i "{lsrc}" -frames:v 1 -update 1 "{SP}" && ffmpeg -v error -y -loop 1 -framerate 30 -i "{SP}" -f lavfi -i anullsrc=r=44100:cl=stereo -t {a.son_sn} -c:v libx264 -pix_fmt yuv420p -crf 16 -r 30 -c:a aac -shortest "{son}"',shell=True,check=True)
e=copy.deepcopy(last); e['id']=U(); SD=int(a.son_sn*1e6)
em=vmat(lm,os.path.basename(son),SD)
e['material_id']=em['id']; e['target_timerange']={'start':voice_end,'duration':SD}; e['source_timerange']={'start':0,'duration':SD}
refs=[]
for r in last['extra_material_refs']:
    k=idx[r]
    if k in ('video_effects','transitions','material_animations'): continue
    mm=copy.deepcopy(getm(r)); mm['id']=U(); M[k].append(mm); refs.append(mm['id'])
e['extra_material_refs']=refs
# son ekran, son sahnenin bittigi olcekten baslar
es=kfval(last,'KFTypeScaleX',last['target_timerange']['duration']/1e6,last['clip']['scale']['x'])
ex=kfval(last,'KFTypePositionX',9e9,last['clip']['transform']['x']); ey=kfval(last,'KFTypePositionY',9e9,last['clip']['transform']['y'])
def kf(pt,pts): return {"id":U(),"material_id":"","property_type":pt,"keyframe_list":[{"id":U(),"curveType":"Line","time_offset":t,"left_control":{"x":0.0,"y":0.0},"right_control":{"x":0.0,"y":0.0},"values":[v],"string_value":"","graphID":""} for t,v in pts]}
e['clip']['scale']={'x':es,'y':es}; e['clip']['transform']={'x':ex,'y':ey}; e['uniform_scale']={'on':True,'value':1.0}
e['common_keyframes']=[kf('KFTypeScaleX',[(0,es),(SD,es*1.02)]),kf('KFTypePositionX',[(0,ex),(SD,ex)]),kf('KFTypePositionY',[(0,ey),(SD,ey)])]
S.append(e)
# 3) altyazi
for s in T['segments']: s['clip']['transform']['y']=-0.68
# 4) muzik
mf=f'{MD}/muzik_{KOD}.m4a'
if not a.muziksiz and not os.path.exists(mf):
    subprocess.run([PY,f'{ARACLAR}/muzik_otomatik.py',KOD]+(['--tohum',a.tohum] if a.tohum else [])+['--son-sn',str(a.son_sn)],check=True)
MUZIK=(not a.muziksiz) and os.path.exists(mf)
if MUZIK:
  md=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',mf],capture_output=True,text=True).stdout)
  aid=U(); sid=U(); spid=U(); AD=min(int(md*1e6)-1000, voice_end+SD)
  M['audios'].append({"app_id":0,"category_id":"","category_name":"local","check_flag":3,"copyright_limit_type":"none","duration":int(md*1e6),"effect_id":"","formula_id":"","id":aid,"local_material_id":aid,"music_id":aid,"name":os.path.basename(mf),"path":PH+os.path.basename(mf),"source_platform":0,"type":"extract_music","wave_points":[]})
  M['speeds'].append({"curve_speed":None,"id":spid,"mode":0,"speed":1.0,"type":"speed"})
  seg={"enable_adjust":True,"enable_color_correct_adjust":False,"enable_color_curves":True,"enable_color_match_adjust":False,"enable_color_wheels":True,"enable_lut":True,"enable_smart_color_adjust":False,"last_nonzero_volume":1.0,"reverse":False,"track_attribute":0,"track_render_index":0,"visible":True,"id":sid,"material_id":aid,"target_timerange":{"start":0,"duration":AD},"common_keyframes":[],"keyframe_refs":[],"source_timerange":{"start":0,"duration":AD},"speed":1.0,"volume":1.0,"extra_material_refs":[spid],"clip":None,"hdr_settings":None,"render_index":0}
  d['tracks'].append({"attribute":0,"flag":0,"id":U(),"is_default_name":False,"name":"muzik","type":"audio","segments":[seg]})
d['duration']=voice_end+SD
os.makedirs(arsiv(KOD),exist_ok=True)
import shutil; shutil.copy(taslak_yolu(DR),f'{arsiv(KOD)}/draft_info_yayin_oncesi.json')
import glob as _g  # CapCut taslağı Timelines/<id>/draft_info.json'dan açar: hepsini birlikte yaz
taslak_yaz(DR, d)  # draft_info.json ve draft_content.json, kök + Timelines, .bak'larıyla
for f in (f'{DR}/draft_meta_info.json',):
    m=json.load(open(f)); m['tm_duration']=d['duration']; json.dump(m,open(f,'w'),ensure_ascii=False)
r=json.load(open(f'{CAPCUT}/root_meta_info.json'))
for x in r['all_draft_store']:
    if x.get('draft_name')==KOD: x['tm_duration']=d['duration']
json.dump(r,open(f'{CAPCUT}/root_meta_info.json','w'),ensure_ascii=False)
print('tamam', len(S), 'sahne, sure', d['duration']/1e6, '| muzik:', 'var' if MUZIK else 'YOK')
