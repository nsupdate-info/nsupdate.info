FROM python:3.14-trixie
# FROM python:3.11-alpine
WORKDIR /app

ARG HTTP_PROXY
ARG http_proxy
ARG HTTPS_PROXY
ARG https_proxy
ENV HTTP_PROXY=http://proxy.kabel-tv.de:3128
ENV http_proxy=http://proxy.kabel-tv.de:3128
ENV HTTPS_PROXY=http://proxy.kabel-tv.de:3128
ENV https_proxy=http://proxy.kabel-tv.de:3128

RUN cat /etc/resolv.conf
COPY resolv.conf /etc/resolv.conf
RUN cat /etc/resolv.conf
RUN set
RUN ps uxa
# RUN ping -c 3 10.207.18.50
# RUN apk add bind git rustc-dev cargo openssl-dev pkgconf
RUN apt-get update
RUN apt-get -y install bind9 git rustc cargo libssl-dev pkgconf
COPY bind/named.conf.local /etc/bind/named.conf.local
COPY bind/zones/ /var/lib/bind/pri/
RUN chown bind -R /var/lib/bind/pri/
RUN git config --global --add safe.directory /app
COPY pip.conf /etc/pip.conf

CMD /app/scripts/docker/test.sh
