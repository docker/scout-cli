# docker scout push

<!---MARKER_GEN_START-->
Push an image or image index to Docker Scout

### Options

| Name             | Type     | Default | Description                                                        |
|:-----------------|:---------|:--------|:-------------------------------------------------------------------|
| `--author`       | `string` |         | Name of the author of the image                                    |
| `--dry-run`      |          |         | Do not push the image but process it                               |
| `--org`          | `string` |         | Namespace of the Docker organization to which image will be pushed |
| `-o`, `--output` | `string` |         | Write the report to a file                                         |
| `--platform`     | `string` |         | Platform of image to be pushed                                     |
| `--sbom`         |          |         | Create and upload SBOMs                                            |
| `--secrets`      |          |         | Scan for secrets in the image                                      |
| `--timestamp`    | `string` |         | Timestamp of image or tag creation                                 |


<!---MARKER_GEN_END-->

## Description

The `docker scout push` command lets you push an image or analysis result to Docker Scout.

## Examples

### Push an image to Docker Scout

```console
$ docker scout push --org my-org registry.example.com/repo:tag
```
