#!/usr/bin/env python3
"""Yesil ekranli maskot videosunu seffaf ProRes 4444 .mov yapar (elle kullanilan arac).
Kullanim: maskot_seffaf.py giris.mp4 cikis.mov [0xRRGGBB]   (Mac surumundeki maskot_seffaf.sh'in karsiligi)"""
import subprocess, sys
giris, cikis = sys.argv[1], sys.argv[2]
C = sys.argv[3] if len(sys.argv) > 3 else '0x22E421'
fc = (f"[0]format=gbrap,chromakey={C}:0.14:0.04,split=3[k][m][s];[m]alphaextract,erosion,erosion,boxblur=1:1[al];"
      "[k][al]alphamerge,split[ke][ko];[ke]despill=type=green:mix=0.5:expand=0,format=gbrap[d];"
      "[s]alphaextract,erosion,erosion,erosion,erosion,erosion,erosion,format=gray,scale=flags=neighbor,format=gbrap[mask0];"
      "[ko]format=gbrap[o];[d][o][mask0]maskedmerge=planes=7,format=yuva444p10le")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', giris, '-an', '-filter_complex', fc, '-c:v', 'prores_ks', '-profile:v', '4444',
                '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0', cikis], check=True)
