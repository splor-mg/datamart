FROM metabase/metabase:v0.64.1

COPY --chmod=755 start.sh /app/start-with-postgres.sh

ENV MB_DB_TYPE=postgres \
    MB_DB_PORT=5432 \
    MB_DB_DBNAME=metabase \
    MB_DB_USER=metabase \
    JAVA_TIMEZONE=America/Sao_Paulo \
    TZ=America/Sao_Paulo

EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --start-period=120s --retries=20 \
    CMD curl --fail --silent http://localhost:3000/api/health

ENTRYPOINT ["/bin/sh", "/app/start-with-postgres.sh"]
