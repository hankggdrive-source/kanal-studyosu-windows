#!/usr/bin/env python3
"""Kullanim: odak_izgara.py "<video klasoru>" "<cikti klasoru>"
Her gorsele 3x3 izgara + sahne numarasi cizer, 12'lik kontak sayfalari (sayfa0.jpg ...) uretir.
(Mac surumundeki odak_izgara.sh'in Windows karsiligi; ImageMagick 7'de komut 'magick', 6'da convert/montage.)"""
import glob, os, shutil, subprocess, sys


def im(alt):
    """ImageMagick komutu: 'magick' varsa onunla (Windows), yoksa eski adlar (convert/montage)."""
    m = shutil.which('magick')
    if m:
        return [m] if alt == 'convert' else [m, alt]
    if sys.platform == 'win32':  # Windows'un kendi convert.exe'si (disk dönüştürücü) asla çağrılmaz
        sys.exit("ImageMagick (magick) bulunamadı. '1 - Ilk kurulum.cmd' dosyasını çalıştır.")
    return [shutil.which(alt) or alt]


GIZLI = {'creationflags': 0x08000000} if sys.platform == 'win32' else {}
V, O = sys.argv[1], sys.argv[2]
os.makedirs(O, exist_ok=True)
gorseller = sorted(glob.glob(os.path.join(V, 'visuals', 'sahne*.jpg')))
if not gorseller:
    sys.exit(f'{V}/visuals icinde sahne*.jpg yok')
for f in gorseller:
    n = os.path.basename(f)[5:9]
    subprocess.run(im('convert') + [f, '-resize', '480x268', '-stroke', '#ff3366', '-strokewidth', '1', '-fill', 'none',
                                    '-draw', 'line 160,0 160,268', '-draw', 'line 320,0 320,268',
                                    '-draw', 'line 0,89 480,89', '-draw', 'line 0,178 480,178',
                                    '-gravity', 'south', '-fill', 'yellow', '-undercolor', '#000a', '-pointsize', '22',
                                    '-annotate', '+0+4', n, os.path.join(O, f't{n}.jpg')], check=True, **GIZLI)
kucukler = sorted(glob.glob(os.path.join(O, 't*.jpg')))
for k, i in enumerate(range(0, len(kucukler), 12)):
    subprocess.run(im('montage') + kucukler[i:i + 12] + ['-tile', '3x', '-geometry', '+3+3', os.path.join(O, f'sayfa{k}.jpg')],
                   check=True, **GIZLI)
for s in sorted(glob.glob(os.path.join(O, 'sayfa*.jpg'))):
    print(s)
