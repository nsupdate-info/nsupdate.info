#!/bin/bash

# update pkg lists first, existing list items might be 404
sudo apt-get -y update

# we install a local bind9 to run the tests against:
sudo apt-get -y install bind9 bind9-dnsutils bind9-host e2fsprogs

echo "named.conf.local"
cat /etc/bind/named.conf.local
sudo cp scripts/ci/etc/bind/named.conf.local /etc/bind/
sudo chown bind.bind /etc/bind/named.conf.local

echo "named.conf.options"
cat /etc/bind/named.conf.options
sudo cp scripts/ci/etc/bind/named.conf.options /etc/bind/
sudo chown bind.bind /etc/bind/named.conf.options

sudo ln -s /var/lib/bind /etc/bind/zones
sudo cp scripts/ci/etc/bind/zones/* /etc/bind/zones/
sudo chown bind.bind /etc/bind/zones/*

sudo service bind9 restart

echo "nsswitch.conf"
ls -l /etc/nsswitch.conf
cat /etc/nsswitch.conf

echo "resolv.conf"
ls -l /etc/resolv.conf
cat /etc/resolv.conf
sudo rm -f /etc/resolv.conf
sudo cp scripts/ci/etc/resolv.conf /etc/
sudo chattr +i /etc/resolv.conf

dig @127.0.0.1 nsupdate.info SOA
dig @127.0.0.1 tests.nsupdate.info SOA
sudo netstat -tulpen | grep 53

nslookup 1.1.1.1
host 1.1.1.1
