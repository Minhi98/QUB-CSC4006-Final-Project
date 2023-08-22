# Build this from the repo's top-level directory (i.e. CSC4006-Artifacts/)

FROM python:3.10-alpine
EXPOSE 8000

ENV WEB_CONCURRENCY 1
ENV TIMEOUT 15
ENV GRACEFUL_TIMEOUT 30
ENV MAX_REQUESTS 5
ENV MAX_REQUESTS_JITTER 5

ENV MYSQL_HOST "csc4006"
ENV MYSQL_PORT 3299
ENV MYSQL_USER "root"
ENV MYSQL_PASS "4006"
ENV MYSQL_DB "testdb"

ENV SERVICE_TABLE "undefined_table_name"
ENV JSON_TABLE_MIN_SCHEMA '{"test_field1": "VARCHAR(255) NOT NULL", "test_field2":"int"}'

ADD ./requirements.txt /tmp/requirements.txt

COPY ./datastore-microservice/src /app
WORKDIR /app
RUN pip3 install -r /tmp/requirements.txt
RUN chmod +x ./main.py

CMD gunicorn main:app -t ${TIMEOUT} --graceful-timeout ${GRACEFUL_TIMEOUT} --max-requests ${MAX_REQUESTS} --max-requests-jitter ${MAX_REQUESTS_JITTER} -b 0.0.0.0:8000