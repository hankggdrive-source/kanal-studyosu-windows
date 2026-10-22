# Kanal Stüdyosu (Windows)

YouTube kanalları için fikirden CapCut taslağına video üretim uygulaması. Her kanal kendi klasöründe, kendi
ayarlarıyla çalışır: konu → araştırma → Türkçe senaryo → hedef dilde senaryo → sahne paketi → paketleme →
görseller (Google Flow) → seslendirme (ElevenLabs, AI84 üzerinden) → sahne videoları → CapCut taslağı.
Yazım işleri Claude Code (Claude aboneliği) ya da OpenRouter ile yapılır.

## İndir ve kur
1. **İndir:** [main.zip](https://github.com/hankggdrive-source/kanal-studyosu-windows/archive/refs/heads/main.zip)
   (GitHub hesabı gerekmez) ya da `git clone https://github.com/hankggdrive-source/kanal-studyosu-windows.git`.
2. Zip'i açmadan önce: sağ tık › Özellikler › "Engellemeyi kaldır". Sonra istediğin yere aç.
3. **KURULUM.txt**'teki adımları izle (kısaca: `1 - Ilk kurulum.cmd`, CapCut'ı kur, masaüstündeki kısayol).
4. Kullanım: **KULLANIM.md**. Bütün teknik tarif ve kodun tamamı tek dosyada: **SPECS.md**.

## Claude ile değiştirmek
Bu klasörde PowerShell aç ve `claude` yaz (Claude Code). Claude, klasördeki **CLAUDE.md** rehberini okuyup sistemi
anlar; ne istediğini Türkçe anlatman yeterli. Adımlar: **Gelistirme.txt**. Her değişiklikten sonra testler:

```powershell
.\Sistem\.venv\Scripts\python.exe -m unittest discover -s tests
```

Kanallarının içeriği (`Kanallar\`) ve ayarların (`Sistem\`) repoya girmez (`.gitignore`). API anahtarları Windows
Kimlik Bilgisi Yöneticisi'nde saklanır, hiçbir dosyaya yazılmaz.
