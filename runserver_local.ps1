$env:TEMP = "$PSScriptRoot\.tmp"
$env:TMP = "$PSScriptRoot\.tmp"
$env:PYTHONDONTWRITEBYTECODE = "1"

if (!(Test-Path "$PSScriptRoot\.tmp")) {
    New-Item -ItemType Directory -Path "$PSScriptRoot\.tmp" | Out-Null
}

python -B manage.py runserver
