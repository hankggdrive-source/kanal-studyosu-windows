#!/usr/bin/env python3
"""Videoya arka plan muzigi yatagi uretir (seviye, gerekirse dongu, parca gecisleri, son ekran, fade).
Her --parca kendi araliginda calar; gecislerde 3 sn capraz gecis. Parca araligindan kisaysa dongulu tekrarlanir
(22 Eki 2026 duzeltmesi: dongu ayni dosyanin ayri girdileriyle kurulur; asplit + zincirli acrossfade dongu
yerine kisa ses uretiyordu, muzik videonun sonuna yetmiyordu).
Kullanim: muzik_yatagi.py cikis.m4a --toplam 669.2 --son 661.2 --parca "dosya.mp3@0-172" --parca "dosya2.mp3@172-390" ...
 --hedef -38 (konusma altindaki LUFS), --son-kat 1.67 (son ekranda yukseltme), gecis 3 sn."""
import argparse, subprocess, json, re, os, tempfile, math
from ortak import muzik_olc
p=argparse.ArgumentParser(); p.add_argument('cikis'); p.add_argument('--toplam',type=float,required=True)
p.add_argument('--son',type=float,required=True); p.add_argument('--parca',action='append',required=True)
p.add_argument('--hedef',type=float,default=-38.0); p.add_argument('--son-kat',type=float,default=1.67); p.add_argument('--gecis',type=float,default=3.0)
a=p.parse_args()
olc = muzik_olc
tmp=tempfile.mkdtemp(); G=a.gecis
seg=[]
for x in a.parca:
    f,r=x.rsplit('@',1); s,e=map(float,r.split('-')); seg.append((f,s,e))
seg[-1]=(seg[-1][0],seg[-1][1],a.toplam)
# Her dosyanin en uzun kullanildigi sure (gecis paylari dahil): dongu en az bu kadar olmali.
gerek={}
for i,(f,s,e) in enumerate(seg):
    bas_=max(0,s-G/2); son_=min(a.toplam,e+G/2) if i<len(seg)-1 else a.toplam
    gerek[f]=max(gerek.get(f,0),son_-bas_)
dongu={}
for f,_,_ in seg:
    if f in dongu: continue
    L,b,e=olc(f); g=a.hedef-L; uz=max(e-b,4.0)
    n=max(1,math.ceil((gerek[f]+2)/(uz-2)))  # her ek tekrar capraz geciste 2 sn kisalir
    out=os.path.join(tmp,f'd{len(dongu)}.wav')
    ins_=[]; fc=''
    for i in range(n):
        ins_+=['-i',f]; fc+=f"[{i}]atrim={b}:{e},asetpts=PTS-STARTPTS,volume={g}dB[a{i}];"
    prev='a0'
    for i in range(1,n):
        fc+=f"[{prev}][a{i}]acrossfade=d=2[b{i}];"; prev=f'b{i}'
    fc=fc.rstrip(';').rsplit(f'[{prev}]',1)[0]
    subprocess.run(['ffmpeg','-v','error','-y',*ins_,'-filter_complex',fc,'-ar','44100','-ac','2',out],check=True)
    dongu[f]=out; print(os.path.basename(f),f'{L} LUFS -> {g:+.1f} dB, parca {uz:.1f}s'+(f', {n} kez' if n>1 else ''))
# Parcalar arka arkaya capraz gecisle birlestirilir (acrossfade zinciri). Onceki surumdeki adelay + amix,
# yeni FFmpeg surumlerinde (9.x) ikinci parcadan sonrasini sessiz birakiyordu (Windows testinde goruldu, 22 Eki 2026).
parca=[]
for i,(f,s,e) in enumerate(seg):
    bas=max(0,s-G/2); son=min(a.toplam,e+G/2) if i<len(seg)-1 else a.toplam
    parca.append((f,max(son-bas,0.2)))
ins=[];fc=''
for i,(f,L) in enumerate(parca):
    ins+=['-i',dongu[f]]; fc+=f"[{i}]atrim=0:{L:.3f},asetpts=PTS-STARTPTS[p{i}];"
prev='p0'
for i in range(1,len(parca)):
    d=max(0.05,min(G,parca[i-1][1]-0.1,parca[i][1]-0.1))
    fc+=f"[{prev}][p{i}]acrossfade=d={d:.3f}[x{i}];"; prev=f'x{i}'
E_=a.son
fc+=f"[{prev}]apad=whole_dur={a.toplam},atrim=0:{a.toplam},volume='1+{a.son_kat-1}*min(max((t-({E_}-0.5))/1.5,0),1)':eval=frame,afade=t=in:d=2,afade=t=out:st={a.toplam-3}:d=3"
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',fc,'-c:a','aac','-b:a','256k','-ar','44100',a.cikis],check=True)
print('tamam',a.cikis)
