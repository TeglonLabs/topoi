#!/usr/bin/env bash
set -euo pipefail

echo "📥 Making babashka gay..."

# Define supported OSes and architectures
declare -A OS_ARCH_MAP=(
  ["linux-amd64"]="linux-amd64"
  ["linux-aarch64"]="linux-aarch64"
  ["macos-amd64"]="macos-amd64"
  ["macos-aarch64"]="macos-aarch64"
  ["windows-amd64"]="windows-amd64"
)

# Base URL for Babashka releases
BASE_URL="https://github.com/babashka/babashka/releases/latest/download"

# Temporary directory for downloads
TMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TMP_DIR"

# Iterate over each OS-ARCH pair
for key in "${!OS_ARCH_MAP[@]}"; do
  IFS='-' read -r OS ARCH <<< "$key"
  FILE_NAME="babashka"
  EXT=""
  
  case "$OS" in
    linux)
      FILE_NAME="babashka-${OS}-${ARCH}"
      EXT=".tar.gz"
      ;;
    macos)
      FILE_NAME="babashka-${OS}-${ARCH}"
      EXT=".tar.gz"
      ;;
    windows)
      FILE_NAME="babashka-${OS}-${ARCH}"
      EXT=".zip"
      ;;
    *)
      echo "Unsupported OS: $OS"
      continue
      ;;
  esac
  
  DOWNLOAD_URL="${BASE_URL}/${FILE_NAME}${EXT}"
  echo "Downloading from: $DOWNLOAD_URL"
  
  curl -L "$DOWNLOAD_URL" -o "${TMP_DIR}/${FILE_NAME}${EXT}"
  
  # Extract and rename
  echo "Extracting and renaming to 'gay'..."
  case "$OS" in
    linux|macos)
      tar -xzf "${TMP_DIR}/${FILE_NAME}${EXT}" -C "$TMP_DIR"
      mv "$TMP_DIR/$FILE_NAME" "$TMP_DIR/gay"
      ;;
    windows)
      unzip "${TMP_DIR}/${FILE_NAME}${EXT}" -d "$TMP_DIR"
      mv "$TMP_DIR/bb.exe" "$TMP_DIR/gay.exe"
      ;;
  esac
  
  # Move to legacy directory
  echo "Moving 'gay' binary to 'legacy' directory..."
  case "$OS" in
    linux|macos)
      cp "$TMP_DIR/gay" "../legacy/gay-${OS}-${ARCH}"
      chmod +x "../legacy/gay-${OS}-${ARCH}"
      ;;
    windows)
      cp "$TMP_DIR/gay.exe" "../legacy/gay-${OS}-${ARCH}.exe"
      ;;
  esac
done

# Clean up temporary directory
rm -rf "$TMP_DIR"

echo "✅ 'gay' binaries have been downloaded and placed in the 'legacy' directory."

# Create symbolic links or wrapper scripts if necessary
echo "🔗 Creating symbolic links for 'gay' binaries..."

# Example for Linux and macOS (assuming amd64 and aarch64)
ln -sf "legacy/gay-linux-amd64" "../legacy/gay"
ln -sf "legacy/gay-macos-amd64" "../legacy/gay-macos"

# Example for Windows (batch script)
echo "@echo off
legacy\gay-windows-amd64.exe %*" > "../legacy/gay.bat"

echo "✅ Symbolic links and wrapper scripts created."

echo "✨ All 'gay' binaries are set up successfully."
