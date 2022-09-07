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
    wget gcc zlib-devel openssl-devel libffi-devel \
  ; \
  # add perms
  chown -R 1001:0 ${APP_HOME}; \
  chmod a+w ${APP_HOME}/tracker/migrations; \
  chmod a+x ${APP_HOME}/docker_entrypoint.sh; \

  # install tini
  wget https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini -O /sbin/tini; \
  chmod +x /sbin/tini \
  ; \
  
  wget https://www.python.org/ftp/python/3.10.6/Python-3.10.6.tgz; \
  tar xzf Python-3.10.6.tgz; \ 
  cd Python-3.10.6; \
  ./configure --enable-optimizations; \
  make install ; \
  cd ../; \
  rm Python-3.10.6.tgz ; \

  /usr/local/bin/python3  -m venv ${APP_HOME}; \
  chmod +x ${APP_HOME}/bin/activate ; \
  ${APP_HOME}/bin/activate ; \
	
  chown -R 1001:0 ${APP_HOME} ; \
      
  # install py modules 
  /usr/local/bin/python3 -m pip install --upgrade pip ; \
  /usr/local/bin/python3 -m pip install wheel ; \
  /usr/local/bin/python3 -m pip install -r requirements.txt ; \
  # collect static
  /usr/local/bin/python3 /app/manage.py collectstatic --noinput; 

USER 1001
ENTRYPOINT ["/sbin/tini", "--"]
EXPOSE 8000 2222
CMD ["./docker_entrypoint.sh"]