FROM postgres:17.11-alpine

# Build com contexto em docker/postgres/.
COPY --chmod=755 init-databases.sh /docker-entrypoint-initdb.d/10-datamart.sh
COPY --chmod=755 with-tls.sh /usr/local/bin/postgres-with-tls.sh
COPY pg_hba.external.conf /etc/postgresql/pg_hba.conf

ENV POSTGRES_DB=postgres \
    POSTGRES_USER=postgres \
    POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 \
    TZ=America/Sao_Paulo

EXPOSE 5432
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=10 \
    CMD pg_isready -U postgres -d postgres

ENTRYPOINT ["/bin/sh", "/usr/local/bin/postgres-with-tls.sh"]
CMD ["postgres", "-c", "ssl=on", "-c", "ssl_cert_file=/run/postgres-tls/server.crt", "-c", "ssl_key_file=/run/postgres-tls/server.key", "-c", "hba_file=/etc/postgresql/pg_hba.conf"]
