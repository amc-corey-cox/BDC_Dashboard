FROM ghcr.io/translatorsri/renci-python-image:3.11.5

ARG TINI_VERSION=v0.19.0

ENV APP_HOME=/app \
  PYTHONUNBUFFERED=1

WORKDIR ${APP_HOME}

USER root
RUN apt-get update
RUN apt-get install -y wget gcc zlib1g-dev libssl-dev libffi-dev libpq-dev git make tzdata
RUN wget -O /sbin/tini https://github.com/krallin/tini/releases/download/$TINI_VERSION/tini

COPY api ./
COPY .env .

RUN pip3 install wheel
RUN pip3 install -r requirements.txt
RUN python3 /app/manage.py collectstatic --noinput

RUN chmod a+w ${APP_HOME}/tracker/migrations
RUN chmod 755 /sbin/tini ${APP_HOME}/docker_entrypoint.sh
RUN chown -R nru:nru ${APP_HOME}

EXPOSE 8000 2222

USER nru

ENTRYPOINT ["/sbin/tini", "--"]
#CMD sleep 2000
CMD [ "/bin/bash", "-c", "./docker_entrypoint.sh"]
