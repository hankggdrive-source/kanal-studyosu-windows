# Kanal Stüdyosu (Windows) başlatıcı. "Kanal Stüdyosu.vbs" bunu gizli pencerede çalıştırır.
# Kurulum klasörü = bu dosyanın iki üstü (app\windows → app → kurulum). Uygulamanın bütün verisi Sistem\ ve Kanallar\'dadır.
# İlk açılışta (ya da ortam bozulduysa) uygulamanın kendi Python ortamını Sistem\.venv'e kurar; sistem Python'una paket kurmaz.
$ErrorActionPreference = 'Continue'
$App = Split-Path -Parent $PSScriptRoot
$Kok = Split-Path -Parent $App
$env:KANAL_STUDYOSU_KOK = $Kok
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$Sistem = Join-Path $Kok 'Sistem'
New-Item -ItemType Directory -Force -Path $Sistem | Out-Null
$Log = Join-Path $Sistem 'kayit.log'
$Venv = Join-Path $Sistem '.venv'
$VPy = Join-Path $Venv 'Scripts\python.exe'
$VPyw = Join-Path $Venv 'Scripts\pythonw.exe'
$Req = Join-Path $App 'requirements.txt'

function Yaz([string]$m, [string]$tur = 'bilgi') {
    Add-Content -Path $Log -Value ("{0} [{1}] {2}" -f (Get-Date -Format 'HH:mm:ss'), $tur, $m) -Encoding UTF8
}
function Uyari([string]$baslik, [string]$mesaj) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show($mesaj, $baslik, 'OK', 'Error') | Out-Null
}
function SonHata {
    if (Test-Path $Log) { (Get-Content $Log -Encoding UTF8 | Where-Object { $_.Trim() } | Select-Object -Last 1) } else { '' }
}
function Calistir([string]$exe, [string]$argumanlar) {
    # Çıktısı kayda eklenir; dönüş: çıkış kodu
    $o = [System.IO.Path]::GetTempFileName(); $e = [System.IO.Path]::GetTempFileName()
    $p = Start-Process -FilePath $exe -ArgumentList $argumanlar -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $o -RedirectStandardError $e
    foreach ($f in @($o, $e)) { Get-Content $f -Encoding UTF8 | Add-Content -Path $Log -Encoding UTF8; Remove-Item $f -ErrorAction SilentlyContinue }
    return $p.ExitCode
}
function PythonBul {
    # Önce py başlatıcısı, sonra PATH'teki python (Microsoft Store kısayolu değil), sonra bilinen klasörler. En az 3.10.
    $kontrol = 'import sys; print(sys.executable) if sys.version_info >= (3, 10) else sys.exit(1)'
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) { $y = & $py.Source -3 -c $kontrol 2>$null; if ($LASTEXITCODE -eq 0 -and $y) { return $y.Trim() } }
    $adaylar = @(Get-Command python.exe -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | ForEach-Object { $_.Source })
    $adaylar += @(Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe", "$env:ProgramFiles\Python3*\python.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | ForEach-Object { $_.FullName })
    foreach ($a in $adaylar) { $y = & $a -c $kontrol 2>$null; if ($LASTEXITCODE -eq 0 -and $y) { return $y.Trim() } }
    return $null
}
function OrtamCalisiyor {
    if (-not (Test-Path $VPy)) { return $false }
    & $VPy -c 'import sys' 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}
function KutuphanelerVar {
    & $VPy -c 'import anthropic, keyring, send2trash, PIL' 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

$Python = PythonBul
if (-not $Python) {
    Uyari 'Python bulunamadı' "Kanal Stüdyosu için Python 3.10 veya üstü gerekir. Kurulum klasöründeki '1 - Ilk kurulum.cmd' dosyasını çalıştır."
    exit 1
}
$imza = (Get-FileHash $Req -Algorithm SHA256).Hash.Substring(0, 16)
$imzaDosyasi = Join-Path $Venv '.gereksinim'
$hazir = (OrtamCalisiyor) -and (Test-Path $imzaDosyasi) -and ((Get-Content $imzaDosyasi -Raw).Trim() -eq $imza) -and (KutuphanelerVar)
if (-not $hazir) {
    Yaz 'Uygulama ortamı kuruluyor (ilk açılış, güncelleme ya da bozulan ortamın onarımı)…'
    if (-not (OrtamCalisiyor)) {
        # Bozuk ya da eski ortam temizlenip yeniden kurulur (--clear: yalnız uygulamanın kendi ortamı)
        if ((Calistir $Python "-m venv --clear `"$Venv`"") -ne 0 -or -not (OrtamCalisiyor)) {
            Uyari 'Kurulum yapılamadı' ("Uygulamanın Python ortamı kurulamadı. Son hata: " + (SonHata) + " — Ayrıntı: Sistem\kayit.log")
            exit 1
        }
    }
    Calistir $VPy '-m pip install --quiet --upgrade pip' | Out-Null
    if ((Calistir $VPy "-m pip install --quiet -r `"$Req`"") -ne 0) {
        Yaz 'Kütüphaneler kurulamadı; uygulama yine açılıyor (Claude Code ile çalışır). Sonraki açılışta yeniden denenecek.' 'uyari'
    } else {
        Set-Content -Path $imzaDosyasi -Value $imza -Encoding ASCII
    }
}
# Sunucu konsolsuz (pythonw) başlar, tarayıcı açılır; uygulama zaten açıksa yeni kopya başlamaz (tek_kopya.py).
Start-Process -FilePath $VPyw -ArgumentList '-m', 'kanal_studyosu' -WorkingDirectory $App
exit 0
