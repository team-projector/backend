#!/usr/bin/env sh

set -o errexit
set -o nounset

version=$(cat VERSION)
git tag -a ${version} -m "v${version}"
git push
git push --tags
