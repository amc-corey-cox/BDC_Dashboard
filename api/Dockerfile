# syntax=docker/dockerfile:1
FROM registry.access.redhat.com/ubi9@sha256:aee6d39282dabc3374a01d4a81f97c6827cbcdcf155cadb5a42966134205b05d

ENV APP_HOME=/app \
  PYTHONUNBUFFERED=1 \
  TINI_VERSION=v0.19.0

WORKDIR ${APP_HOME}

COPY . ./

USER 0
RUN set -eux; \
  yum update -y; \
  yum install -y \
    wget gcc zlib-devel openssl-devel libffi-devel libpq-devel git \
  ; \

  # install tini
  wget https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini -O /sbin/tini; 

RUN set -eux; \
  # install pyenv
  git clone https://github.com/pyenv/pyenv.git /.pyenv; \
  export PYENV_ROOT="/.pyenv"; \
  export PATH="${PYENV_ROOT}/bin:${PATH}"; \
  eval "$(pyenv init -)"; \

  # install python 3.11.1
  pyenv install 3.11.1; \
  pyenv global 3.11.1; \
  pyenv rehash; \

  # install python modules
  python3.11 -m pip install --upgrade pip; \
  python3.11 -m pip install wheel; \
  python3.11 -m pip install -r requirements.txt; \
  
  # Django collectstatic
  python3.11 /app/manage.py collectstatic --noinput; \

  # add perms
  chmod a+w ${APP_HOME}/tracker/migrations; \
  chmod a+x ${APP_HOME}/docker_entrypoint.sh; \
  chmod +x /sbin/tini; \
  chown -R 1001:0 ${APP_HOME}; \
  chown -R 1001:0 /.pyenv;

USER 1001

ENTRYPOINT ["/sbin/tini", "--"]
EXPOSE 8000 2222
CMD ["./docker_entrypoint.sh"]