# Just commands for topOS v0.0.1Ω

# Default recipe
default:
    @just --list

# Install based on coin-flip decision
install:
    #!/usr/bin/env bash
    echo "Flipping coin for installation path..."
    result=$(bb -m topos_mcp.core --mode coin-flip --no-start)
    case $result in
        "+1")
            echo "Coin landed on +1: Using Flox path"
            just install-flox
            ;;
        "0")
            echo "Coin landed on 0: Using current MCP client"
            just install-current
            ;;
        "-1")
            echo "Coin landed on -1: Using Babashka path"
            just install-babashka
            ;;
    esac

# Install using Flox
install-flox:
    @echo "Installing via Flox..."
    flox install
    @echo "Setting up MCP servers..."
    bb add-server.clj

# Use current MCP client
install-current:
    @echo "Using current MCP client with pseudo-operational semantics..."
    @echo "Preserving existing state and configuration..."

# Install using Babashka
install-babashka:
    @echo "Installing via Babashka..."
    bb install.clj
    @echo "Setting up MCP servers progressively..."
    bb add-server.clj

# Clean build artifacts
clean:
    rm -rf build dist *.egg-info __pycache__ .pytest_cache

# Run tests
test:
    bb test.clj

# Build package
build:
    bb build.clj

# Create backup
backup:
    bb -m topos-mcp.core --mode backup

# Run the full experience
play:
    bb -m topos-mcp.core --mode play

# Publish to package registries
publish:
    bb publish.clj
