#!/bin/bash
# Auto-upgrade MetaCubeX/metacubexd UI panel
# Usage: ./update-mihomo-ui.sh [version]
# If no version is given, fetch the latest release automatically

set -eu  # exit on any error or undefined variable

# Working directory (change if needed)
WORK_DIR="/etc/mihomo"
cd "$WORK_DIR" || { echo "Error: Cannot enter $WORK_DIR"; exit 1; }

BACKUP_NAME=""

# Version handling
if [ -n "${1:-}" ]; then
    VERSION="$1"
else
    echo "Fetching the latest version number..."
    VERSION=$(wget -qO- https://api.github.com/repos/MetaCubeX/metacubexd/releases/latest \
        | grep -oE '"tag_name": "[^"]+"' \
        | sed 's/"tag_name": "//;s/"//')
    if [ -z "$VERSION" ]; then
        echo "Error: Failed to get the latest version, please specify manually"
        exit 1
    fi
    echo "Latest version: $VERSION"
fi

# Download filename
FILENAME="compressed-dist.tgz"
DOWNLOAD_URL="https://github.com/MetaCubeX/metacubexd/releases/download/${VERSION}/${FILENAME}"

# Backup existing ui folder
if [ -d "ui" ]; then
    BACKUP_NAME="ui-$(date +%Y%m%d_%H%M%S)"
    echo "Backing up current ui to $BACKUP_NAME"
    mv ui "$BACKUP_NAME"
fi

# Download the new package
echo "Downloading $DOWNLOAD_URL ..."
wget -q "$DOWNLOAD_URL" -O "$FILENAME"
if [ $? -ne 0 ]; then
    echo "Download failed, please check network or version number"
    exit 1
fi

# Create new ui directory and extract
echo "Creating ui directory and extracting..."
mkdir ui
tar -xzvf "$FILENAME" -C ui > /dev/null
if [ $? -ne 0 ]; then
    echo "Error: Extraction failed, archive may be corrupted"
    exit 1
fi

# Clean up the downloaded archive (optional)
rm -f "$FILENAME"

echo "Upgrade complete! New UI deployed to $WORK_DIR/ui"
if [ -n "$BACKUP_NAME" ]; then
    echo "Old version backed up at $WORK_DIR/$BACKUP_NAME (remove manually if not needed)"
fi