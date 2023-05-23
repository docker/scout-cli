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
        scout-binary = pkgs.fetchzip {
          url = "https://raw.githubusercontent.com/docker/scout-cli/main/dist/docker-scout_0.13.1_darwin_arm64.tar.gz";
          sha256 = "sha256-8ZYtKvuSn3fsReO7TZJf+PYk1lF+wAiDgXzm1b9i+R8=";
          stripRoot = false;
        };
      in
      with pkgs; rec {
        packages.scout-cli-plugin = stdenv.mkDerivation {
          inherit version;
          pname = "scout-cli-plugin";
          src = ./.;
          propogatedBuildInputs = [ docker ];
          installPhase = ''
            	    mkdir -p $out/.docker/cli-plugins
            	    cp ${scout-binary}/docker-scout $out/.docker/cli-plugins
            	  '';
        };
	devShells.default = mkShell {
	  inherit version;
	  pname = "scout-cli";
	  buildInputs = [packages.scout-cli-plugin];
	  shellHook = ''
			export PATH=${docker}/bin:$PATH
			export DOCKER_CONFIG=$(pwd)/.docker
			mkdir -p $DOCKER_CONFIG/cli-plugins
			cp -u ${packages.scout-cli-plugin}/.docker/cli-plugins/docker-scout $DOCKER_CONFIG/cli-plugins
		      '';
	};
      });
}

