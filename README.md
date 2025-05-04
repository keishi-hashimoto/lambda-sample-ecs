# Requirements

- [mise](https://mise.jdx.dev/)

# Getting Started

## 1. Install uv and aws-cli via mise

```sh
mise trust
```

```sh
mise install
```

## 2. Setup Python environment

```sh
uv sync
```

## 3. Install and setup docker

```sh
mise run setup-docker
```

# Specify environmental variables

For following tasks such as ... and ..., you need to specify environmental variables.

Do

```sh
cp .env.sample .env
```

and then fill `.env` file.

# Build and test local

If you have updated source code and then need to test it locally, edit followin environmental variables in `.env`.

- `IMAGE_NAME`
- `TAG`

And then run

```sh
# compile requiments defined in pyproject.toml to requirements.txt
mise run compile
```

and

```sh
# build docker image
mise run build
```

and

```sh
# run image locally
mise run run-local
```

and then

```sh
# Post test request to locally running image
mise run test-local
```

If your want to stop locally running image, then

```sh
mise run stop
```

# Create new release branch

Run

```sh
mise run new-version "${version}"
```

`version` must be specified like `v1.0.0` and newer than current version specified in `pyproject.toml`.

In this command, following tasks are executed.

1. New release branch `${version}` is created.
   - **Base branch must be main**
2. `version` in `pyproject.toml` is updated.
3. File change in step「2」is commited and pushed to GitHub.
