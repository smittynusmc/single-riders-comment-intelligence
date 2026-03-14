param(
    [switch]$ResetData
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker Desktop is required to stop the handoff stack."
}

if (-not (Test-Path $composeFile)) {
    throw "docker-compose.yml not found at $composeFile"
}

$arguments = @("down")
if ($ResetData) {
    $arguments += "-v"
}

Push-Location $repoRoot
try {
    & docker compose -f $composeFile @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose $($arguments -join ' ') failed with exit code $LASTEXITCODE"
    }

    if ($ResetData) {
        Write-Host "Handoff stack stopped and Docker volumes were removed." -ForegroundColor Yellow
    }
    else {
        Write-Host "Handoff stack stopped. Database data was kept for the next launch." -ForegroundColor Green
    }
}
finally {
    Pop-Location
}
