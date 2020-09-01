#!/usr/bin/env sh

set -o errexit
set -o nounset

git_branch=$(git symbolic-ref --short -q HEAD)
if [ "${git_branch}" != "prod" ]
then
  echo "Error! Release should be on \"prod\" branch."
  exit 1
fi

version=$(cat VERSION)
git tag -a ${version} -m "v${version}"
git push
git push --tags
