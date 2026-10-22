#!/bin/sh
set -eu

# A imagem oficial executa este arquivo apenas quando o volume está vazio.
# As senhas são lidas do ambiente pelo psql, sem interpolação de SQL no shell.
psql --set ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv datamart_password DATAMART_PASSWORD
\getenv metabase_password METABASE_DB_PASSWORD
\getenv reader_password METABASE_READER_PASSWORD

CREATE ROLE datamart LOGIN PASSWORD :'datamart_password';
CREATE ROLE metabase LOGIN PASSWORD :'metabase_password';
CREATE ROLE metabase_reader LOGIN PASSWORD :'reader_password';

CREATE DATABASE datamart OWNER datamart;
REVOKE ALL ON DATABASE datamart FROM PUBLIC;
GRANT CONNECT ON DATABASE datamart TO metabase_reader;

CREATE DATABASE metabase OWNER metabase;
REVOKE ALL ON DATABASE metabase FROM PUBLIC;

\connect datamart
SET ROLE datamart;
CREATE SCHEMA dados_siafi AUTHORIZATION datamart;
CREATE SCHEMA linktable AUTHORIZATION datamart;
GRANT USAGE ON SCHEMA public, dados_siafi, linktable TO metabase_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public, dados_siafi, linktable TO metabase_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE datamart IN SCHEMA public, dados_siafi, linktable
    GRANT SELECT ON TABLES TO metabase_reader;
RESET ROLE;
SQL
