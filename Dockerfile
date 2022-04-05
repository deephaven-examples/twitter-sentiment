FROM ghcr.io/deephaven/web:${VERSION:-latest} AS ts-web
COPY data/notebooks /data/notebooks
RUN chown www-data:www-data /data/notebooks