#!/usr/bin/env sh

set -o errexit
set -o nounset

run_checkers() {
  CHANGED_FILES=$(git diff --name-only --no-ext-diff --diff-filter=ACMRTUXB HEAD | grep -E "\.py$" || true)

  if [ ! -z "${CHANGED_FILES}" ]; then
    black --check ${CHANGED_FILES}
    flake8 ${CHANGED_FILES}
  fi
}

run_checkers
