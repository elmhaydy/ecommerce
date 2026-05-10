$Port = if ($args.Length -gt 0) { $args[0] } else { "8000" }

$env:TEMP = "$PSScriptRoot\.tmp"
$env:TMP = "$PSScriptRoot\.tmp"
$env:PYTHONDONTWRITEBYTECODE = "1"

if (!(Test-Path "$PSScriptRoot\.tmp")) {
    New-Item -ItemType Directory -Path "$PSScriptRoot\.tmp" | Out-Null
}

Write-Host "Running ecommerce project from: $PSScriptRoot"
Write-Host "Using Python: $PSScriptRoot\venv\Scripts\python.exe"
Write-Host "Open: http://127.0.0.1:$Port/admin-panel/"

& "$PSScriptRoot\venv\Scripts\python.exe" -B "$PSScriptRoot\manage.py" runserver "127.0.0.1:$Port"
