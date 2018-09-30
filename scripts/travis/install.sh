#!/bin/bash

# update pkg lists first, existing list items might be 404
sudo apt-get -y update

# we install a local bind9 to run the tests against:
sudo apt-get -y install bind9 dnsutils e2fsprogs

sudo ln -s /var/lib/bind /etc/bind/zones
sudo cp scripts/travis/etc/bind/named.conf.local /etc/bind/
sudo chown bind.bind /etc/bind/named.conf.local
sudo cp scripts/travis/etc/bind/zones/* /etc/bind/zones/
sudo chown bind.bind /etc/bind/zones/*
sudo service bind9 restart

sudo dpkg -P ubuntu-minimal resolvconf
sudo rm -f /etc/resolv.conf
sudo cp scripts/travis/etc/resolv.conf /etc/
sudo chattr +i /etc/resolv.conf

#dig @127.0.0.1 nsupdate.info SOA
#dig @127.0.0.1 tests.nsupdate.info SOA
#sudo netstat -tulpen | grep 53

pip install Django~=$DJANGO
pip install -r requirements.d/travis.txt
pip install -e .
