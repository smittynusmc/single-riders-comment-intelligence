param(
    [switch]$SkipBrowser
)

$ErrorActionPreference = "Stop"

$bundleRoot = Split-Path -Parent $PSScriptRoot
$stateRoot = Join-Path $env:LOCALAPPDATA "Single Riders Comment Intelligence"
$runtimeRoot = Join-Path $stateRoot "runtime"
$logsRoot = Join-Path $stateRoot "logs"
$apiWorkRoot = Join-Path $runtimeRoot "api"
$stateFile = Join-Path $runtimeRoot "process-state.json"
$apiPort = 8000
$webPort = 3000

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Test-UrlReady {
    param([string]$Url)

    try {
        $null = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        return $true
    }
    catch {
        return $false
    }
}

function Wait-ForUrl {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-UrlReady -Url $Url) {
            return
        }

        Start-Sleep -Milliseconds 750
    }

    throw "Timed out waiting for $Url"
}

function Find-ProcessByPattern {
    param(
        [string]$Pattern,
        [int[]]$ExcludeIds = @()
    )

    $escapedPattern = [Regex]::Escape($Pattern)

    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        $match = Get-CimInstance Win32_Process |
            Where-Object {
                $_.ProcessId -notin $ExcludeIds -and
                $_.CommandLine -and
                $_.CommandLine -match $escapedPattern
            } |
            Sort-Object ProcessId -Descending |
            Select-Object -First 1

        if ($match) {
            return [int]$match.ProcessId
        }

        Start-Sleep -Milliseconds 500
    }

    throw "Could not find a running process for pattern: $Pattern"
}

Ensure-Directory -Path $runtimeRoot
Ensure-Directory -Path $logsRoot
Ensure-Directory -Path $apiWorkRoot

if (Test-UrlReady -Url "http://127.0.0.1:$webPort/guide") {
    if (-not $SkipBrowser) {
        Start-Process "http://127.0.0.1:$webPort/guide"
    }
    Write-Host "Single Riders Comment Intelligence is already running at http://127.0.0.1:$webPort" -ForegroundColor Green
    exit 0
}

$apiExe = Join-Path $bundleRoot "api\single-riders-comment-intelligence-api.exe"
$nodeExe = Join-Path $bundleRoot "runtime\node\node.exe"
$webRoot = Join-Path $bundleRoot "web"
$serverJs = Get-ChildItem -Path $webRoot -Filter "server.js" -Recurse | Select-Object -First 1

if (-not (Test-Path $apiExe)) {
    throw "Native API executable not found at $apiExe"
}

if (-not (Test-Path $nodeExe)) {
    throw "Bundled Node runtime not found at $nodeExe"
}

if (-not $serverJs) {
    throw "Could not find the bundled Next.js server.js file under $webRoot"
}

$dbPath = Join-Path $stateRoot "local.db"
$dbUrl = "sqlite:///$($dbPath.Replace('\', '/'))"
$apiLog = Join-Path $logsRoot "api.log"
$webLog = Join-Path $logsRoot "web.log"
$apiEnvPath = Join-Path $apiWorkRoot ".env"
$apiRunner = Join-Path $runtimeRoot "run-api.cmd"
$webRunner = Join-Path $runtimeRoot "run-web.cmd"

@"
SCI_DATABASE_URL=$dbUrl
SCI_ALLOWED_ORIGINS=http://127.0.0.1:$webPort,http://localhost:$webPort
SCI_WORKER_MODE=inline
SCI_LLM_PROVIDER=stub
"@ | Set-Content -LiteralPath $apiEnvPath -Encoding ASCII

@"
@echo off
cd /d "$apiWorkRoot"
"$apiExe" >> "$apiLog" 2>>&1
"@ | Set-Content -LiteralPath $apiRunner -Encoding ASCII

@"
@echo off
set PORT=$webPort
set HOSTNAME=127.0.0.1
set API_BASE_URL=http://127.0.0.1:$apiPort
set NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:$apiPort
cd /d "$($serverJs.Directory.FullName)"
"$nodeExe" "$($serverJs.FullName)" >> "$webLog" 2>>&1
"@ | Set-Content -LiteralPath $webRunner -Encoding ASCII

$started = @()

try {
    $apiWrapper = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$apiRunner`"" -WindowStyle Hidden -PassThru
    $started += $apiWrapper.Id
    $apiPid = Find-ProcessByPattern -Pattern $apiExe -ExcludeIds @($apiWrapper.Id)

    Wait-ForUrl -Url "http://127.0.0.1:$apiPort/health" -TimeoutSeconds 45

    $webWrapper = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$webRunner`"" -WindowStyle Hidden -PassThru
    $started += $webWrapper.Id
    $webPid = Find-ProcessByPattern -Pattern $serverJs.FullName -ExcludeIds @($webWrapper.Id)

    Wait-ForUrl -Url "http://127.0.0.1:$webPort/guide" -TimeoutSeconds 60

    @{
        api_wrapper_pid = $apiWrapper.Id
        api_pid = $apiPid
        web_wrapper_pid = $webWrapper.Id
        web_pid = $webPid
        api_log = $apiLog
        web_log = $webLog
    } | ConvertTo-Json | Set-Content -LiteralPath $stateFile -Encoding ASCII

    Write-Host "Native app started." -ForegroundColor Green
    Write-Host "Web: http://127.0.0.1:$webPort" -ForegroundColor Green
    Write-Host "API: http://127.0.0.1:$apiPort" -ForegroundColor Green
    Write-Host "Logs: $logsRoot" -ForegroundColor Yellow

    if (-not $SkipBrowser) {
        Start-Process "http://127.0.0.1:$webPort/guide"
    }
}
catch {
    foreach ($processId in $started) {
        try {
            Stop-Process -Id $processId -Force -ErrorAction Stop
        }
        catch {
        }
    }

    throw
}
