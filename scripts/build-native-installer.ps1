param(
    [switch]$SkipApiBuild,
    [switch]$SkipWebBuild,
    [switch]$SkipInstaller,
    [string]$NodeVersion = "20.18.0"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiRoot = Join-Path $repoRoot "apps\api"
$webRoot = Join-Path $repoRoot "apps\web"
$distRoot = Join-Path $repoRoot "dist\native"
$bundleRoot = Join-Path $distRoot "Single Riders Comment Intelligence"
$pyInstallerDist = Join-Path $distRoot "pyinstaller"
$pyInstallerWork = Join-Path $distRoot "pyinstaller-build"
$nodeCacheRoot = Join-Path $repoRoot ".native-cache\node"
$portableZipPath = Join-Path $distRoot "single-riders-comment-intelligence-native-portable.zip"
$innoScript = Join-Path $repoRoot "infra\windows\SingleRidersCommentIntelligence.iss"
$nextCli = Join-Path $repoRoot "node_modules\next\dist\bin\next"

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Copy-Tree {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }

    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
}

function Get-NodeRuntime {
    param([string]$RequestedVersion)

    $pathNode = Get-Command node -ErrorAction SilentlyContinue
    if ($pathNode) {
        $versionOutput = & $pathNode.Source --version
        if ($LASTEXITCODE -eq 0) {
            $version = [version]($versionOutput.TrimStart("v"))
            if ($version.Major -ge 20) {
                return Split-Path -Parent $pathNode.Source
            }
        }
    }

    $nvmRoot = Join-Path $env:APPDATA "nvm"
    if (Test-Path $nvmRoot) {
        $nodeDir = Get-ChildItem $nvmRoot -Directory |
            Where-Object { $_.Name -match "^v\d+\.\d+\.\d+$" } |
            Sort-Object { [version]($_.Name.TrimStart("v")) } -Descending |
            Where-Object { [version]($_.Name.TrimStart("v")) -ge [version]"20.0.0" } |
            Select-Object -First 1

        if ($nodeDir) {
            return $nodeDir.FullName
        }
    }

    Ensure-Directory -Path $nodeCacheRoot
    $zipFile = Join-Path $nodeCacheRoot "node-v$RequestedVersion-win-x64.zip"
    $expandedRoot = Join-Path $nodeCacheRoot "node-v$RequestedVersion-win-x64"

    if (-not (Test-Path $expandedRoot)) {
        if (-not (Test-Path $zipFile)) {
            $downloadUrl = "https://nodejs.org/dist/v$RequestedVersion/node-v$RequestedVersion-win-x64.zip"
            Write-Host "Downloading Node runtime from $downloadUrl" -ForegroundColor Cyan
            Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile
        }

        Expand-Archive -LiteralPath $zipFile -DestinationPath $nodeCacheRoot -Force
    }

    return $expandedRoot
}

function Get-PythonExecutable {
    $venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        return $venvPython
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return $pythonCommand.Source
    }

    throw "Python was not found. Create the project .venv or install Python 3.11+ before building the native installer."
}

function Get-InnoCompiler {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
    ) | Where-Object { $_ -and (Test-Path $_) }

    return $candidates | Select-Object -First 1
}

Ensure-Directory -Path $distRoot

$nodeRuntime = Get-NodeRuntime -RequestedVersion $NodeVersion
$nodeExe = Join-Path $nodeRuntime "node.exe"
$npmCmd = Join-Path $nodeRuntime "npm.cmd"
$npmCli = Join-Path $nodeRuntime "node_modules\npm\bin\npm-cli.js"
$pythonExe = Get-PythonExecutable

if (-not (Test-Path $nodeExe)) {
    throw "node.exe was not found under $nodeRuntime"
}

if (-not (Test-Path $npmCmd)) {
    throw "npm.cmd was not found under $nodeRuntime"
}

if (-not (Test-Path $npmCli)) {
    throw "npm-cli.js was not found under $nodeRuntime"
}

