# Sahne metni + ses süreleri + ses içindeki duraklamalardan senkron SRT üretir.
import re, subprocess, sys, glob, os
VID, TXT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MAXC = 84  # iki satır x 42 karakter
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
def pauses(f):
    o = subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','silencedetect=n=-40dB:d=0.18','-f','null','-'],capture_output=True,text=True).stderr
    s=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; e=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
    return [((a+b)/2,a,b) for a,b in zip(s,e)]
def wrap(t):
    if len(t)<=42: return t
    if len(t)>92:
        w=t.split(); n=len(w); a=' '.join(w[:n//3]); b=' '.join(w[n//3:2*n//3]); c=' '.join(w[2*n//3:]); return a+'\n'+b+'\n'+c
    w=t.split(); best=None
    for i in range(1,len(w)):
        a,b=' '.join(w[:i]),' '.join(w[i:]); m=max(len(a),len(b))
        if best is None or m<best[0]: best=(m,a+'\n'+b)
    return best[1]
def chunks(sent):
    if len(sent)<=MAXC: return [sent]
    # önce virgül/iki nokta, sonra kelime
    parts=re.split(r'(?<=[,:;])\s+',sent); out=[]; cur=''
    for p in parts:
        if len(cur)+len(p)+1<=MAXC: cur=(cur+' '+p).strip()
        else:
            if cur: out.append(cur)
            while len(p)>MAXC:
                w=p.split(); c=''
                while w and len(c)+len(w[0])+1<=MAXC: c=(c+' '+w.pop(0)).strip()
                out.append(c); p=' '.join(w)
            cur=p
    if cur: out.append(cur)
    return out
paras=[p.strip() for p in open(TXT,encoding='utf-8').read().split('\n\n') if p.strip()]
vids=sorted(glob.glob(os.path.join(VID,'scene-videos','sahne*.mp4')))
auds=sorted(glob.glob(os.path.join(VID,'audio','sahne*.mp3')))
assert len(paras)==len(vids)==len(auds), (len(paras),len(vids),len(auds))
def ts(x):
    ms=int(round(x*1000)); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000); return f'{h:02}:{m:02}:{s:02},{ms:03}'
cues=[]; t0=0.0
for para,v,a in zip(paras,vids,auds):
    text=re.sub(r'\[[a-z ]+\]\s*','',para).strip()
    ad=dur(a); vd=dur(v); ps=[p for p in pauses(a) if 0.15<p[0]<ad-0.15]
    # konuşmanın gerçek bitişi (sondaki sessizlik hariç)
    tail=[p for p in pauses(a) if p[2]>=ad-0.05]; end=tail[0][1] if tail else ad
    sents=[s for s in re.split(r'(?<=[.!?…»])\s+(?=[«A-ZÀ-ÝÀ-ſ])',text) if s]
    pieces=[]; 
    for s in sents:
        for c in chunks(s): pieces.append(c)
    L=sum(len(p) for p in pieces); acc=0; bounds=[0.0]
    for p in pieces[:-1]:
        acc+=len(p); est=end*acc/L
        # en yakın duraklamaya yapıştır (±0.8 sn)
        near=[q for q in ps if abs(q[0]-est)<0.8 and q[0]>bounds[-1]+0.4]
        bounds.append(min(near,key=lambda q:abs(q[0]-est))[0] if near else est)
    bounds.append(end)
    # çok kısa kalan satırları (<0,9 sn) komşusuyla birleştir
    segs=[[bounds[i],bounds[i+1],p] for i,p in enumerate(pieces)]
    changed=True
    while changed and len(segs)>1:
        changed=False
        for i,(a_,b_,p) in enumerate(segs):
            if b_-a_<0.9:
                j=i-1 if i>0 else i+1
                if i>0 and i+1<len(segs) and len(segs[i+1][2])<len(segs[i-1][2]): j=i+1
                lo,hi=min(i,j),max(i,j)
                segs[lo]=[segs[lo][0],segs[hi][1],segs[lo][2]+' '+segs[hi][2]]; del segs[hi]; changed=True; break
    for i,(a_,b_,p) in enumerate(segs):
        st=t0+a_; en=t0+b_
        if i+1<len(segs): en-=0.05
        cues.append((st,en,wrap(p) if len(p)<=MAXC+10 else wrap(p)))
    t0+=vd
with open(OUT,'w',encoding='utf-8') as f:
    for i,(s,e,t) in enumerate(cues,1): f.write(f'{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n')
print('cues',len(cues),'toplam',ts(t0))
