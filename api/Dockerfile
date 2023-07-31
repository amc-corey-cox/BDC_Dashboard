# syntax=docker/dockerfile:1
FROM ubuntu:latest 

ARG TINI_VERSION=v0.19.0

ENV APP_HOME=/app \
  PYTHONUNBUFFERED=1

WORKDIR ${APP_HOME}

COPY . ./

USER 0
RUN set -eux; \
  apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget gcc zlib1g-dev libssl-dev libffi-dev libpq-dev git make tzdata \
  ; \
  
  # install tini
  wget https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini -O /sbin/tini; \
	
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
