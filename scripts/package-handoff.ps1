$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$distRoot = Join-Path $repoRoot "dist"
$stagingRoot = Join-Path $distRoot "handoff-staging"
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$zipPath = Join-Path $distRoot "single-riders-comment-intelligence-handoff-$timestamp.zip"

$excludedDirectoryNames = @(
    ".git",
    ".venv",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "coverage",
    "dist",
    "node_modules"
)

$excludedFilePatterns = @(
    ".env",
    ".env.local",
    "*.pyc",
    "*.pyo",
    "*.db",
    "*.db-wal",
    "*.db-shm",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "local.db"
)

function Should-SkipItem {
    param(
        [System.IO.FileSystemInfo]$Item
    )

    if ($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        return $true
    }

    if ($excludedDirectoryNames -contains $Item.Name) {
        return $true
    }

    foreach ($pattern in $excludedFilePatterns) {
        if ($Item.Name -like $pattern) {
            return $true
        }
    }

    return $false
}

function Copy-IncludedTree {
    param(
        [string]$Source,
        [string]$Destination
    )

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null

    foreach ($item in Get-ChildItem -Force -LiteralPath $Source) {
        if (Should-SkipItem -Item $item) {
            continue
        }

        $target = Join-Path $Destination $item.Name
        if ($item.PSIsContainer) {
            Copy-IncludedTree -Source $item.FullName -Destination $target
        }
        else {
            Copy-Item -LiteralPath $item.FullName -Destination $target -Force
        }
    }
}

New-Item -ItemType Directory -Force -Path $distRoot | Out-Null

if (Test-Path $stagingRoot) {
    Remove-Item -LiteralPath $stagingRoot -Recurse -Force
}

Copy-IncludedTree -Source $repoRoot -Destination $stagingRoot

@"
Single Riders Comment Intelligence Handoff

Quick start
1. Install Docker Desktop and open it once.
2. Double-click scripts\start-handoff.bat
3. Wait for the browser to open the in-app guide at http://localhost:3000/guide
4. Use scripts\stop-handoff.bat when you are done

TikTok JSON
- The app expects the TikTok account data export in JSON format
- Step-by-step instructions live in docs\handoff.md and in the in-app Guide page
"@ | Set-Content -LiteralPath (Join-Path $stagingRoot "HANDOFF-START-HERE.txt") -Encoding ASCII

if (Test-Path $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path (Join-Path $stagingRoot "*") -DestinationPath $zipPath -Force

Remove-Item -LiteralPath $stagingRoot -Recurse -Force

Write-Host ""
Write-Host "Handoff package created:" -ForegroundColor Green
Write-Host $zipPath -ForegroundColor Green
Write-Host ""
Write-Host "Share that zip with teammates. They only need Docker Desktop plus the included start/stop scripts." -ForegroundColor Cyan
