=================
Using the service
=================

Requirements
============

Update client
-------------
The best way to use the service for updating a hostname with a dynamic address is to have a dyndns2 compatible
update client.

Usually this kind of software is built-in in your internet router (search for "dynamic DNS", "DDNS", "dyndns" on
its user interface).

Alternatively, you can also run a software on a PC / server (like ddclient for Linux).

Or even just use your browser to update your IP via the web interface of the service.

Note: please do not "update" your IP address if it did not change. Doing so is considered abusive use of the service.
All sane dyndns2 clients only send an update if the IP address has changed.

Web interface
-------------
When using a browser for administrating your hosts / domains via the web interface of the service, please:

* use https (for security)
* have cookies enabled (we need them for keeping the session after you logged in)
* have javascript enabled
* use a sane browser, like Firefox, Chrome/Chromium or Safari

Functionality of the Web Interface
==================================

Your current IP(s)
------------------

At some places, we show your current IP address(es). Depending on the type of your internet connection, this can be
IP v4 or v6 or both (dual stack).

We always show you the IP addresses where your requests come from. Under some circumstances, these might not be what
you expect (e.g. presence or non-presence of NAT gateways, proxies, etc.).

We detect your IPv4 and v6 addresses in the same way (no matter what you currently use to look at the web interface)
using 2 invisible fake "images" that your browser loads from a IPv4-only and a IPv6-only server.

We do some optimizations to not load these images too frequently, but also try to make sure we do not show you outdated
information about your current IP addresses.

If you don't see an IP address of some kind (v4 or v6) after a few seconds, it means you don't have that kind of address.

Register / Login / Logout
-------------------------
You need to create an account to use most of the functionality of the service.

Your hosts / domains are only for you, so you need to identify to create or change them.

You need to give a valid E-Mail address, as we send you a link you need to access to complete the registration.

We'll also use that E-Mail address in case you forget your login password.

For your own safety, use https and a sane password.

Hosts
-----
You can add hosts to all the zones (base domains) offered to you.
Usually this will be one or more zone(s) offered by the service operator, but you can even add your own domains
(see the separate section about domains).

After creating a new dynamic host name, we'll show you an automatically created update secret for that host.
You need it for configuring your update client and we show you example configurations for some popular routers and
clients on the same page.

In case you lose the update secret, just create a new one (and enter it in your router / update client).

IP v4 and v6 addresses work completely independently of each other, you need to send 2 updates if you want to update
both. If you want to be specific about which IP address you update, use our IPv4-only or IPv6-only host to make sure
it is the v4 (or v6) address.

Domains
-------
If you control an own nameserver / zone, you can use the service to dynamically update it with your router / update
client.

For this, it is required that the master nameserver of that zone accepts dynamic updates (RFC 2136) using a shared
secret.

You can either privately use such an own domain or alternatively even offer them publically for all users of the service.

If you have cool domains, please offer publically!
