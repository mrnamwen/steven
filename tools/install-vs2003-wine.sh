#!/bin/bash
# Install Visual Studio .NET 2003 Professional compiler under Wine
# Only extracts the VC++ compiler toolchain — not the full IDE
#
# Usage: ./install-vs2003-wine.sh /path/to/disc1.iso [/path/to/disc2.iso]

set -euo pipefail

DISC1="${1:?Usage: $0 /path/to/disc1.iso [/path/to/disc2.iso]}"
DISC2="${2:-}"

WINEPREFIX="${WINEPREFIX:-$HOME/.wine}"
export WINEPREFIX

echo "=== VS2003 VC++ Compiler Installation for Wine ==="
echo "Wine prefix: $WINEPREFIX"
echo "Disc 1: $DISC1"

# Mount disc 1
MOUNTPOINT=$(udisksctl loop-setup --file "$DISC1" 2>&1 | grep -oP '/dev/loop\d+')
udisksctl mount --block-device "$MOUNTPOINT" 2>&1
DISC1_PATH=$(findmnt -n -o TARGET "$MOUNTPOINT")
echo "Disc 1 mounted at: $DISC1_PATH"

# Check for setup.exe
if [ -f "$DISC1_PATH/Setup/setup.exe" ]; then
    echo ""
    echo "Found setup.exe. Starting VS2003 installation..."
    echo ""
    echo "IMPORTANT: During installation, choose CUSTOM install and select ONLY:"
    echo "  - Visual C++ .NET"
    echo "  - .NET Framework SDK (needed for headers)"
    echo "Deselect everything else (VB, C#, Crystal Reports, etc.)"
    echo ""
    echo "Press Enter to start the installer, or Ctrl+C to abort."
    read -r

    wine "$DISC1_PATH/Setup/setup.exe"
elif [ -f "$DISC1_PATH/setup.exe" ]; then
    echo "Starting installer..."
    wine "$DISC1_PATH/setup.exe"
else
    echo "No setup.exe found. Contents of disc:"
    ls "$DISC1_PATH/"
    echo ""
    echo "Try running the installer manually:"
    echo "  wine \"$DISC1_PATH/<installer>.exe\""
fi

# Cleanup
echo ""
echo "Unmounting disc..."
udisksctl unmount --block-device "$MOUNTPOINT" 2>&1 || true
udisksctl loop-delete --block-device "$MOUNTPOINT" 2>&1 || true

echo ""
echo "=== Post-installation ==="
echo "Check if cl.exe is available:"
echo "  find \$WINEPREFIX -name 'cl.exe' 2>/dev/null"
echo ""
echo "Test the compiler:"
echo "  wine \"\$(find \$WINEPREFIX -name 'cl.exe' -path '*/VC7/*' | head -1)\" /?"
