# Kanal Stüdyosu (Windows) · ilk kurulum. Bir kez çalıştırman yeterli. Hiçbir dosyayı silmez.
$App = Split-Path -Parent $PSScriptRoot
$Kok = Split-Path -Parent $App
Write-Host '== Kanal Stüdyosu · ilk kurulum ==' -ForegroundColor Cyan
Write-Host ''
# İnternetten indirilen dosyaların "engellendi" işaretini kaldır (yoksa Windows açarken uyarır)
Get-ChildItem -Path $Kok -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue
Write-Host '✓ Dosyaların indirme engeli kaldırıldı.'

$winget = Get-Command winget.exe -ErrorAction SilentlyContinue
function Kur([string]$kimlik, [string]$ad) {
    if (-not $winget) { Write-Host "  ! winget yok: $ad'ı elle kur." -ForegroundColor Yellow; return }
    Write-Host "  $ad kuruluyor…"
    winget install -e --id $kimlik --accept-source-agreements --accept-package-agreements --silent
}
$pyVar = $false
$py = Get-Command py.exe -ErrorAction SilentlyContinue
if ($py) { & $py.Source -3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>$null; $pyVar = ($LASTEXITCODE -eq 0) }
if (-not $pyVar) { Kur 'Python.Python.3.12' 'Python 3.12' } else { Write-Host '✓ Python kurulu.' }
if (-not (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue)) { Kur 'Gyan.FFmpeg' 'FFmpeg' } else { Write-Host '✓ FFmpeg kurulu.' }
if (-not (Get-Command magick.exe -ErrorAction SilentlyContinue)) { Kur 'ImageMagick.ImageMagick' 'ImageMagick' } else { Write-Host '✓ ImageMagick kurulu.' }

Write-Host ''
if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-Host '✓ Claude Code kurulu. Aboneliğinle giriş yaptığından emin ol: PowerShell''de  claude  yaz, /login.'
} else {
    Write-Host 'Claude Code kurulu değil. Yazım işleri Claude Code aboneliğinle yapılır.' -ForegroundColor Yellow
    $c = Read-Host 'Claude Code şimdi kurulsun mu? (e/h)'
    if ($c -eq 'e' -or $c -eq 'E') {
        Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
        Write-Host 'Kurulduysa yeni bir PowerShell penceresinde  claude  yazıp /login ile aboneliğinle giriş yap.'
    } else {
        Write-Host 'Sonra kurmak için: https://claude.com/claude-code'
    }
}

# Masaüstüne kısayol
try {
    $sh = New-Object -ComObject WScript.Shell
    $lnk = $sh.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Kanal Stüdyosu.lnk'))
    $lnk.TargetPath = 'wscript.exe'
    $lnk.Arguments = '"' + (Join-Path $Kok 'Kanal Stüdyosu.vbs') + '"'
    $lnk.WorkingDirectory = $Kok
    $lnk.Description = 'Kanal Stüdyosu'
    $lnk.Save()
    Write-Host '✓ Masaüstüne "Kanal Stüdyosu" kısayolu kondu.'
} catch { Write-Host '  ! Masaüstü kısayolu oluşturulamadı; kurulum klasöründeki "Kanal Stüdyosu.vbs" ile aç.' -ForegroundColor Yellow }

Write-Host ''
Write-Host 'CapCut: capcut.com adresinden CapCut''ın (İngilizce, uluslararası) masaüstü sürümünü kur ve bir kez açıp kapat.'
Write-Host 'Çin sürümü JianYing (剪映) kullanma: taslak dosyalarını şifreliyor.'
Write-Host ''
Write-Host 'Bitti. Yeni kurulan programların görünmesi için bu pencereyi kapat, sonra masaüstündeki "Kanal Stüdyosu"na çift tıkla.' -ForegroundColor Green
Write-Host 'İlk açılışta uygulama bu klasörde Sistem\ ve Kanallar\ klasörlerini kurar ve kendi kütüphanesini indirir (~1 dk).'
Read-Host 'Kapatmak için Enter'
