#!/usr/bin/env sh

docker-compose -p team_projector \
               -f develop/docker-compose.base.yml \
               stop
