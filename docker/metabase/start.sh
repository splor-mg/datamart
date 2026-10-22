#!/bin/sh
set -eu

: "${MB_DB_PASS:?Defina MB_DB_PASS com a senha da role metabase}"
: "${MB_ENCRYPTION_SECRET_KEY:?Defina MB_ENCRYPTION_SECRET_KEY}"

# A conexão pode ser personalizada, por exemplo para verificar uma CA privada.
if [ -z "${MB_DB_CONNECTION_URI:-}" ]; then
    : "${MB_DB_HOST:?Defina MB_DB_HOST com o DNS interno do PostgreSQL}"
    export MB_DB_CONNECTION_URI="jdbc:postgresql://${MB_DB_HOST}:${MB_DB_PORT:-5432}/${MB_DB_DBNAME:-metabase}?sslmode=require"
fi

# Preserva criação do usuário, secrets _FILE e inicialização da imagem oficial.
exec /app/run_metabase.sh "$@"
