#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Bootstrapping development environment..."

# Detect package manager
if command -v guix &> /dev/null; then
    PKG_MANAGER="guix"
elif command -v flox &> /dev/null; then
    PKG_MANAGER="flox"
else
    echo "Installing flox as default package manager..."
    curl https://get.flox.dev/install | sh
    PKG_MANAGER="flox"
fi

echo "Using package manager: ${PKG_MANAGER}"

# Install core dependencies based on package manager
install_deps() {
    local pkg=$1
    case "${PKG_MANAGER}" in
        "guix")
            guix install "$pkg"
            ;;
        "flox")
            flox install "$pkg"
            ;;
    esac
}

# Install just if not present
if ! command -v just &> /dev/null; then
    echo "Installing just..."
    install_deps just
fi

# Install Babashka if not present
if ! command -v bb &> /dev/null; then
    echo "Installing Babashka..."
    case "${PKG_MANAGER}" in
        "guix")
            guix install babashka
            ;;
        "flox")
            bash < <(curl -s https://raw.githubusercontent.com/babashka/babashka/master/install)
            ;;
    esac
fi

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Run just init if present
if [ -f "justfile" ]; then
    echo "Running initialization..."
    just init
else
    echo "❌ No justfile found"
    exit 1
fi

# Verify Babashka process manager
if [ -f "bb/process.clj" ]; then
    echo "Testing Babashka process manager..."
    bb bb/process.clj --help
fi

echo "✨ Bootstrap complete!"
echo "Run 'just self-test' to verify setup."
echo "Use 'bb bb/process.clj' to manage MCP processes:"
echo "  - 'bb bb/process.clj server' to start the server"
echo "  - 'bb bb/process.clj client' to start the client"
echo "  - 'bb bb/process.clj all' to start both"
