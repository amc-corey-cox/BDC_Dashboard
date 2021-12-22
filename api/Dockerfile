# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.8-slim-buster

ENV APP_HOME=/app \
  PYTHONUNBUFFERED=1 \
  TINI_VERSION=v0.19.0

WORKDIR ${APP_HOME}

COPY . ./

RUN set eux; \
  apt-get update; \
  apt-get install -y \
    wget \
  ; \
  # install tini
  wget https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini -O /sbin/tini; \
  chmod +x /sbin/tini \
  ; \
  # install py modules
  pip3 install -r requirements.txt; \
  # clean up cache
  apt-get clean && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/sbin/tini", "--"]
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]