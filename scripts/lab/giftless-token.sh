#!/bin/sh
set -eu

container=$(sudo -n docker ps -q \
  --filter label=com.docker.swarm.service.name=datamart_giftless)
if [ -z "$container" ]; then
  echo 'Giftless não está em execução.' >&2
  exit 1
fi
exec sudo -n docker exec "$container" python /app/create-token.py \
  --scope 'obj:*/*/*:read,write,verify' "$@"
