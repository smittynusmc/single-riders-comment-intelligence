param(
    [switch]$SkipBrowser
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"

function Invoke-Compose {
    param(
        [string[]]$Arguments
    )

    & docker compose -f $composeFile @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker Desktop is required. Install Docker Desktop, open it once, then run this script again."
}

if (-not (Test-Path $composeFile)) {
    throw "docker-compose.yml not found at $composeFile"
}

& docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is installed but not running. Start Docker Desktop, wait for it to finish starting, then run this script again."
}

Write-Host ""
Write-Host "Starting Single Riders Comment Intelligence for handoff use..." -ForegroundColor Cyan
Write-Host "This launcher will:" -ForegroundColor DarkGray
Write-Host "  1. Start Docker services" -ForegroundColor DarkGray
Write-Host "  2. Run database migrations" -ForegroundColor DarkGray
Write-Host "  3. Open the in-app guide" -ForegroundColor DarkGray
Write-Host ""

Push-Location $repoRoot
try {
    Invoke-Compose -Arguments @("up", "--build", "-d", "postgres", "redis")

    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        & docker compose -f $composeFile exec -T postgres pg_isready -U postgres -d comment_intelligence *> $null
        if ($LASTEXITCODE -eq 0) {
            break
        }

        if ($attempt -eq 29) {
            throw "Postgres did not become ready in time."
        }

        Start-Sleep -Seconds 2
    }

    Invoke-Compose -Arguments @("run", "--rm", "api", "alembic", "upgrade", "head")
    Invoke-Compose -Arguments @("up", "--build", "-d", "api", "worker", "web")

    Write-Host "Web: http://localhost:3000" -ForegroundColor Green
    Write-Host "API: http://localhost:8000" -ForegroundColor Green
    Write-Host "Stop later with scripts\\stop-handoff.bat" -ForegroundColor Yellow
    Write-Host ""

    if (-not $SkipBrowser) {
        Start-Sleep -Seconds 3
        Start-Process "http://localhost:3000/guide"
    }
}
finally {
    Pop-Location
}
