{ pkgs ? import <nixpkgs> {} }:

with pkgs;

mkShell {
  buildInputs = [
    # Core dependencies
    babashka
    qemu
    jet

    # Development tools
    git
    just
  ];

  shellHook = ''
    echo ""
    echo "🌀 Topos MCP Development Environment"
    echo "-----------------------------------"
    echo "Available commands:"
    echo "  just         - Show available tasks"
    echo "  topos        - Run topos command"
    echo ""
  '';
}
