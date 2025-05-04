#!/bin/bash

DOCKER_CONFIG_FILE="${HOME}/.docker/config.json"
DOCKER_CONFIG_FILE_TMP="${DOCKER_CONFIG_FILE}.tmp"
DOCKER_CONFIG_FILE_BAK="${DOCKER_CONFIG_FILE}.bak"

THIS_DIR="$(dirname "${0}")"
BASE_FILE_PATH="${THIS_DIR}/config.json"

if [ ! -f "${DOCKER_CONFIG_FILE}" ]; then
  envsubst < "${BASE_FILE_PATH}" | tee "${DOCKER_CONFIG_FILE}"
  exit 0
fi

cp -f "${DOCKER_CONFIG_FILE}" "${DOCKER_CONFIG_FILE_BAK}"
envsubst < "${BASE_FILE_PATH}" | tee "${DOCKER_CONFIG_FILE_TMP}"

jq -s '.[0] * .[1]' "${DOCKER_CONFIG_FILE_BAK}" "${DOCKER_CONFIG_FILE_TMP}" | tee "${DOCKER_CONFIG_FILE}"