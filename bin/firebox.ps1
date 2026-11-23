<#
.SYNOPSIS
    FireBox PowerShell Launcher
.DESCRIPTION
    Launches FireBox AI Coding Agent within Windows PowerShell.
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$fireboxRoot = (Resolve-Path "$scriptDir\..").Path

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python 3.10+ is required to launch FireBox." -ForegroundColor Red
    Write-Host "Please install Python from https://python.org or Microsoft Store." -ForegroundColor Yellow
    exit 1
}

$env:PYTHONPATH = "$fireboxRoot;$env:PYTHONPATH"
python -m firebox.cli @ArgsList
