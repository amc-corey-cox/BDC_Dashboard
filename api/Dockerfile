# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.10-slim-bullseye

ENV APP_HOME=/app \
  PYTHONUNBUFFERED=1 \
  TINI_VERSION=v0.19.0

WORKDIR ${APP_HOME}

COPY . ./

RUN set -eux; \
  apt-get update; \
  apt-get upgrade -y; \
  apt-get install -y \
    wget \
  ; \
  # install tini
  wget https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini -O /sbin/tini; \
  chmod +x /sbin/tini \
  ; \
  # install py modules
  pip3 install --upgrade pip; \
  pip3 install -r requirements.txt; \
  # clean up cache
  apt-get clean && rm -rf /var/lib/apt/lists/*; \
  # collect static
  python /app/manage.py collectstatic --noinput

ENTRYPOINT ["/sbin/tini", "--"]
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]