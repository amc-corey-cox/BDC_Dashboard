# syntax=docker/dockerfile:1
FROM registry.access.redhat.com/ubi8/python-39@sha256:cb3faf3d1c87f177f56f6bbcca50945a28648a2bb7496204724ae13fc42fb35d

ENV APP_HOME=/app \
  PYTHONUNBUFFERED=1 \
  TINI_VERSION=v0.19.0

WORKDIR ${APP_HOME}

COPY . ./

USER 0
RUN set -eux; \
  yum update -y; \
  yum install -y \
    wget \
  ; \
  # add perms
  chown -R 1001:0 ${APP_HOME}; \
  # install tini
  wget https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini -O /sbin/tini; \
  chmod +x /sbin/tini \
  ; \
  # install py modules
  pip install --upgrade pip; \
  pip install -r requirements.txt; \
  # collect static
  python /app/manage.py collectstatic --noinput;

USER 1001
ENTRYPOINT ["/sbin/tini", "--"]
EXPOSE 8000 2222
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]