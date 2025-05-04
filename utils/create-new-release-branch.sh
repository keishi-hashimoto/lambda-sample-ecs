#!/bin/bash

BASE_BRANCH="main"
CURRENT_BRANCH="$(git branch --show-current)"

error() {
  echo "[ERROR] ${1}"
  exit 1
}

info () {
  echo "[INFO] ${1}"
}

if [ ! "${CURRENT_BRANCH}" = "${BASE_BRANCH}" ]; then
  error "You must be on the \"${BASE_BRANCH}\" branch to create a new release branch."
fi

NEW_VERSION="${1}"
CURRENT_VERSION="$(grep "version =" pyproject.toml | sed -E 's/^version\s=\s\"([0-9]+\.[0-9]+\.[0-9]+)\"/\1/')"

get_comparable_version() {
  local version="${1}"
  # メジャーバージョン以外は 0 埋めするようにしているので、以下のような出力になる
  #  v1.0.0 ->  1000000
  # v13.2.3 -> 13002003
  echo "${version#v}" | awk -F. '{printf "%3d%03d%03d", $1,$2,$3}'
}

validate_new_version() {
  if [ -z "${NEW_VERSION}" ]; then
    error "NEW_VERSION is not specified."
  fi

  if [[ ! "${NEW_VERSION}" =~ ^v[0-9]+(\.[0-9]+){2}$ ]]; then
    error "NEW_VERSION is not valid. It should be in the format vX.Y.Z (e.g., v1.2.3)."
  fi

  if [ ! "$(get_comparable_version "${NEW_VERSION}")" -gt "$(get_comparable_version "${CURRENT_VERSION}")" ]; then
    error "NEW_VERSION \"${NEW_VERSION}\" must be newer than CURRENT_VERSION \"${CURRENT_VERSION}\"."
  fi
}


info "NEW_VERSION: ${NEW_VERSION}"
info "CURRENT_VERSION: ${CURRENT_VERSION}"
validate_new_version

# 新しいリリースブランチを作成
info "Creating new release branch \"${NEW_VERSION}\" from \"${BASE_BRANCH}\""
git switch -c "${NEW_VERSION}"

# pyproject.toml の version を更新
info "Updating version in pyproject.toml to \"${NEW_VERSION}\""
cp pyproject.toml{,.bak}
sed -i "s/^version = \"${CURRENT_VERSION}\"/version = \"${NEW_VERSION#v}\"/" pyproject.toml

# git commit して push
git add .
git commit -m ":ship: update version to ${NEW_VERSION}"
git push origin "${NEW_VERSION}"