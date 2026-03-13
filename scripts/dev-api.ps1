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

    if (Test-Path "local.db") {
        $schemaCheck = @'
import sqlite3
from pathlib import Path

db_path = Path("local.db")
conn = sqlite3.connect(db_path)
try:
    def has_column(table_name: str, column_name: str) -> bool:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        return any(row[1] == column_name for row in rows)

    required_checks = [
        ("ingestion_runs", "import_format"),
        ("raw_comments", "source_parent_comment_id"),
        ("raw_comments", "raw_payload_json"),
        ("normalized_comments", "source_parent_comment_id"),
    ]

    ok = all(has_column(table_name, column_name) for table_name, column_name in required_checks)
    print("ok" if ok else "reset")
finally:
    conn.close()
'@

        $schemaState = $schemaCheck | python -
        if ($schemaState.Trim() -eq "reset") {
            Write-Warning "Detected stale local SQLite schema. Rebuilding local.db for current code."
            Remove-Item "local.db" -Force
        }
    }

    python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    Get-CimInstance Win32_Process |
        Where-Object {
            $_.CommandLine -like '*uvicorn*app.main:app*' -and
            $_.ProcessId -ne $PID
        } |
        ForEach-Object {
            try {
                Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop
            }
            catch {
                Write-Warning "Could not stop stale uvicorn process $($_.ProcessId)"
            }
        }

    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
