# Build this from the repo's top-level directory (i.e. CSC4006-Artifacts/)

FROM python:3.10-alpine
EXPOSE 8000

ENV WEB_CONCURRENCY 1
ENV TIMEOUT 15
ENV GRACEFUL_TIMEOUT 30
ENV MAX_REQUESTS 5
ENV MAX_REQUESTS_JITTER 5

ENV SECRET_KEY  ""
ENV INTEGRATION_URL  ""

ADD ./requirements.txt /tmp/requirements.txt

COPY ./frontend-ms/src /app
WORKDIR /app
RUN pip3 install -r /tmp/requirements.txt
RUN chmod +x ./main.py

CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000"]