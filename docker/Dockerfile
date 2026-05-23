FROM python:3.11-bookworm
#LABEL maintainer="kevin@meredithkm.info"

ARG BUILD=prod
ARG uwsgi_uid=700
ARG uwsgi_gid=700

ENV BASEDOMAIN=nsupdate.localdomain
ENV BUILD=$BUILD
ENV DATABASE_URL="sqlite:////config/nsupdate.sqlite"
ENV DJANGO_EMAIL=django@nsupdate.localdomain
ENV DJANGO_SETTINGS_MODULE=local_settings
ENV DJANGO_SUPERPASS=S3cr3t
ENV DJANGO_SUPERUSER_EMAIL="admin@localhost.localdomain"
ENV DJANGO_SUPERUSER_PASSWORD="admin"
ENV DJANGO_SUPERUSER_USERNAME="admin"
ENV DOCKER_CONTAINER=1
ENV SECRET_KEY=S3cr3t
ENV SERVICE_CONTACT=hostmaster@nsupdate.localdomain
ENV UWSGI_INI=/nsupdate/uwsgi.ini
ENV PYTHONPATH="/nsupdate/src"

RUN mkdir /config

# Install python3 and pip
RUN DEBIAN_FRONTEND=noninteractive apt update \
    && apt install -y --no-install-recommends \
       git 
RUN  git clone https://github.com/nsupdate-info/nsupdate.info.git /nsupdate \
  && cd /nsupdate/ \
  && pip install -r requirements.d/prod.txt \
  && pip install -e .

COPY local_settings.py.default /nsupdate/src/local_settings.py
RUN django-admin migrate \
  && django-admin createsuperuser --noinput

RUN rm -rf /tmp/* /var/tmp/* \
    && rm -rf /var/lib/apt/lists/*


EXPOSE 8000

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

VOLUME ["/config"]

#ENTRYPOINT ["django-admin", "runserver"]
#ENTRYPOINT ["python3", "/nsupdate/manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT ["/docker-entrypoint.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
RUN pip install  django-xff
RUN pip install whitenoise
RUN django-admin collectstatic --noinput
