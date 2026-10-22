# Kullanim: python3 senk_kontrol.py <KOD>        (ör. BK-04)
#           python3 senk_kontrol.py <KOD> --metin  (ayrica paragraflari listeler: gorsel-cumle kontrolu icin)
# Salt okunur. Kontrol eder: senaryo paragrafi = Pipeline'in seslendirdigi metin; gorsel/ses/sahne videosu
# dosya sirasi; sahne videosu = ses + ~0.35 sn; kanal video olcusu + ses; CapCut taslagi (<KOD>) sira ve sure;
# her altyazi kendi sahnesinin icinde ve o sahnenin cumlesinden; konusma hizi sapmalari; ses seviyesi/uzun sessizlik.
import json,re,sys,subprocess,os,glob
from ortak import kod_al, uretim, video, taslak, altyazi, GEN, YUK, taslak_yolu
kod=kod_al(sys.argv[1]); V=uretim(kod)
D=video(kod); DR=taslak_yolu(taslak(kod))
par=lambda f:[x.strip() for x in re.split(r'\n\s*\n',open(f,encoding='utf-8').read().strip()) if x.strip()]
P=par(f'{D}/02_ElevenLabs_seslendirme_metni.txt'); Q=par(f'{D}/03_Gorsel_promptlari.txt')
vj=json.load(open(f'{V}/video.json'))['scenes']; dr=json.load(open(DR))
clean=lambda s:re.sub(r'\[[a-z ]+\]\s*','',s).strip(); norm=lambda s:re.sub(r'[^\w]','',s.lower())
def probe(f): return json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',f],capture_output=True,text=True).stdout)
iss=[]; print(f'{kod}: paragraf {len(P)} · prompt {len(Q)} · Pipeline sahne {len(vj)}')
if not len(P)==len(Q)==len(vj): iss.append('SAYILAR ESIT DEGIL')
vt=[t for t in dr['tracks'] if t['type']=='video'][0]['segments']; mats={m['id']:m for m in dr['materials']['videos']}

if len(vt)==len(vj)+1 and '_son.mp4' in {m['id']:m for m in dr['materials']['videos']}[vt[-1]['material_id']]['path']: print('son ekran var: %.1f sn' % (vt[-1]['target_timerange']['duration']/1e6))
elif len(vt)!=len(vj): iss.append(f'taslakta {len(vt)} sahne var')
t0=0; rows=[]
for i,s in enumerate(vj):
    num=f'{i+1:04d}'
    if clean(s['text'])!=clean(P[i]): iss.append(f'{num} METIN FARKLI: Pipeline="{s["text"][:60]}" / dosya="{P[i][:60]}"')
    for k,exp in (('media_file',f'visuals/sahne{num}.jpg'),('audio_file',f'audio/sahne{num}.mp3'),('video_file',f'scene-videos/sahne{num}.mp4')):
        if s[k]!=exp: iss.append(f'{num} {k}={s[k]}')
    a=float(probe(f'{V}/audio/sahne{num}.mp3')['format']['duration']); v=probe(f'{V}/scene-videos/sahne{num}.mp4'); vd=float(v['format']['duration'])
    st=[x for x in v['streams'] if x['codec_type']=='video'][0]
    if not (0.2<vd-a<0.5): iss.append(f'{num} ses {a:.2f} sn / sahne videosu {vd:.2f} sn')
    if (st['width'],st['height'])!=(GEN,YUK): iss.append(f'{num} boyut {st["width"]}x{st["height"]}')
    if not any(x['codec_type']=='audio' for x in v['streams']): iss.append(f'{num} sahne videosunda ses yok')
    seg=vt[i]; m=mats[seg['material_id']]
    if not (m['path'].endswith(f'sahne{num}.mp4') or m['path'].endswith(f'sahne{num}_maskot.mp4')): iss.append(f'{num} taslakta yanlis dosya {m["path"][-20:]}')
    st0=seg['target_timerange']['start']/1e6; du=seg['target_timerange']['duration']/1e6
    if abs(st0-t0)>0.05: iss.append(f'{num} taslakta bosluk/ust uste: {st0:.2f} (beklenen {t0:.2f})')
    rows.append((num,st0,du,a,len(clean(P[i]).split()))); t0+=du
rates=sorted(r[4]/r[3] for r in rows); med=rates[len(rates)//2]
for r in rows:
    if r[4]/r[3]<med*0.6 or r[4]/r[3]>med*1.5: iss.append(f'{r[0]} konusma hizi farkli: {r[4]} kelime / {r[3]:.1f} sn (orta {med:.2f} k/sn) - dinle')
def ts(x):h,m,s=x.split(':');return int(h)*3600+int(m)*60+float(s.replace(',','.'))
srt=open(altyazi(kod),encoding='utf-8').read().strip().split('\n\n'); B=[(r[1],r[1]+r[2]) for r in rows]
for b in srt:
    L=b.split('\n'); a,e=[ts(x) for x in L[1].split(' --> ')]; txt=' '.join(L[2:]); mid=(a+e)/2
    k=next((j for j,(x,y) in enumerate(B) if x<=mid<y+0.001),len(B)-1)
    if norm(txt) not in norm(clean(P[k])):
        w=[j+1 for j in range(max(0,k-2),min(len(P),k+3)) if norm(txt) in norm(clean(P[j]))]; iss.append(f'ALTYAZI {L[1]} "{txt[:50]}" sahne {k+1} zamaninda ama metni sahne {w}')
    if a<B[k][0]-0.05 or e>B[k][1]+0.05: iss.append(f'ALTYAZI {L[1]} sahne {k+1} sinirini asiyor')
tt=[t for t in dr['tracks'] if t['type']=='text'][0]['segments']
if len(tt)!=len(srt): iss.append(f'SRT {len(srt)} satir, taslakta {len(tt)} altyazi')
for r in rows:
    o=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f'{V}/audio/sahne{r[0]}.mp3','-af','silencedetect=n=-40dB:d=1.5,volumedetect','-f','null','-'],capture_output=True,text=True).stderr
    mv=float(re.search(r'mean_volume: ([-\d.]+)',o).group(1)); mx=float(re.search(r'max_volume: ([-\d.]+)',o).group(1)); sl=re.findall(r'silence_duration: ([\d.]+)',o)
    if mv<-26 or mv>-13: iss.append(f'{r[0]} ses seviyesi {mv} dB (normal ~-18)')
    if mx>=0: iss.append(f'{r[0]} ses tepesi {mx} dB (cizirti riski)')
    if sl: iss.append(f'{r[0]} {", ".join(sl)} sn sessizlik (metinde [pause] yoksa dinle)')
print(f'toplam {t0:.1f} sn · SRT {len(srt)} · taslak altyazi {len(tt)}')
print('SONUC: TEMIZ' if not iss else f'SONUC: {len(iss)} not'); print('\n'.join(iss))
if '--metin' in sys.argv:
    for i,p in enumerate(P): print(f'{i+1:04d}',clean(p)[:170])
