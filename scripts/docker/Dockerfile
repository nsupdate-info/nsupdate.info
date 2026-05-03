FROM python:3.11-alpine
WORKDIR /app

RUN apk add bind git rustc-dev cargo openssl-dev pkgconf
COPY bind/named.conf.local /etc/bind/named.conf.local
COPY bind/zones/ /var/lib/bind/pri/
RUN chown named -R /var/lib/bind/pri/
RUN git config --global --add safe.directory /app

CMD /app/scripts/docker/test.sh
