# Build this from the repo's top-level directory (i.e. CSC4006-Artifacts/)

FROM python:3.10-alpine
EXPOSE 8000

ENV WEB_CONCURRENCY 1

ENV MYSQL_HOST "csc4006"
ENV MYSQL_PORT 3306
ENV MYSQL_USER "root"
ENV MYSQL_PASS "4006"
ENV MYSQL_DB "cmsdb"

ENV POPULATE_EMPTY_DB 1

ADD ./requirements.txt /tmp/requirements.txt

COPY ./Customer-Management-Service /app
WORKDIR /app
RUN pip3 install -r /tmp/requirements.txt
RUN chmod +x ./main.py

CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000"]