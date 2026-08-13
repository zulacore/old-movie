{
  description = "old-movie: devshell with python and its dependencies, pinned only via nixpkgs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python3.withPackages (ps: [ ps.pillow ps.click ]);
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ python ];
        shellHook = ''
          export PYTHONPATH="$PWD/src:$PYTHONPATH"
        '';
      };
    };
}
