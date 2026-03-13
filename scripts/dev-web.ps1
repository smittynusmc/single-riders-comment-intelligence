$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$webRoot = Join-Path $repoRoot "apps\web"
$nvmRoot = Join-Path $env:APPDATA "nvm"

if (-not (Test-Path $nvmRoot)) {
    throw "NVM for Windows directory not found at $nvmRoot"
}

$nodeDir = Get-ChildItem $nvmRoot -Directory |
    Where-Object { $_.Name -match "^v\d+\.\d+\.\d+$" } |
    Sort-Object { [version]($_.Name.TrimStart("v")) } -Descending |
    Where-Object { [version]($_.Name.TrimStart("v")) -ge [version]"20.0.0" } |
    Select-Object -First 1

if (-not $nodeDir) {
    throw "No Node 20+ installation was found under $nvmRoot"
}

$nodeExe = Join-Path $nodeDir.FullName "node.exe"
$npmCmd = Join-Path $nodeDir.FullName "npm.cmd"
$nextCli = Join-Path $repoRoot "node_modules\next\dist\bin\next"

if (-not (Test-Path $nodeExe)) {
    throw "node.exe not found at $nodeExe"
}

if (-not (Test-Path $npmCmd)) {
    throw "npm.cmd not found at $npmCmd"
}

if (-not (Test-Path (Join-Path $webRoot ".env.local"))) {
    Copy-Item (Join-Path $webRoot ".env.example") (Join-Path $webRoot ".env.local")
}

if (-not (Test-Path $nextCli)) {
    Push-Location $repoRoot
    try {
        & $npmCmd install
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

Push-Location $webRoot
try {
    & $nodeExe $nextCli "dev" "--hostname" "0.0.0.0" "--port" "3000"
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
