Param(
    [string]$Input,
    [string]$Output
)

# Sanal ortamı etkinleştir
$venv = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    & $venv
} else {
    Write-Host "Sanal ortam bulunamadı. '.venv' dizininde venv oluşturun: python -m venv .venv"
    exit 1
}

if (-not $Input) {
    Write-Host "Kullanım: .\run-windows.ps1 -Input <dosya veya klasör> [-Output <hedef>]"
    exit 1
}

$cmd = "python .\docx-converter.py -i \"$Input\""
if ($Output) { $cmd += " -o \"$Output\"" }
Invoke-Expression $cmd
