#!/bin/sh
set -eu

# Copia a chave montada para corrigir dono/permissão em qualquer host Docker.
mkdir -p /run/postgres-tls
cp /certificates/server.crt /run/postgres-tls/server.crt
cp /certificates/server.key /run/postgres-tls/server.key
chown -R postgres:postgres /run/postgres-tls
chmod 700 /run/postgres-tls
chmod 600 /run/postgres-tls/server.key
chmod 644 /run/postgres-tls/server.crt

exec /usr/local/bin/docker-entrypoint.sh "$@"
