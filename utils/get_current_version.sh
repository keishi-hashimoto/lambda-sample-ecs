#!/bin/bash

set -Ceu pipefail

WORKING_DIR="$(dirname "$(dirname "$(realpath "${0}")")")"
cd "${WORKING_DIR}"

CURRENT_VERSION="$(grep "version =" pyproject.toml | sed -E 's/^version\s=\s\"([0-9]+\.[0-9]+\.[0-9]+)\"/\1/')"
echo "${CURRENT_VERSION}"