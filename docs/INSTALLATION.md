# FireBox Installation Guide

This guide covers installing FireBox on Windows 10/11, Linux, and macOS.

## System Prerequisites

- **Python**: Version 3.10 or higher.
- **Git**: Git 2.20+ recommended for version control tools.
- **Terminal**: Windows Terminal, PowerShell 7 / Windows PowerShell, iTerm2, or any modern terminal emulator supporting ANSI TrueColor.

---

## 🪟 Windows 10 & Windows 11 Installation

### Method 1: Automated PowerShell Installer (Recommended)
1. Open Windows PowerShell.
2. Navigate to the FireBox directory:
   ```powershell
   cd C:\Users\vivia\Downloads\FIREBOX
   ```
3. Run the installer:
   ```powershell
   .\install.ps1
   ```
4. The installer will:
   - Verify Python and Git.
   - Deploy `firebox.cmd` and `firebox.ps1` to `%USERPROFILE%\.firebox\bin`.
   - Add the binary directory to your user `PATH`.
   - Run `firebox doctor` to ensure all checks pass.

### Method 2: Portable Run (No installation required)
You can run FireBox immediately without modifying your system PATH:
```powershell
.\bin\firebox.cmd
```
Or directly via Python:
```powershell
python -m firebox.cli
```

---

## 🐧 Linux & 🍎 macOS Installation

1. Open your terminal.
2. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. Ensure `~/.local/bin` is in your shell `PATH`:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
4. Verify installation:
   ```bash
   firebox doctor
   ```

---

## 🩺 Verifying Your Installation

Run the built-in diagnostic doctor:
```bash
firebox doctor
```

All core categories (System, OS, Git CLI, Storage, Tools, Security) should report **PASS**.
