# docker scout policy

<!---MARKER_GEN_START-->
Evaluate local Rego policies against an image and display the results (experimental)

### Subcommands

| Name                                 | Description                                                                             |
|:-------------------------------------|:----------------------------------------------------------------------------------------|
| [`publish`](scout_policy_publish.md) | Package local Rego policies into an OCI bundle and push it to a registry (experimental) |


### Options

| Name                | Type          | Default | Description                                                                                                                                                                              |
|:--------------------|:--------------|:--------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-e`, `--exit-code` |               |         | Return exit code '2' if policies are not met, '0' otherwise                                                                                                                              |
| `--only-policy`     | `stringSlice` |         | Comma separated list of policies to evaluate                                                                                                                                             |
| `--org`             | `string`      |         | Namespace of the Docker organization                                                                                                                                                     |
| `-o`, `--output`    | `string`      |         | Write the report to a file                                                                                                                                                               |
| `--platform`        | `string`      |         | Platform of image to evaluate policies against                                                                                                                                           |
| `--policy-bundle`   | `stringArray` |         | OCI reference of a policy bundle to evaluate (repeatable)                                                                                                                                |
| `--policy-config`   | `string`      |         | Path or http(s) URL to a JSON file configuring policy enablement and inputs                                                                                                              |
| `--policy-dir`      | `stringArray` |         | Path to a directory of local .rego policy files (repeatable)                                                                                                                             |
| `--policy-file`     | `stringArray` |         | Path or http(s) URL to a .rego policy file (repeatable)                                                                                                                                  |
| `--result-file`     | `string`      |         | Write the full Rego evaluation result (pass, violations, query bindings and OPA metrics) of each evaluated policy to a JSON file (useful when iterating on local --policy-file policies) |


<!---MARKER_GEN_END-->

## Description

The `docker scout policy` command evaluates policies against an image.
The image analysis is uploaded to Docker Scout where policies get evaluated.

The policy evaluation results may take a few minutes to become available.

## Examples

### Evaluate policies against an image and display the results

```console
$ docker scout policy dockerscoutpolicy/customers-api-service:0.0.1
```

### Evaluate policies against an image for a specific organization

```console
$ docker scout policy dockerscoutpolicy/customers-api-service:0.0.1 --org dockerscoutpolicy
```

### Evaluate policies against an image with a specific platform

```console
$ docker scout policy dockerscoutpolicy/customers-api-service:0.0.1 --platform linux/amd64
```

### Compare policy results for a repository in a specific environment

```console
$ docker scout policy dockerscoutpolicy/customers-api-service --to-env production
```
