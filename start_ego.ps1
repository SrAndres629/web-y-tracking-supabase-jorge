param(
    [int]$Cycles = 0
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" }

if ($Cycles -gt 0) {
    $env:PROJECT_EGO_MAX_CYCLES = "$Cycles"
}

Write-Host "[PROJECT EGO v2] Starting OODA loop..."
& $pythonCmd ".ai/cortex/main.py"
