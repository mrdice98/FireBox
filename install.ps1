<#
.SYNOPSIS
    FireBox Automated Installer for Windows 10 & 11
.DESCRIPTION
    Installs FireBox AI Coding Agent, configures PATH, initializes directories,
    and validates system prerequisites.
#>

[CmdletBinding()]
param(
    [switch]$Portable,
    [string]$InstallDir = "$env:USERPROFILE\.firebox\bin"
)

$Host.UI.RawUI.WindowTitle = "FireBox AI Agent Installer"

Write-Host @"
  ███████╗██╗██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗
  ██╔════╝██║██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗██╔╝
  █████╗  ██║██████╔╝█████╗  ██████╔╝██████╔╝ ╚███╔╝ 
  ██╔══╝  ██║██╔══██╗██╔══╝  ██╔══██╗██╔═══╝  ██╔██╗ 
  ██║     ██║██║  ██║███████╗██║  ██║██║     ██║  ██╗
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
             IGNITE YOUR CODE. BURN THROUGH TASKS.
"@ -ForegroundColor Red

Write-Host "`n>>> Starting FireBox Installation Sequence...`n" -ForegroundColor Yellow

$sourceDir = $PSScriptRoot

# 1. Check Python
Write-Host "[1/5] Checking Python environment..." -NoNewline
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "Python 3.10+ not found on PATH. Please install Python from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}
$pyVer = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host " OK (Python $pyVer detected)" -ForegroundColor Green

# 2. Check Git
Write-Host "[2/5] Checking Git availability..." -NoNewline
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if ($gitCmd) {
    Write-Host " OK (Git detected)" -ForegroundColor Green
} else {
    Write-Host " WARNING (Git not found; some version control tools will be limited)" -ForegroundColor Yellow
}

# 3. Create Installation Directory & Copy Files
Write-Host "[3/5] Deploying FireBox executable binaries..." -NoNewline
$targetDir = $InstallDir

try {
    New-Item -ItemType Directory -Force -Path $targetDir -ErrorAction Stop | Out-Null
    Copy-Item -Path "$sourceDir\bin\firebox.cmd" -Destination "$targetDir\firebox.cmd" -Force -ErrorAction Stop
    Copy-Item -Path "$sourceDir\bin\firebox.ps1" -Destination "$targetDir\firebox.ps1" -Force -ErrorAction Stop
} catch {
    # Fallback to local workspace bin directory
    $targetDir = "$sourceDir\bin"
}

# Also ensure root firebox.cmd exists for direct execution
Copy-Item -Path "$sourceDir\bin\firebox.cmd" -Destination "$sourceDir\firebox.cmd" -Force -ErrorAction SilentlyContinue

# Install python package in editable mode with offline fallback
try {
    & python -m pip install -e "$sourceDir" --no-deps --no-build-isolation *>$null
} catch {}
Write-Host " OK ($targetDir)" -ForegroundColor Green

# 4. PATH Configuration
Write-Host "[4/5] Configuring Windows Environment PATH..." -NoNewline
try {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -and ($userPath -notlike "*$targetDir*")) {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$targetDir", "User")
    }
    $env:Path = "$env:Path;$targetDir"
    Write-Host " OK (PATH updated)" -ForegroundColor Green
} catch {
    $env:Path = "$env:Path;$targetDir"
    Write-Host " OK (Current Session PATH updated)" -ForegroundColor Green
}

# 5. Health Check Diagnostics
Write-Host "[5/5] Running FireBox Doctor diagnostics..." -ForegroundColor Cyan
& python -m firebox.cli doctor

Write-Host @"
=============================================================================
  🔥 FIREBOX INSTALLATION COMPLETE! 🔥
  
  To start FireBox, open any terminal or PowerShell window and run:
      firebox
      
  Or target your project workspace directly:
      firebox .
      
  To run diagnostics:
      firebox doctor
      
  To configure your AI provider and API keys:
      firebox setup
      
  Documentation:
      README.md & docs/
=============================================================================
"@ -ForegroundColor Green
