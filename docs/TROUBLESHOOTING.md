# FireBox Troubleshooting Guide

This guide helps resolve common setup, provider, and runtime issues.

---

## 1. Run System Diagnostics First

Whenever you encounter an issue, run FireBox Doctor:
```bash
firebox doctor
```
Doctor will check:
- Python runtime compatibility.
- Git binary path and version.
- Configuration directory write permissions.
- Active provider credentials and model endpoints.
- Registered tools status.
- Workspace boundary enforcement.

---

## 2. Common Issues & Solutions

### Issue: "No API key found for <provider>"
- **Solution**: Set the environment variable:
  ```powershell
  $env:OPENAI_API_KEY = "sk-..."
  $env:ANTHROPIC_API_KEY = "sk-ant-..."
  ```
  Or run the configuration wizard:
  ```bash
  firebox setup
  ```
  Or switch to the offline simulator or local Ollama:
  ```bash
  firebox provider add mock mock-key
  firebox models set firebox-sim-1.0
  ```

### Issue: "Access is denied: C:\Users\...\.firebox"
- **Solution**: If running in a sandboxed, restricted, or containerized environment, set the `FIREBOX_HOME` environment variable to a writable workspace folder:
  ```powershell
  $env:FIREBOX_HOME = "C:\Users\vivia\Downloads\FIREBOX\.firebox"
  ```
  FireBox automatically falls back to `./.firebox` if the home directory is read-only.

### Issue: PowerShell ExecutionPolicy Blocks Running Scripts
- **Solution**: On Windows, PowerShell may block executing `.ps1` scripts by default. Run:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```
  Or launch using the batch file:
  ```cmd
  .\bin\firebox.cmd
  ```

### Issue: Local Model Connection Failed (Ollama / LM Studio)
- **Solution**: Ensure your local LLM server is running and accessible:
  - Ollama: Ensure `ollama serve` is running on `http://localhost:11434`.
  - LM Studio: Ensure the local server is started on `http://localhost:1234` with CORS enabled.
