{
  description = "Docker Scout cli";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        version = "0.13.1";

        scout-binary = pkgs.fetchurl {
	  inherit (import ./releases.nix {inherit system;}) url sha256; };
      in
      with pkgs; rec {
        packages.scout-cli-plugin = stdenv.mkDerivation {
          inherit version;
          pname = "scout-cli-plugin";
          src = ./.;
	  nativeBuildInputs = [gnutar];
          propogatedBuildInputs = [ docker docker-credential-helpers ];
          installPhase = ''
	            tar -xzf ${scout-binary} 
            	    mkdir -p $out/.docker/cli-plugins
            	    cp docker-scout $out/.docker/cli-plugins
            	  '';
        };
	devShells.default = mkShell {
	  inherit version;
	  pname = "scout-cli";
	  buildInputs = [packages.scout-cli-plugin];
	  shellHook = ''
			export PATH=${docker}/bin:${docker-credential-helpers}/bin:$PATH
			export DOCKER_CONFIG=$(pwd)/.docker
			mkdir -p $DOCKER_CONFIG/cli-plugins
			cp -u ${packages.scout-cli-plugin}/.docker/cli-plugins/docker-scout $DOCKER_CONFIG/cli-plugins
		      '';
	};
      });
}

