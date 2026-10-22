# Kullanim: python3 hassas_kelime_kontrol.py <KOD>   (ör. BK-04; eski kullanim: 04)
# Paketleme (04_Paketleme_ve_Veo3.md: baslik, kapak yazisi, aciklama, etiketler) ve metnin ilk 30 sn'sinde (ilk 6 paragraf)
# kanal ayarindaki hassas/klinik kelimeleri (hassas_kelimeler; kok yazilabilir) arar. Liste bossa TEMIZ.
import re,sys,os
from ortak import AYAR, kod_al, video
kod=kod_al(sys.argv[1]); D=video(kod)
L=[k.strip() for k in AYAR.get('hassas_kelimeler',[]) if k.strip()]
K='|'.join(L)
bul=[]
if K:
    pk=open(f'{D}/04_Paketleme_ve_Veo3.md',encoding='utf-8').read().split('\n')
    kes=next((i for i,l in enumerate(pk) if re.search(r'Veo3|VEO3|Veo 3',l) and l.startswith('#') and i>5),len(pk))
    for i,l in enumerate(pk[:kes]):
        if re.search(K,l,re.I) and not l.strip().startswith('>'): bul.append(f'paketleme satir {i+1}: {l.strip()[:140]}')
    P=[x.strip() for x in re.split(r'\n\s*\n',open(f'{D}/02_ElevenLabs_seslendirme_metni.txt',encoding='utf-8').read().strip()) if x.strip()]
    for i,p in enumerate(P[:6]):
        if re.search(K,p,re.I): bul.append(f'metin ilk 30 sn, paragraf {i+1}: {p[:140]}')
print(f'{kod} hassas kelime: '+('TEMIZ' if not bul else f'{len(bul)} bulgu')); print('\n'.join(bul))
