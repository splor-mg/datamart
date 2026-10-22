-- Execute UMA VEZ com psql interativo, usando um administrador PostgreSQL.
-- Verifique antes se a role e o banco metabase já existem; este arquivo
-- interrompe em caso de erro e não apaga nem reaproveita bases existentes.
-- \password pede a senha sem colocá-la no arquivo ou no histórico SQL.
\set ON_ERROR_STOP on

CREATE ROLE metabase LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
\password metabase
CREATE DATABASE metabase OWNER metabase ENCODING 'UTF8' TEMPLATE template0;
REVOKE ALL ON DATABASE metabase FROM PUBLIC;

\connect metabase
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO metabase;
