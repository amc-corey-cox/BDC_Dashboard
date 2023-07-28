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

# RUN set -eux; \
#   # install pyenv
#   git clone https://github.com/pyenv/pyenv.git ~/.pyenv; \
#   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc; \
#   echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc; \
#   echo 'eval "$(pyenv init --path)"' >> ~/.bashrc; \
#   echo 'eval "$(pyenv init -)"' >> ~/.bashrc; \
#   echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc;

# RUN set -eux; \
#   exec bash ; \
#   # source ~/.bashrc; \
#   pyenv install 3.11.1; \
#   pyenv global 3.11.1; \
#   pyenv rehash;

RUN set -eux; \
  # install python 3.11.1
  wget https://www.python.org/ftp/python/3.11.1/Python-3.11.1.tgz; \
  tar xzf Python-3.11.1.tgz; \ 
  cd Python-3.11.1; \
  ./configure --enable-optimizations; \
  make install ; \
  cd ../; \
  rm Python-3.11.1.tgz ; \

  # create venv
  /usr/local/bin/python3  -m venv ${APP_HOME};

# add perms
RUN set -eux; \
  chown -R 1001:0 ${APP_HOME} ; \
  chmod a+w ${APP_HOME}/tracker/migrations ; \
  chmod a+x ${APP_HOME}/docker_entrypoint.sh ; \
  chmod +x /sbin/tini ; \
  chmod +x ${APP_HOME}/bin/activate ; \
  chown -R 1001:0 ${APP_HOME} ;

# install python modules
RUN set -eux; \
  ${APP_HOME}/bin/activate ; \
  /usr/local/bin/python3 -m pip install --upgrade pip ; \
  /usr/local/bin/python3 -m pip install wheel ; \
  /usr/local/bin/python3 -m pip install -r requirements.txt ; \
  
  # Django collectstatic
  /usr/local/bin/python3 /app/manage.py collectstatic --noinput; 

USER 1001
ENTRYPOINT ["/sbin/tini", "--"]
EXPOSE 8000 2222
CMD ["./docker_entrypoint.sh"]