#!/bin/bash
# Auto-upgrade MetaCubeX/mihomo kernel
# Usage: ./update-mihomo-kernel.sh [version] [arch] [-d|--download-only]
#   version       - specific version like "1.19.29" or "v1.19.29" (default: latest)
#   arch          - e.g. "linux-amd64-v2", "linux-amd64-v3", "linux-arm64" (default: auto-detect)
#   -d|--download-only  - download the deb only, do not install

set -eu

DOWNLOAD_ONLY=0

# Simple flag parsing (version/arch are positional)
for arg in "$@"; do
    case "$arg" in
        -d|--download-only) DOWNLOAD_ONLY=1 ;;
    esac
done

# Root check: only needed when installing
if [ "$DOWNLOAD_ONLY" -eq 0 ] && [ "$(id -u)" -ne 0 ]; then
    echo "Error: Install mode requires root (sudo). Use -d to download only." >&2
    exit 1
fi

# Dependency check
NEEDED=("wget")
if [ "$DOWNLOAD_ONLY" -eq 0 ]; then
    NEEDED+=("dpkg")
fi
for cmd in "${NEEDED[@]}"; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '$cmd' not found, please install it first" >&2
        exit 1
    fi
done

WORK_DIR="/etc/mihomo"
cd "$WORK_DIR" || { echo "Error: Cannot enter $WORK_DIR"; exit 1; }

# ---- Arch auto-detection ----
detect_arch() {
    local arch
    arch=$(uname -m)
    case "$arch" in
        x86_64)
            if grep -q '^flags.*\bavx2\b' /proc/cpuinfo 2>/dev/null; then
                echo "linux-amd64-v3"
            else
                echo "linux-amd64-v2"
            fi
            ;;
        aarch64)
            echo "linux-arm64"
            ;;
        armv7l|armv6l)
            echo "linux-armv7"
            ;;
        i686|i386)
            echo "linux-386"
            ;;
        *)
            echo "Error: Unsupported architecture: $arch" >&2
            exit 1
            ;;
    esac
}

# ---- Argument parsing ----
POS_ARGS=()
for arg in "$@"; do
    case "$arg" in
        -d|--download-only) ;;
        *) POS_ARGS+=("$arg") ;;
    esac
done

VERSION_ARG="${POS_ARGS[0]:-}"
ARCH_ARG="${POS_ARGS[1]:-}"

if [ -n "$ARCH_ARG" ]; then
    ARCH_TAG="$ARCH_ARG"
else
    ARCH_TAG=$(detect_arch) || { echo "Error: Architecture detection failed, please specify arch manually" >&2; exit 1; }
fi

# ---- Version handling ----
if [ -n "$VERSION_ARG" ]; then
    VERSION="${VERSION_ARG#v}"
else
    echo "Fetching the latest version number..."
    VERSION=$(wget -qO- https://api.github.com/repos/MetaCubeX/mihomo/releases/latest \
        | grep -oE '"tag_name": "[^"]+"' \
        | sed 's/"tag_name": "v//;s/"//')
    if [ -z "$VERSION" ]; then
        echo "Error: Failed to get the latest version, please specify manually"
        exit 1
    fi
    echo "Latest version: v$VERSION"
fi

# ---- Build URL ----
FILENAME="mihomo-${ARCH_TAG}-v${VERSION}.deb"
DOWNLOAD_URL="https://github.com/MetaCubeX/mihomo/releases/download/v${VERSION}/${FILENAME}"

# ---- Check current version ----
if command -v mihomo &>/dev/null; then
    CURRENT_VER=$(timeout 5 mihomo -v 2>/dev/null | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | sed 's/v//' | head -1 || true)
    if [ -n "$CURRENT_VER" ]; then
        echo "Current version: v$CURRENT_VER"
        if [ "$CURRENT_VER" = "$VERSION" ]; then
            echo "Already up-to-date, skipping."
            exit 0
        fi
    fi
fi

echo "Target version: v$VERSION ($ARCH_TAG)"

# ---- Download ----
echo "Downloading $FILENAME ..."
wget -q --show-progress --timeout=30 --tries=3 "$DOWNLOAD_URL" -O "$FILENAME" 2>/dev/null || \
wget -q --timeout=30 --tries=3 "$DOWNLOAD_URL" -O "$FILENAME" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Download failed. The asset may not exist for this arch ($ARCH_TAG)."
    echo "Try specifying a different arch manually, e.g.: $0 $VERSION linux-amd64-v2"
    exit 1
fi

# ---- Install ----
if [ "$DOWNLOAD_ONLY" -eq 1 ]; then
    echo "Download complete: $WORK_DIR/$FILENAME"
    echo "Install manually with: dpkg -i $WORK_DIR/$FILENAME"
else
    echo "Installing $FILENAME ..."
    dpkg -i "$FILENAME"
    rc=$?
    rm -f "$FILENAME"
    if [ $rc -ne 0 ]; then
        echo "Error: Installation failed (dpkg exit code $rc)"
        exit 1
    fi
    echo "Upgrade complete! mihomo v$VERSION installed."
fi
