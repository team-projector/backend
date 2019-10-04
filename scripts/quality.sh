#!/usr/bin/env sh

set -o errexit
set -o nounset

run_checkers() {
  flake8 server

  mypy server

  # po files
  polint -i location,unsorted locale

  if find locale -name '*.po' -print0 | grep -q "."; then
    # Only executes when there is at least one `.po` file:
    dennis-cmd lint --errorsonly locale
  fi
}

run_checkers
