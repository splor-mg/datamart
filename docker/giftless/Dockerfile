FROM ghcr.io/datopian/giftless:v0.6.2

COPY config.yaml /app/giftless-config.yaml
COPY start.py /app/start-giftless.py
COPY create-token.py /app/create-token.py

ENV TZ=America/Sao_Paulo

EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD python -c "import http.client; c = http.client.HTTPConnection('localhost', 8080, timeout=4); c.request('GET', '/'); assert c.getresponse().status == 404"

# O usuário giftless e o dono de /lfs-storage são preservados da imagem oficial.
ENTRYPOINT ["python", "/app/start-giftless.py"]
CMD ["--http", "0.0.0.0:8080", "-M", "-T", "--threads", "2", "-p", "2", "--manage-script-name", "--callable", "app", "--buffer-size", "16384", "--disable-logging"]
