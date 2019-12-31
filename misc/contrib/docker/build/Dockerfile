FROM debian:stable-slim
LABEL maintainer="it@nkey.com.br"

ARG BUILD=prod
ARG DOCKER_DIR=./misc/contrib/docker
ARG uwsgi_uid=700
ARG uwsgi_gid=700

ENV BUILD=$BUILD
ENV DOCKER_CONTAINER=1
ENV UWSGI_INI /nsupdate/uwsgi.ini
ENV DJANGO_SETTINGS_MODULE=local_settings
ENV DJANGO_SUPERUSER=django
ENV DJANGO_SUPERPASS=S3cr3t
ENV DJANGO_EMAIL=django@nsupdate.localdomain
ENV SERVICE_CONTACT=hostmaster@nsupdate.localdomain
ENV SECRET_KEY=S3cr3t
ENV BASEDOMAIN=nsupdate.localdomain
ENV REGISTRATION_OPEN=False

RUN mkdir /static
RUN mkdir /upload
RUN mkdir /var/run/uwsgi

# Install runtime tools
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y --no-install-recommends \
      python3 \
      python3-setuptools \
      python3-pip

# Install confd
RUN apt-get install -y --no-install-recommends wget \
    && mkdir -p /usr/local/bin \
    && wget -O /usr/local/bin/confd https://github.com/kelseyhightower/confd/releases/download/v0.16.0/confd-0.16.0-linux-amd64 \
    && chmod +x /usr/local/bin/confd \
    && mkdir -p /etc/confd/{conf.d,templates} \
    && apt-get autoremove -y wget

# Use local version of nsupdate from sources
COPY ./*.py /nsupdate/
COPY ./*.rst /nsupdate/
COPY ./*.in /nsupdate/
COPY ./*.cfg /nsupdate/
COPY ./*.txt /nsupdate/
COPY ./requirements.d/ /nsupdate/requirements.d/
COPY ./.git/ /nsupdate/.git/
COPY ./src/ /nsupdate/src/
WORKDIR /nsupdate

# Build and install
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y --no-install-recommends \
      git \
      python3-dev \
      build-essential \
      libpcre3-dev \
    && pip3 install wheel \
    && python3 setup.py bdist_wheel \
    && pip3 install psycopg2-binary uwsgi \
    && pip3 install -r requirements.d/$BUILD.txt \
    && pip3 install -e . \
    && cp /usr/lib/x86_64-linux-gnu/libpython* /tmp \
    && apt-get autoremove -y \
      git \
      python3-dev \
      build-essential \
      libpcre3-dev \
    && cp /tmp/libpython* /usr/lib/x86_64-linux-gnu/ \
    && rm -rf build \
    && rm -rf .git && rm -rf /root/.cache \
    && rm -rf /tmp/* /var/tmp/* \
    && rm -rf /var/lib/apt/lists/*

# Copy helper files
COPY $DOCKER_DIR/build/django/create-superuser.py /nsupdate/src/nsupdate/management/commands/create-superuser.py
COPY $DOCKER_DIR/build/uwsgi.ini /nsupdate/uwsgi.ini
COPY $DOCKER_DIR/build/confd/ /etc/confd/
COPY $DOCKER_DIR/build/setup.sh /
COPY $DOCKER_DIR/build/docker-entrypoint.sh /var/local/

# Set the permissions according to env options
RUN chmod a+x /var/local/docker-entrypoint.sh
RUN bash /setup.sh "${uwsgi_uid}" "${uwsgi_gid}"

VOLUME /nsupdate
VOLUME /static
VOLUME /upload
VOLUME /var/run/uwsgi

EXPOSE 3031
EXPOSE 8080

ENTRYPOINT ["/var/local/docker-entrypoint.sh"]
