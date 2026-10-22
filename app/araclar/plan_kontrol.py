# Kullanim: python3 plan_kontrol.py 05_Montaj_plani.tsv <sahne_sayisi>
# Montaj planinin kurallarini denetler (maskot sirasi kanal ayarindan; KES %65-75, KARARMA sadece bolum degisiminde, KES ile zit hareket yok, ayni hareket 3x yok, kodlar sozlukte).
import sys,csv
from ortak import AYAR
SIRA=[x.strip().upper() for x in AYAR.get('montaj',{}).get('maskot',{}).get('sira',[])]
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8'),delimiter='\t'))
n=int(sys.argv[2]); err=[]
if len(rows)!=n: err.append(f"satir {len(rows)}!={n}")
H={'YAKINLAS','UZAKLAS','SAGA','SOLA','ASAGI','YUKARI','NEFES','SABIT'}
G={'KES','KARISIM','KARARMA','ANI_GIRIS','ANI_CIKIS','SAYFA','ICERI','-'}
E={'-','ESKI_FOTO','VINYET','YUMUSAK_ISIK'}
opp={('YAKINLAS','UZAKLAS'),('SAGA','SOLA'),('ASAGI','YUKARI')}
g=[r['sonraki_gecis'] for r in rows[:-1]]
print('KES %',round(100*g.count('KES')/len(g),1))
for i,r in enumerate(rows):
    if r['hareket'] not in H: err.append(f"{r['sahne']} hareket {r['hareket']}")
    if r['sonraki_gecis'] not in G: err.append(f"{r['sahne']} gecis {r['sonraki_gecis']}")
    if r['efekt'] not in E: err.append(f"{r['sahne']} efekt {r['efekt']}")
    if int(r['sahne'])!=i+1: err.append(f"sira {r['sahne']}")
    if i+1<len(rows):
        s=rows[i+1]
        if r['sonraki_gecis']=='KARARMA' and r['bolum']==s['bolum']: err.append(f"{r['sahne']} KARARMA bolum icinde")
        if r['sonraki_gecis']=='KES' and ((r['hareket'],s['hareket']) in opp or (s['hareket'],r['hareket']) in opp): err.append(f"{r['sahne']}->{s['sahne']} zit hareket KES")
    if i>=2 and rows[i-2]['hareket']==rows[i-1]['hareket']==r['hareket']: err.append(f"{r['sahne']} 3x {r['hareket']}")
if rows and 'maskot' in rows[0]:
    M=[(r['sahne'],r['maskot'].strip().upper()) for r in rows if r.get('maskot','-').strip() not in ('-','')]
    if [m for _,m in M]!=SIRA: err.append(f"maskot sirasi {M} (beklenen {','.join(SIRA) or 'maskot yok'})")
    for sh,m in M:
        r=rows[int(sh)-1]
        if r['hareket'] not in ('NEFES','YAKINLAS'): err.append(f"{sh} maskot sahnesi hareketi {r['hareket']}")
        if r['rol'] in ('guvenlik','cta'): err.append(f"{sh} maskot sahnesi rolu {r['rol']}")
    print('yayin_hazirla maskot:',' '.join(f"--maskot {int(sh)}:{m[1]}:2" for sh,m in M))
print('HATA' if err else 'TEMIZ', err)
