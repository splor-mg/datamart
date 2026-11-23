#!/bin/sh
set -eu

container=$(sudo -n docker ps -q \
  --filter label=com.docker.swarm.service.name=datamart_datamart-postgres)
if [ -z "$container" ]; then
  echo 'O PostgreSQL analítico não está em execução.' >&2
  exit 1
fi
if [ -t 0 ]; then
  exec sudo -n docker exec -it "$container" psql -U postgres -d datamart "$@"
fi
exec sudo -n docker exec -i "$container" psql -U postgres -d datamart "$@"
