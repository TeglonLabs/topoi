{
  description = "Topos MCP - Model Context Protocol implementation for topological computing";

  inputs = {
    flox-floxpkgs.url = "github:flox/floxpkgs";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, flox-floxpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);
    in {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.stdenv.mkDerivation {
            name = "topos-mcp";
            version = "0.1.0";
            src = ./.;
            
            buildInputs = with pkgs; [
              babashka
              qemu
              jet
            ];

            installPhase = ''
              mkdir -p $out/bin
              cp -r bb $out/lib/bb
              cp -r src $out/lib/src
              
              # Create the topos command wrapper
              cat > $out/bin/topos << EOF
              #!/bin/sh
              exec ${pkgs.babashka}/bin/bb -cp $out/lib/bb:$out/lib/src "$@"
              EOF
              
              chmod +x $out/bin/topos
            '';
          };
        });

      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              babashka
              qemu
              jet
            ];
          };
        });
    };
}
