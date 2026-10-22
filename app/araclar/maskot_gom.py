#!/usr/bin/env python3
"""Sahne videosuna CapCut hareketini (olcek/konum anahtar kareleri) ve maskotu gomer.
Kullanim: maskot_gom.py sahne.mp4 maskot_seffaf.mov cikis.mp4 --basla 1.0 --kf "t0,s0,x0,y0;t1,s1,x1,y1"
kf: CapCut degerleri (olcek, konum x/y yarim-tuval birimi, y yukari +). Sonuc tasta hareketsiz kullanilir."""
import sys, subprocess, argparse
from PIL import Image
p=argparse.ArgumentParser(); p.add_argument('sahne'); p.add_argument('maskot'); p.add_argument('cikis')
p.add_argument('--basla',type=float,default=1.0); p.add_argument('--kf',required=True)
p.add_argument('--olcek',type=float,default=0.42); p.add_argument('--mx',type=float,default=-0.836); p.add_argument('--my',type=float,default=-0.58)
p.add_argument('--fade',type=float,default=0.3)
a=p.parse_args()
W,H,F=1920,1080,30
kf=[tuple(map(float,x.split(','))) for x in a.kf.split(';')]
def lerp(t,i):
    if t<=kf[0][0]: return kf[0][i]
    if t>=kf[-1][0]: return kf[-1][i]
    for (t0,*v0),(t1,*v1) in zip(kf,kf[1:]):
        if t0<=t<=t1: r=(t-t0)/(t1-t0); return v0[i-1]+(v1[i-1]-v0[i-1])*r
# maskot kareleri
mw,mh=720,1280
raw=subprocess.run(['ffmpeg','-v','error','-i',a.maskot,'-f','rawvideo','-pix_fmt','rgba','-'],capture_output=True).stdout
n=len(raw)//(mw*mh*4); mfps=24.0; mdur=n/mfps
th=H*a.olcek; tw=th*mw/mh; cx=W/2+a.mx*W/2; cy=H/2-a.my*H/2
mk=[Image.frombytes('RGBA',(mw,mh),raw[i*mw*mh*4:(i+1)*mw*mh*4]).resize((round(tw),round(th)),Image.LANCZOS) for i in range(n)]
ox,oy=round(cx-tw/2),round(cy-th/2)
dec=subprocess.Popen(['ffmpeg','-v','error','-i',a.sahne,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(F),'-i','-','-i',a.sahne,'-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-shortest',a.cikis],stdin=subprocess.PIPE)
fb=W*H*3; k=0
while True:
    b=dec.stdout.read(fb)
    if len(b)<fb: break
    t=k/F; im=Image.frombytes('RGB',(W,H),b)
    s=lerp(t,1); tx=lerp(t,2)*W/2; ty=-lerp(t,3)*H/2
    c=W/2; d=H/2
    # cikis=S*(giris-merkez)+merkez+T  => giris=(cikis-merkez-T)/S+merkez
    im=im.transform((W,H),Image.AFFINE,(1/s,0,c-(c+tx)/s,0,1/s,d-(d+ty)/s),resample=Image.BICUBIC)
    mt=t-a.basla
    if 0<=mt<mdur:
        m=mk[min(int(mt*mfps),n-1)]
        al=min(1,mt/a.fade,(mdur-mt)/a.fade)
        if al<1:
            r,g,bb,aa=m.split(); aa=aa.point(lambda v:int(v*al)); m=Image.merge('RGBA',(r,g,bb,aa))
        im.paste(m,(ox,oy),m)
    enc.stdin.write(im.tobytes()); k+=1
enc.stdin.close(); enc.wait(); print('kare',k)
