#!/usr/bin/env bash
# ============================================================================
# FireBox Automated Installer for Linux & macOS
# Ignite Your Code. Burn Through Tasks.
# ============================================================================

set -e

echo -e "\033[38;2;255;85;0m"
cat << "EOF"
  ███████╗██╗██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗
  ██╔════╝██║██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗██╔╝
  █████╗  ██║██████╔╝█████╗  ██████╔╝██████╔╝ ╚███╔╝ 
  ██╔══╝  ██║██╔══██╗██╔══╝  ██╔══██╗██╔═══╝  ██╔██╗ 
  ██║     ██║██║  ██║███████╗██║  ██║██║     ██║  ██╗
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
             IGNITE YOUR CODE. BURN THROUGH TASKS.
EOF
echo -e "\033[0m"

echo ">>> Starting FireBox Installation Sequence..."

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3.10+ is required."
    exit 1
fi

INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# 2. Install FireBox package
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -m pip install -e "$SOURCE_DIR" --user

# 3. Create launcher script
LAUNCHER="$INSTALL_DIR/firebox"
cat << EOF > "$LAUNCHER"
#!/usr/bin/env bash
python3 -m firebox.cli "\$@"
EOF
chmod +x "$LAUNCHER"

echo ">>> FireBox installed successfully to $LAUNCHER!"
echo ">>> Run 'firebox doctor' to verify your setup."
