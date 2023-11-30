- [Docker Scout](#docker-scout)
- [Usage](#usage)
- [CLI Plugin Installation](#cli-plugin-installation)
- [Run as container](#run-as-container)
- [CI integration](#ci-integration)
- [License](#license)
 
# Docker Scout

[Docker Scout](https://www.docker.com/products/docker-scout/)  is a set of software supply chain features integrated into Docker's user interfaces and command line interface (CLI). These features offer comprehensive visibility into the structure and security of container images.
This repository contains installable binaries of the `docker scout` CLI plugin.

## Usage

The [CLI documentation is available in this repository](./docs/scout.md).

See the [reference documentation](https://docs.docker.com/scout) to learn about Docker Scout including Docker Desktop and Docker Hub integrations.

### Environment Variables

The following environment variables are availabe to configure the Scout CLI:

| Name | Description |
| ---- | ----------- |
| `DOCKER_SCOUT_CACHE_FORMAT` | Format of the local image cache; can be `oci` or `tar` |
| `DOCKER_SCOUT_CACHE_DIR` | Directory where the local SBOM cache is stored |
| `DOCKER_SCOUT_NO_CACHE` | Disable the local SBOM cache |
| `DOCKER_SCOUT_REGISTRY_TOKEN` | Registry Access token to authenticate when pulling images |
| `DOCKER_SCOUT_REGISTRY_USER` | Registry user name to authenticate when pulling images |
| `DOCKER_SCOUT_REGISTRY_PASSWORD` | Registry password/PAT to authenticate when pulling images |
| `DOCKER_SCOUT_HUB_USER` | Docker Hub user name to authenticate against the Docker Scout backend |
| `DOCKER_SCOUT_HUB_PASSWORD` | Docker Hub password/PAT to authenticate against the Docker Scout backend |
| `DOCKER_SCOUT_OFFLINE` | Offline mode during SBOM indexing |
| `DOCKER_SCOUT_NEW_VERSION_WARN` | Warn about new versions of the Docker Scout CLI |
| `DOCKER_SCOUT_EXPERIMENTAL_WARN` | Warn about experimental features |
| `DOCKER_SCOUT_EXPERIMENTAL_POLICY_OUTPUT` | Disable experimental policy output |


## CLI Plugin Installation

### Docker Desktop

`docker scout` CLI plugin is available by default on [Docker Desktop](https://docs.docker.com/desktop/) starting with version `4.17`.

### Manual Installation

To install it manually:

- Download the `docker-scout` binary corresponding to your platform from the [latest](https://github.com/docker/scout-cli/releases/latest) or [other](https://github.com/docker/scout-cli/releases) releases.
- Uncompress it as
    - `docker-scout` on _Linux_ and _macOS_
    - `docker-scout.exe` on _Windows_
- Copy the binary to the `scout` directory
    - `$HOME/.docker/scout` on _Linux_ and _macOS_
    - `%USERPROFILE%\.docker\scout` on _Windows_
- Make it executable on _Linux_ and _macOS_
    - `chmod +x $HOME/.docker/scout/docker-scout`
- Authorize the binary to be executable on _macOS_
    - `xattr -d com.apple.quarantine $HOME/.docker/scout/docker-scout`
- Add the `scout` directory to your `.docker/config.json` as a plugin directory
    - `$HOME/.docker/config.json` on _Linux_ and _macOS_
    - `%USERPROFILE%\.docker\config.json` on _Windows_
    - Add the `cliPluginsExtraDirs` property to the `config.json` file
```
{
	...
	"cliPluginsExtraDirs": [
		<full path to the .docker/scout folder>
	],
	...
}
```

### Script Installation

To install, run the following command in your terminal:

```shell
curl -sSfL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh -s --
```

## Run as container

A container image to run the Docker Scout CLI in containerized environments is available at [docker/scout-cli](https://hub.docker.com/r/docker/scout-cli). 

## CI Integration

Docker Scout CLI can be used in CI environments. See below for the various ways to integrate the CLI into your CI pipelines.

### GitHub Action

An early prototype of running the Docker Scout CLI as part of a GitHub Action workflow is available at [docker/scout-action](https://github.com/docker/scout-action).

The following GitHub Action workflow can be used as a template to integrate Docker Scout:

```yaml
name: Docker

on:
  push:
    tags: [ "*" ]
    branches:
      - 'main'
  pull_request:
    branches: [ "**" ]
    
env:
  # Use docker.io for Docker Hub if empty
  REGISTRY: docker.io
  IMAGE_NAME: ${{ github.repository }}
  SHA: ${{ github.event.pull_request.head.sha || github.event.after }}

jobs:
  build:

    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          ref: ${{ env.SHA }}
          
      - name: Setup Docker buildx
        uses: docker/setup-buildx-action@v2.5.0

      # Login against a Docker registry except on PR
      # https://github.com/docker/login-action
      - name: Log into registry ${{ env.REGISTRY }}
        uses: docker/login-action@v2.1.0
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PAT }}

      # Extract metadata (tags, labels) for Docker
      # https://github.com/docker/metadata-action
      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v4.4.0
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          labels: |
            org.opencontainers.image.revision=${{ env.SHA }}
          tags: |
            type=edge,branch=$repo.default_branch
            type=semver,pattern=v{{version}}
            type=sha,prefix=,suffix=,format=short
      
      # Build and push Docker image with Buildx (don't push on PR)
      # https://github.com/docker/build-push-action
      - name: Build and push Docker image
        id: build-and-push
        uses: docker/build-push-action@v4.0.0
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Docker Scout
        id: docker-scout
        if: ${{ github.event_name == 'pull_request' }}
        uses: docker/scout-action@dd36f5b0295baffa006aa6623371f226cc03e506
        with:
          command: cves
          image: ${{ steps.meta.outputs.tags }}
          only-severities: critical,high
          exit-code: true
```

### GitLab

Use the following pipeline definition as a template to get Docker Scout integrated in GitLab CI:

```yaml
docker-build:
  image: docker:latest
  stage: build
  services:
    - docker:dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
    
    # Install curl and the Docker Scout CLI
    - |
      apk add --update curl
      curl -sSfL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh -s -- 
      apk del curl 
      rm -rf /var/cache/apk/* 
    # Login to Docker Hub required for Docker Scout CLI
    - echo "$DOCKER_HUB_PAT" | docker login --username "$DOCKER_HUB_USER" --password-stdin
  script:
    - |
      if [[ "$CI_COMMIT_BRANCH" == "$CI_DEFAULT_BRANCH" ]]; then
        tag=""
        echo "Running on default branch '$CI_DEFAULT_BRANCH': tag = 'latest'"
      else
        tag=":$CI_COMMIT_REF_SLUG"
        echo "Running on branch '$CI_COMMIT_BRANCH': tag = $tag"
      fi
    - docker build --pull -t "$CI_REGISTRY_IMAGE${tag}" .
    
    - |
      if [[ "$CI_COMMIT_BRANCH" == "$CI_DEFAULT_BRANCH" ]]; then
        # Get a CVE report for the built image and fail the pipeline when critical or high CVEs are detected
        docker scout cves "$CI_REGISTRY_IMAGE${tag}" --exit-code --only-severity critical,high    
      else
        # Compare image from branch with latest image from the default branch and fail if new critical or high CVEs are detected
        docker scout compare "$CI_REGISTRY_IMAGE${tag}" --to "$CI_REGISTRY_IMAGE:latest" --exit-code --only-severity critical,high --ignore-unchanged
      fi
    
    - docker push "$CI_REGISTRY_IMAGE${tag}"
  rules:
    - if: $CI_COMMIT_BRANCH
      exists:
        - Dockerfile
```

### CircleCI 

Use the following pipeline definition as a template to get Docker Scout integrated in CircleCI project:

```yaml
version: 2.1

jobs:
  
  build:

    docker:
      - image: cimg/base:stable
    
    environment:
      IMAGE_TAG: docker/scout-demo-service:latest
    
    steps:
      # Checkout the repository files
      - checkout

      # Set up a separate Docker environment to run `docker` commands in
      - setup_remote_docker:
          version: 20.10.24

      # Install Docker Scout and login to Docker Hub
      - run:
          name: Install Docker Scout
          command: |
            env
            curl -sSfL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh -s -- -b /home/circleci/bin
            echo $DOCKER_HUB_PAT | docker login -u $DOCKER_HUB_USER --password-stdin

      # Build the Docker image
      - run:
          name: Build Docker image
          command: docker build -t $IMAGE_TAG .
      
      # Run Docker Scout          
      - run:
          name: Scan image for CVEs
          command: |
            docker-scout cves $IMAGE_TAG --exit-code --only-severity critical,high

workflows:
  build-docker-image:
    jobs:
      - build
```

### Microsoft Azure DevOps Pipelines

Use the following pipeline definition as a template to get Docker Scout integrated in Azure DevOps Pipelines:

```yaml
trigger:
- main

resources:
- repo: self

variables:
  tag: '$(Build.BuildId)'
  image: 'vonwig/nodejs-service'

stages:
- stage: Build
  displayName: Build image
  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: ubuntu-latest
    steps:
    - task: Docker@2
      displayName: Build an image
      inputs:
        command: build
        dockerfile: '$(Build.SourcesDirectory)/Dockerfile'
        repository: $(image)
        tags: |
          $(tag)
    - task: CmdLine@2
      displayName: Find CVEs on image
      inputs:
        script: |
          # Install the Docker Scout CLI
          curl -sSfL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh -s --
          # Login to Docker Hub required for Docker Scout CLI
          docker login -u $(DOCKER_HUB_USER) -p $(DOCKER_HUB_PAT)
          # Get a CVE report for the built image and fail the pipeline when critical or high CVEs are detected
          docker scout cves $(image):$(tag) --exit-code --only-severity critical,high
```

### Jenkins

The following snippet can be added to a `Jenkinsfile` to install and analyze images:

```groovy
        stage('Analyze image') {
            steps {
                // Install Docker Scout
                sh 'curl -sSfL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh -s -- -b /usr/local/bin'
                
                // Log into Docker Hub
                sh 'echo $DOCKER_HUB_PAT | docker login -u $DOCKER_HUB_USER --password-stdin'

                // Analyze and fail on critical or high vulnerabilities
                sh 'docker-scout cves $IMAGE_TAG --exit-code --only-severity critical,high'
            }
        }
```

This example assume two secrets to be available to authenticate against Docker Hub, called `DOCKER_HUB_USER` and `DOCKER_HUB_PAT`. 

### Bitbucket

Use the following pipeline definition as a template to get Docker Scout integrated in Bitbucket Pipelines:

```yaml
image: docker

pipelines:
  default:
    - step:
        name: Build
        services:
          - docker
        caches:
          - docker
        script:
          - echo "$DOCKER_HUB_PAT" | docker login --username "$DOCKER_HUB_USER" --password-stdin $CI_REGISTRY

          # Install curl and the Docker Scout CLI
          - |
            export DOCKER_BUILDKIT=0
            apk add --update curl
            curl -sSfL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh -s -- 
            apk del curl 
            rm -rf /var/cache/apk/* 
          # Login to Docker Hub required for Docker Scout CLI
          - echo "$DOCKER_HUB_PAT" | docker login --username "$DOCKER_HUB_USER" --password-stdin

          - |
            export DEVELOPMENT_BRANCH="main"
            if [[ "$BITBUCKET_BRANCH" == "$DEVELOPMENT_BRANCH" ]]; then # Bitbucket uses master by default, adjust if your default branch is different
              tag=":latest"
              echo "Running on default branch '$DEVELOPMENT_BRANCH': tag = 'latest'"
            else
              tag=":$BITBUCKET_COMMIT"
              echo "Running on branch '$BITBUCKET_BRANCH': tag = $tag"
            fi
          - docker build --pull -t "$CI_REGISTRY_IMAGE${tag}" .

          - |
            if [[ "$BITBUCKET_BRANCH" == "$DEVELOPMENT_BRANCH" ]]; then
              # Get a CVE report for the built image and fail the pipeline when critical or high CVEs are detected
              docker scout cves "$CI_REGISTRY_IMAGE${tag}" --exit-code --only-severity critical,high    
            else
              # Compare image from branch with latest image from the default branch and fail if new critical or high CVEs are detected            
              docker scout compare "$CI_REGISTRY_IMAGE${tag}" --to "$CI_REGISTRY_IMAGE:latest" --exit-code --only-severity critical,high --ignore-unchanged
            fi
          - docker push "$CI_REGISTRY_IMAGE${tag}"

definitions:
  services:
    docker:
      memory: 2048 # Optional: Increase if needed
```

This example assumes two secrets to be available to authenticate against Docker Hub, called `DOCKER_HUB_USER` and `DOCKER_HUB_PAT`, also is necessary more two secrets called `CI_REGISTRY`, `CI_REGISTRY_IMAGE` about registry info. 

## License

The Docker Scout CLI is licensed under the Terms and Conditions of the [Docker Subscription Service Agreement](https://www.docker.com/legal/docker-subscription-service-agreement/).
