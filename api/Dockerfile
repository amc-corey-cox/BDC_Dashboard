# syntax=docker/dockerfile:1
FROM python:3.4
ENV PYTHONUNBUFFERED=1

# install modules
COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV APP_HOME /app/api
WORKDIR ${APP_HOME}
COPY . ${APP_HOME}

EXPOSE 8000
# TODO: add entrypoint