if (-not $SkipApiBuild) {
    Write-Host "Building native API executable..." -ForegroundColor Cyan
    & $pythonExe -m pip install -e "$apiRoot[package]"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install API packaging dependencies."
    }

    if (Test-Path $pyInstallerDist) {
        Remove-Item -LiteralPath $pyInstallerDist -Recurse -Force
    }

    if (Test-Path $pyInstallerWork) {
        Remove-Item -LiteralPath $pyInstallerWork -Recurse -Force
    }

    Push-Location $apiRoot
    try {
        & $pythonExe -m PyInstaller `
            --noconfirm `
            --clean `
            --onedir `
            --name "single-riders-comment-intelligence-api" `
            --distpath $pyInstallerDist `
            --workpath $pyInstallerWork `
            --paths $apiRoot `
            --hidden-import app.db.base `
            app\run_native.py

        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller failed."
        }
    }
    finally {
        Pop-Location
    }
}

if (-not $SkipWebBuild) {
    Write-Host "Building standalone web app..." -ForegroundColor Cyan
    Push-Location $repoRoot
    try {
        if (-not (Test-Path $nextCli)) {
            & $nodeExe $npmCli install
            if ($LASTEXITCODE -ne 0) {
                throw "npm install failed."
            }
        }
    }
    finally {
        Pop-Location
    }

    Push-Location $webRoot
    try {
        & $nodeExe $nextCli build
        if ($LASTEXITCODE -ne 0) {
            throw "Next.js standalone build failed."
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "Staging native bundle..." -ForegroundColor Cyan

if (Test-Path $bundleRoot) {
    Remove-Item -LiteralPath $bundleRoot -Recurse -Force
}

Ensure-Directory -Path $bundleRoot
Ensure-Directory -Path (Join-Path $bundleRoot "docs")
Ensure-Directory -Path (Join-Path $bundleRoot "runtime")
Ensure-Directory -Path (Join-Path $bundleRoot "scripts")

Copy-Tree -Source (Join-Path $pyInstallerDist "single-riders-comment-intelligence-api") -Destination (Join-Path $bundleRoot "api")
Copy-Tree -Source (Join-Path $webRoot ".next\standalone") -Destination (Join-Path $bundleRoot "web")
Copy-Tree -Source $nodeRuntime -Destination (Join-Path $bundleRoot "runtime\node")
Copy-Tree -Source (Join-Path $repoRoot "sample_data") -Destination (Join-Path $bundleRoot "sample_data")

$stagedServerJs = Get-ChildItem -Path (Join-Path $bundleRoot "web") -Filter "server.js" -Recurse | Select-Object -First 1
if (-not $stagedServerJs) {
    throw "Could not find server.js in the standalone web output."
}

$stagedAppRoot = $stagedServerJs.Directory.FullName
$staticSource = Join-Path $webRoot ".next\static"
$publicSource = Join-Path $webRoot "public"

if (Test-Path $staticSource) {
    Ensure-Directory -Path (Join-Path $stagedAppRoot ".next")
    Copy-Tree -Source $staticSource -Destination (Join-Path $stagedAppRoot ".next\static")
}

if (Test-Path $publicSource) {
    Copy-Tree -Source $publicSource -Destination (Join-Path $stagedAppRoot "public")
}

Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\start-native.ps1") -Destination (Join-Path $bundleRoot "scripts\start-native.ps1") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\start-native.bat") -Destination (Join-Path $bundleRoot "scripts\start-native.bat") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\stop-native.ps1") -Destination (Join-Path $bundleRoot "scripts\stop-native.ps1") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\stop-native.bat") -Destination (Join-Path $bundleRoot "scripts\stop-native.bat") -Force

Copy-Item -LiteralPath (Join-Path $repoRoot "docs\handoff.md") -Destination (Join-Path $bundleRoot "docs\handoff.md") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "docs\native-handoff.md") -Destination (Join-Path $bundleRoot "docs\native-handoff.md") -Force

@"
Single Riders Comment Intelligence Native Bundle

Start
1. Double-click scripts\start-native.bat
2. Wait for the browser to open
3. Upload a TikTok JSON export on the Imports page

Stop
- Double-click scripts\stop-native.bat

More help
- docs\native-handoff.md
- docs\handoff.md
"@ | Set-Content -LiteralPath (Join-Path $bundleRoot "START-HERE.txt") -Encoding ASCII

if (Test-Path $portableZipPath) {
    Remove-Item -LiteralPath $portableZipPath -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($bundleRoot, $portableZipPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)

if (-not $SkipInstaller) {
    $innoCompiler = Get-InnoCompiler
    if ($innoCompiler) {
        Write-Host "Building native installer with Inno Setup..." -ForegroundColor Cyan
        & $innoCompiler "/DBundleRoot=$bundleRoot" "/DOutputRoot=$distRoot" $innoScript
        if ($LASTEXITCODE -ne 0) {
            throw "Inno Setup failed."
        }
    }
    else {
        Write-Warning "Inno Setup 6 was not found. The portable native bundle was created, but no .exe installer was produced."
    }
}

Write-Host ""
Write-Host "Portable native bundle:" -ForegroundColor Green
Write-Host $portableZipPath -ForegroundColor Green
if (-not $SkipInstaller) {
    Write-Host "Installer output directory: $distRoot" -ForegroundColor Green
}
