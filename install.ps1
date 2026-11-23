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
$sourceDir = $PSScriptRoot
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

Copy-Item -Path "$sourceDir\bin\firebox.cmd" -Destination "$InstallDir\firebox.cmd" -Force
Copy-Item -Path "$sourceDir\bin\firebox.ps1" -Destination "$InstallDir\firebox.ps1" -Force

# Install python package in editable or user mode
& python -m pip install -e "$sourceDir" --no-deps | Out-Null
Write-Host " OK" -ForegroundColor Green

# 4. PATH Configuration
Write-Host "[4/5] Configuring Windows Environment PATH..." -NoNewline
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$InstallDir", "User")
    $env:Path = "$env:Path;$InstallDir"
    Write-Host " OK (Added $InstallDir to User PATH)" -ForegroundColor Green
} else {
    Write-Host " OK (Already in PATH)" -ForegroundColor Green
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
      
  To configure your AI provider and API keys:
      firebox setup
      
  Documentation:
      README.md & docs/
=============================================================================
"@ -ForegroundColor Green
