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

## 3. Specify environmental variables

```sh
cp .env.sample .env
```

and then fill following variables in `.env` file.

- AWS_ACCOUNT_ID
- AWS_DEFAULT_REGION

> [!NOTE]
>
> Other variables in this file is needed for following steps such as [Build and test local].

## 4. Install and setup docker

```sh
mise run setup-docker
```

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
