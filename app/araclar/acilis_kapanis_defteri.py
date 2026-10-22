# Kullanim: python3 acilis_kapanis_defteri.py
# Kanalin tum Videolar/<KOD>/02 metinlerinden ACILIS-KAPANIS DEFTERI uretir -> <kanal>/Acilis_Kapanis_Defteri.md
# Kalip sayaclari (kalip_sayaclari: {"etiket": "regex"}) ve imza kanal ayarindan gelir.
import re,glob,os
from ortak import AYAR, KANAL, ONEK, TAG
out=f'{KANAL}/Acilis_Kapanis_Defteri.md'
clean=lambda s:TAG.sub('',s).strip()
KALIP=AYAR.get('kalip_sayaclari',{}) or {}
desen=re.compile(rf'^{re.escape(ONEK)}-\d+$')
kod_=lambda f: os.path.basename(os.path.dirname(f))  # Windows'ta yol ayracı \\ olabilir
V=sorted(f for f in glob.glob(f'{KANAL}/Videolar/*/02_ElevenLabs_seslendirme_metni.txt') if desen.match(kod_(f)))
imza=AYAR.get('imza','')
L=[f'# {AYAR.get("ad","")} — Açılış–Kapanış Defteri','', 'Otomatik üretilir (Kanal Stüdyosu). Her videodan sonra yenilenir.',
'Kural: yeni video bu açılışlara ve kapanışlara BENZEMEZ.'+(f' Tek sabit satır imzadır: *"{imza}"*' if imza else ''),'']
say={k:[] for k in KALIP}
for f in V:
    kod=kod_(f); P=[clean(x) for x in re.split(r'\n\s*\n',open(f,encoding='utf-8').read().strip()) if x.strip()]
    L+= [f'## {kod} ({len(P)} paragraf)','','**Açılış (ilk 4 paragraf):**','']+[f'{i+1}. {p}' for i,p in enumerate(P[:4])]
    L+= ['','**Kapanış (son 3 paragraf):**','']+[f'- {p}' for p in P[-3:]]+['']
    t=' '.join(P)
    for k,r in KALIP.items(): say[k].append((kod,len(re.findall(r,t,re.I))))
if KALIP and V:
    L+=['## Tekrar eden kalıplar (video başına adet)','','| Kalıp | '+' | '.join(kod_(x) for x in V)+' |','|---|'+'---|'*len(V)]
    for k,v in say.items(): L.append(f'| {k} | '+' | '.join(str(c) for _,c in v)+' |')
open(out,'w',encoding='utf-8').write('\n'.join(L)+'\n'); print('yazildi',out,len(V),'video')
