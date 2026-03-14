$ErrorActionPreference = "Stop"

$stateRoot = Join-Path $env:LOCALAPPDATA "Single Riders Comment Intelligence"
$runtimeRoot = Join-Path $stateRoot "runtime"
$stateFile = Join-Path $runtimeRoot "process-state.json"

if (-not (Test-Path $stateFile)) {
    Write-Host "No native runtime state file found. The app may already be stopped." -ForegroundColor Yellow
    exit 0
}

$state = Get-Content -LiteralPath $stateFile | ConvertFrom-Json
$pids = @(
    $state.web_pid,
    $state.web_wrapper_pid,
    $state.api_pid,
    $state.api_wrapper_pid
) | Where-Object { $_ }

foreach ($processId in $pids) {
    try {
        Stop-Process -Id ([int]$processId) -Force -ErrorAction Stop
    }
    catch {
    }
}

Remove-Item -LiteralPath $stateFile -Force -ErrorAction SilentlyContinue

Write-Host "Native app stopped." -ForegroundColor Green
