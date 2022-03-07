FROM ghcr.io/deephaven/web:0.9.0 AS ts-web
COPY data/notebooks /data/notebooks
RUN chown www-data:www-data /data/notebooks


from python:3.8 AS twitter-sent
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
