# FireBox 5-Minute Quickstart

Get up and running with FireBox in under five minutes.

---

## Step 1: Launch FireBox in your project
Navigate to any codebase or folder:
```powershell
cd C:\Users\dev\my-awesome-project
firebox .
```
You will be greeted by the cinematic ASCII fire logo and system status card.

---

## Step 2: Initialize Project Guidelines
Generate a `FIREBOX.md` file to give FireBox project context:
```bash
firebox init
```
Edit `FIREBOX.md` with your build commands and coding standards. FireBox reads this file automatically on every turn.

---

## Step 3: Run Interactive Coding Tasks
Inside the interactive prompt:

### Ask questions about the codebase
```
Explain the authentication flow in this repository.
```

### Create a plan
```
/plan Add a rate-limiting middleware to our FastAPI endpoints
```

### Implement code with automatic testing
```
/fix Fix the TypeError in auth.py and verify with tests
```

### Review your changes
```
/review
/diff
```

---

## Step 4: Undo any unwanted changes
If an edit produces unexpected behavior, instantly restore the file:
```
/undo
```

---

## Step 5: Quit when done
```
/exit
```
Your session and conversation history will be saved automatically.
