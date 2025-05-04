#!/bin/bash

DOCKER_CONFIG_FILE="${HOME}/.docker/config.json"


THIS_DIR="$(dirname "${0}")"
BASE_FILE_PATH="${THIS_DIR}/config.json"

cp -f "${DOCKER_CONFIG_FILE}"{,.bak}
envsubst < "${BASE_FILE_PATH}" | tee "${DOCKER_CONFIG_FILE}"