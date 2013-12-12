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

At some places, we additionally show the result of a reverse DNS lookup ("rDNS") for your IP address(es).
If nothing shows up for an IP, the IP does not have a reverse DNS record.

We always show you the IP addresses where your requests come from. Under some circumstances, these might not be what
you expect (e.g. presence or non-presence of NAT gateways, proxies, etc.).

We detect your addresses by 2 means:

* your current remote address (where your accesses to the web interface come from) - the IP detected this way is
  immediately visible on the web interface.
* if we don't already have the IP address from the remote address, we use an invisible fake "image" that your browser
  loads from an IPv4-only or IPv6-only server - the IP detected by this method usually shows up after a few seconds.

We do some optimizations to not load these images too frequently, but also try to make sure we do not show you outdated
information about your current IP addresses.

If you don't see an IP address of some kind (v4 or v6) after a few seconds, it means you don't have that kind of
address (plus working connectivity of that kind).

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

After configuring a new update client, please keep an eye one the Faults column on the overview page.
It shows 2 values: C: <client faults> S: <server faults>

An increasing number of client faults usually means you (or the software you use) are doing something wrong
(e.g. sending updates although your IP address did not change). If you see that, please fix it!

An increasing number of server faults means there is either something wrong with the nameserver or the
connection to it or it is rejecting the updates for your hostname.


Domains
-------
If you control an own nameserver / zone, you can use the service to dynamically update it with your router / update
client.

For this, it is required that the master nameserver of that zone accepts dynamic updates (RFC 2136) using a shared
secret.

You can either privately use such an own domain or alternatively even offer them publically for all users of the service.

If you have cool domains, please offer publically!


Other Services Updaters
-----------------------

Users can associate "other services" (3rd party services) updaters with their
hosts and if we receive an update for such a host, we'll automatically send
(dyndns2) updates to these other services.

You can choose which kind of IP addresses shall be sent to the other service
using the "give IPv4" and/or "give IPv6" options.

Currently, Users can only use services that were made available by an admin
(by adding the service record using Django's admin interface).


Browser-based Update Client
---------------------------

The service has a "built-in" browser/javascript-based update client that will
query the IP and send update requests if the IP changes.

One typical scenario where this is useful:

* you are an admin for multiple, sometimes rather ad-hoc clients where you
  have to do remote support / maintenance
* the clients have no (working) dynamic dns host / updater configured
* you have prepared a hostname in the nsupdate.info service you use just
  for such scenarios, e.g. "yourname-adhoc" (+ the base domain you use)
* you need to do some remote work, but you want to avoid losing access in
  case you get disconnected and the IP changes
* you don't want to require the client to find out his/her current IP and
  communicate it to you nor do you want to remember an IP address if you can
  have a nice (and always same) hostname

How to optimize this scenario:

* go to the "yourname-adhoc" entry and use "Show Configuration"
* copy and paste the URL shown in the "Browser" tab of the configuration help
  panel, under headline "Browser-based update client"
* optional: try it yourself in your browser
* give this URL to your client (E-Mail, Chat, ...), tell the client to open it
  with a browser and keep that page open in the browser until you're finished.
* once the client has done that, "yourname-adhoc" will point to the client's IP

Note:

* we show 3 slightly different URLs:

  - the first one is generic and will use either IP v4 or v6,
  - the other 2 are specific and will either enforce usage of IP v4, or v6.
* this whole browser-based mechanism is only for adhoc and temporary use - if
  you need something permanently or repeatingly, please configure a real update
  client
* if you can't electronically give the URL to the client, you can also give:

  - URL: like above, but remove the "yourname-adhoc.basedomain:secret@" part
  - when clients visits that URL, it will ask for username and password:

    - User name: yourname-adhoc.basedomain
    - Password: secret
  - let the client check "Last update response". Should be "good" (or "nochg")
    plus same IP as shown below "My IP". If it shows something else, then there
    likely was a typo in the user name or password.
