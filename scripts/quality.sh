#!/usr/bin/env sh

set -o errexit
set -o nounset

run_checkers() {
  flake8 server

  mypy server

  # Check that all migrations worked fine:
  python manage.py makemigrations --dry-run --check

  # Checking `pyproject.toml` file contents:
  poetry check

  # Checking dependencies status:
  pip check

  # Checking if all the dependencies are secure and do not have any
  # known vulnerabilities:
  safety check --bare --full-report

  # po files
  polint -i location,unsorted locale

  if find locale -name '*.po' -print0 | grep -q "."; then
    # Only executes when there is at least one `.po` file:
    dennis-cmd lint --errorsonly locale
  fi
}

run_checkers
