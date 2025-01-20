#!/usr/bin/env bash

set -euo pipefail

# Determine OS and architecture
case "$(uname -s)" in
    Linux*)     OS=linux;;
    Darwin*)    OS=macos;;
    MINGW*)     OS=windows;;
    *)          echo "Unsupported OS: $(uname -s)"; exit 1;;
esac

case "$(uname -m)" in
    x86_64)     ARCH=amd64;;
    aarch64)    ARCH=aarch64;;
    arm64)      ARCH=aarch64;;
    *)          echo "Unsupported architecture: $(uname -m)"; exit 1;;
esac

# Get latest version from GitHub
VERSION=$(curl -s https://api.github.com/repos/babashka/babashka/releases/latest | grep -o '"tag_name": "[^"]*' | cut -d'"' -f4)
BINARY_VERSION="${VERSION:1}"  # Remove 'v' prefix

# Set download URL based on OS and architecture
if [ "$OS" = "windows" ]; then
    ARCHIVE="babashka-${BINARY_VERSION}-windows-amd64.zip"
    BINARY="bb.exe"
    TARGET="gay.exe"
else
    if [ "$OS" = "macos" ]; then
        ARCHIVE="babashka-${BINARY_VERSION}-macos-${ARCH}.tar.gz"
    else
        ARCHIVE="babashka-${BINARY_VERSION}-linux-${ARCH}.tar.gz"
    fi
    BINARY="bb"
    TARGET="gay"
fi

DOWNLOAD_URL="https://github.com/babashka/babashka/releases/download/v${BINARY_VERSION}/${ARCHIVE}"

# Create temporary directory
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

echo "Downloading Babashka $VERSION for $OS-$ARCH..."
curl -LO "$DOWNLOAD_URL"

# Extract archive
if [ "$OS" = "windows" ]; then
    unzip "$ARCHIVE"
else
    tar xf "$ARCHIVE"
fi

# Modify binary to support .gay extension
if [ "$OS" = "windows" ]; then
    # Windows: Use resource hacker or similar to modify binary
    echo "Windows binary modification not yet implemented"
else
    # Unix: Use strings replacement
    echo "Adding .gay extension support..."
    strings -t d "$BINARY" | grep ".clj" > string_offsets.txt
    while read -r line; do
        offset=$(echo "$line" | awk '{print $1}')
        dd if=/dev/zero of="$BINARY" bs=1 seek=$offset count=4 conv=notrunc 2>/dev/null
        printf ".gay" | dd of="$BINARY" bs=1 seek=$offset count=4 conv=notrunc 2>/dev/null
    done < string_offsets.txt
fi

# Install binary
INSTALL_DIR="${HOME}/.local/bin"
mkdir -p "$INSTALL_DIR"

if [ "$OS" = "windows" ]; then
    mv "$BINARY" "${INSTALL_DIR}/${TARGET}"
else
    mv "$BINARY" "${INSTALL_DIR}/${TARGET}"
    chmod +x "${INSTALL_DIR}/${TARGET}"
fi

# Create file extension association
if [ "$OS" = "macos" ]; then
    defaults write com.apple.LaunchServices LSHandlers -array-add '{LSHandlerContentType=public.gay;LSHandlerRoleAll='"${INSTALL_DIR}/${TARGET}"';}'
elif [ "$OS" = "linux" ]; then
    mkdir -p "${HOME}/.local/share/applications"
    cat > "${HOME}/.local/share/applications/gay.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Gay
Exec=${INSTALL_DIR}/${TARGET} %f
MimeType=text/gay;
Categories=Development;
EOF
    
    mkdir -p "${HOME}/.local/share/mime/packages"
    cat > "${HOME}/.local/share/mime/packages/gay.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="text/gay">
    <glob pattern="*.gay"/>
    <comment>Gay script file</comment>
  </mime-type>
</mime-info>
EOF
    update-mime-database "${HOME}/.local/share/mime"
fi

# Clean up
cd
rm -rf "$TMP_DIR"

echo "✨ Installation complete! The 'gay' command is now available."
echo "You can run .gay files with: gay script.gay"

# Add to PATH if not already present
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo "Adding ${INSTALL_DIR} to PATH..."
    echo "export PATH=\"\${PATH}:${INSTALL_DIR}\"" >> "${HOME}/.bashrc"
    echo "Please restart your shell or run: export PATH=\"\${PATH}:${INSTALL_DIR}\""
fi
