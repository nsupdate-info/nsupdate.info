#!/bin/sh

set -euxo pipefail

cd /tmp && named -g -u named -c /etc/bind/named.conf.local &

cd /app
pip install -e .
pip install -r requirements.d/dev.txt

pylint src/nsupdate
pytest src/nsupdate
