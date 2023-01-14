FROM python:3.11-alpine
WORKDIR /app

RUN apk add bind git
COPY bind/named.conf.local /etc/bind/named.conf.local
COPY bind/zones/ /var/lib/bind/pri/
RUN chown named -R /var/lib/bind/pri/

CMD /app/scripts/docker/test.sh
