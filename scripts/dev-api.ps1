$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiRoot = Join-Path $repoRoot "apps\api"
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
    throw "Virtual environment not found at $venvActivate"
}

Push-Location $apiRoot
try {
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
    }

    . $venvActivate
    $env:SCI_DATABASE_URL = "sqlite:///./local.db"
    $env:SCI_WORKER_MODE = "inline"

    python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    uvicorn app.main:app --reload
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
