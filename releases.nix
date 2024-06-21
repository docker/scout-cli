let
  systems = {
    aarch64-darwin = {
      url = "https://raw.githubusercontent.com/docker/scout-cli/main/dist/docker-scout_0.13.1_darwin_arm64.tar.gz";
      sha256 = "6915fa2201a9ac8be3ddba4f0e160e69ed6a61ce133713bfd16e402538ba5091";
    };
    x86_64-darwin = {
      url = "https://raw.githubusercontent.com/docker/scout-cli/main/dist/docker-scout_0.13.1_darwin_amd64.tar.gz";
      sha256 = "ec754631c9b96fa1ecf2111fa5d202bff6c354cf266f4eb7a7ac8d9121a31fc3";
    };
    aarch64-linux = {
      url = "https://raw.githubusercontent.com/docker/scout-cli/main/dist/docker-scout_0.13.1_linux_arm64.tar.gz";
      sha256 = "f2c6a1526e17c6463624452f7a4d4347c7749e2f610b4dedfcdfea52586a39be";
    };
    x86_64-linux = {
      url = "https://raw.githubusercontent.com/docker/scout-cli/main/dist/docker-scout_0.13.1_linux_amd64.tar.gz";
      sha256 = "e9395ca5c4147cf034a4a01f8cb86f6441d3823b8e950abaae543fb7a6bdafb6";
    };
    aarch64-windows = {
      url = "https://raw.githubusercontent.com/docker/scout-cli/main/dist/docker-scout_0.13.1_windows_arm64.tar.gz";
      sha256 = "21fcca22b2ba699913b1ced8964d639ccb9006c08560a839cdaf7bcc367b45d9";
    };
    x86_64-windows = {
      url = "https://raw.githubusercontent.com/docker/scout-cli/main/dist/docker-scout_0.13.1_windows_amd64.tar.gz";
      sha256 = "0243ec94cd466fe0790b53074c36d2b6ea3ecfa62227a17fa73ce22961881b72";
    };
  };
in
{ system }: builtins.getAttr system systems
