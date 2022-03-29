FROM ghcr.io/deephaven/web:0.9.0 AS ts-web
COPY data/notebooks /data/notebooks
RUN chown www-data:www-data /data/notebooks