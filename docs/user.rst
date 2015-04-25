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

Alternatively, you can also run a software on a PC / server (like ddclient or inadyn for Linux).

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

Your current IP(s) + reverse DNS
--------------------------------

We show your current IP address(es).
Depending on the type of your internet connection, this can be IP v4 or v6 or both (dual stack).
If nothing shows up, you don't have that kind of IP address.

We additionally show the result of a reverse DNS lookup ("rDNS") for your IP address(es).
If nothing shows up, that IP does not have a reverse DNS record.

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

We'll also use that E-Mail address in case you forget your login password or when there are technical issues
with your hosts or domains.

For your own safety, use https and a sane password.

Be careful: in case you lose your login username/password and you also can't receive mail sent to the E-Mail address
you gave when registering, you might not be able to regain access to your account / your hosts (neither automatically
nor with help from service admin) as you likely can't prove that they are really yours / you are permitted to
control them.

Overview
--------
We show a list of your hosts and also available (public) domains as well as your domains (if any).

You can see the most important data directly on the overview page. If you need more details or you want to change
something, click on the host or domain you want to see / edit.

You can also add hosts and domains by clicking on the respective button.

You can always get back to the overview page by clicking on the link in the navigation bar.

Adding Hosts
------------
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

At the bottom of the host view, we also show the last result messages for authentication (of course only if at can be
related to that host), for the client result, for the server result. Check if everything looks ok there.

Adding Domains
--------------
If you control an own nameserver / zone, you can use the service to dynamically update it with your router / update
client.

For this, it is required that the master nameserver of that zone accepts dynamic updates (RFC 2136) using a shared
secret. If you run your own bind9 nameserver for your domain, we show you how to configure it for dynamic updates
after you add a domain on nsupdate.info.

You can either privately use such an own domain or alternatively even offer them publically for all users of the service.

If you have cool domains, please offer publically!

Note: if you just register a domain at some domain seller (and the domain seller runs the DNS for you), you usually
just get some web interface to manage the DNS records. Often, that nameserver is not configured to accept dynamic
updates (RFC 2136) unless otherwise noted by your DNS hoster. If unsure, read their documentation, examine their
web interfaces (if they allow dynamic updates, there should be some means to configure or see the update algorithm,
secret and maybe even the update policy (where you can setup rules to allow/deny specific hosts) or just ask them.

If your DNS hoster does not support dynamic updates, there is some trick how you still can use them:

::

    # configure this for your domain at your DNS hoster:
    dynamichost.yourdomain.com  CNAME  updatedhost.nsupdate.info

At the nsupdate.info site, add a host "updatedhost.nsupdate.info" and keep it updated using an update client.


Related Hosts
-------------

In short: update a whole bunch of DNS records for other hosts on same LAN.

This is a feature most interesting for IPv6 users, but the same mechanism also
works for IPv4 (it is just rather rare that you get a IPv4 network and you need
dynamic DNS). So, let's assume IPv6 from now on.

On your main host entry you can configure the IPv6 prefix length (think of netmask).
Usually you'll get a /64 network from your ISP, so keep the default of "64" there
and only change it if you know better.

The specific prefix you get from your ISP might be static or may change now and
then (for better privacy or other reasons - and in that case, you really need
the related hosts feature).

You need to configure a dyndns2 compatible updater on some device on your LAN
and the updater needs to send this device's global IPv6 address to the service.

So far, nothing special, upon receiving an update the service will then update
DNS like this:

::

    mainhost.nsupdate.info -> pppp:pppp:pppp:pppp:iiii:iiii:iiii:iiii

p are prefix parts, i are host/interface parts of the address.

Additionally, the service will go over all related hosts entries for mainhost
and does more DNS updates based on this computation:

::

    relatedhost.mainhost.nsupdate.info -> pppp:pppp:pppp:pppp:rrrr:rrrr:rrrr:rrrr

You also see it prepends the related host's name to your mainhost's FQDN.

For the related hosts's address, p is same prefix as above (the host is on same
network), but r comes from what you entered as interface ID into the related
host record.

The interface ID must be a proper notation.
For IPv6 a interface ID might look like `::rrrr:rrrr:rrrr:rrrr`,
for IPv4 a interface ID might look like `r.r.r.r`.

If you leave the interface ID field empty, that means not to create such a DNS record.

In other words:

::

    related_fqdn = relatedhost_name.mainhost_fqdn
    related_address = mainhost_address_prefix + interface_id


Note:

* enter the static interface ID (usually you can get it from the rear 4 words
  of the address that looks like FE80::rrrr:rrrr:rrrr:rrrr). The r part is
  usually derived from your hardware MAC address and does not change.
* make sure your device has a IPv6 address with global scope, some prefix that
  starts with a "2" and precisely that rrrr:rrrr:rrrr:rrrr value
* you only need a dyndns2 updater on one device (called mainhost in this
  example), but the updater needs to find out an address with the same prefix
  as seen on your LAN (should be easy if the updater runs on a LAN device, but
  might be difficult if it runs on the router and the router has a different
  external prefix)
* if you want your mainhost to resolve correctly to some specific device,
  make sure you send this device's IPv6 address with the update (myip=...) or
  run the updater on that device and make sure the request originates from
  the IPv6 address you want in DNS.


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


Troubleshooting
===============

Look here first if it doesn't work
----------------------------------

On the web interface, find the not working host in the overview's host list.

What does the "available" and "faults c/s" column say?

* if your host is not available, it can't be updated (visit host view to make
  it available)
* if you see increasing client faults count, your update client is doing something
  wrong. in the end, that might flag that host as abusive: you'll see "abuse" or
  "abuse_blocked" in that case (visit host view to deselect "abuse" flag).

Now click on the hostname to go to the detailled host view.

There, at the bottom, you will see the last messages that were generated about
your client (whether it is updating ok or causing errors/warnings) and about
the domain's DNS server (in case it can't be reached or is malfunctioning or
rejects updates). The date/time given is UTC.

But please note: we can not show you issues with your credentials there (like
when you configured your update client with wrong values for http basic authentication).


Address update for your host is not working (and never worked)
--------------------------------------------------------------

Check your update client settings again:

* typos? additional spaces somewhere? this is sometimes hard to see.
* keep in mind that when we create and show you a new update secret, the old one becomes invalid.
* the updater uses your host's fqdn and the update secret as credentials,
  NOT your service web site username / password.
* if the https update URL does not work, try http - especially for older software.

Address update for your host is not working (but worked before)
---------------------------------------------------------------

If this is the case, first check these things (and then the ones listed above):

* if you use an updater that does not conform to the dyndns2 standard, it might be that your host got flagged as
  abusive. Go to the detailled view of your host and see whether abuse is checked. If it is, fix / change your
  updater then uncheck the abuse flag and save.
* if the client fault counter on the overview page keeps rising, you didn't fix the issue - try again.
* if it keeps getting flagged as abusive, you didn't fix the issue - try again.
* if you have a local network with multiple machines that shared one internet connection, it is sufficient to enable
  an update client on one of the machines (preferably your internet router or a machine that is on most of the time).
  if you run update clients on multiple machines, this may cause them sending nochg updates frequently and your host
  might get flagged as abusive due to that.

Something else?
---------------

* read the hints and on-screen help the service shows to you, including the footer stuff.
* if nothing else helps, contact the service administrator.
* if you think you have found a bug in the software, file it on the project's issue tracker on github (after doing
  a quick check whether such a bug has already been reported or even fixed).


Update clients
==============

It is important that you run a dyndns2 standards compliant software to update your host.

Recommended
-----------

Here are some clients that likely qualify:

* ddclient

  - we offer configuration help for it, just copy & paste
  - good working, reliable
  - the official version is IPv4 only, IPv6 support needs a patched version
  - Linux & other POSIX systems
* inadyn (>= 1.99.11)

  - we offer configuration help for it, just copy & paste
  - good working, reliable
  - IPv4 only
  - Linux & other POSIX systems
* python-dyndnsc

  - still alpha/beta, but works
  - IPv4 and good IPv6 support
  - Mac OS X, Linux and FreeBSD
* whatever your router / gateway / firewall has for dyndns / ddns

  - quality of update client implementations varies widely
  - running on the system that has your public IP makes updating your host when your IP changes easier
  - no need to run additional software on other machines in that network
* nsupdate-info's browser-based updater

  - only for adhoc scenarios, not intended for long term use
  - runs in your browser with javascript

Known-Problematic
-----------------

These clients or update methods have known issues or are not dyndns2 standards compliant.
This likely causes unnecessary load on the service servers and network.

You should not use these:

* a cron job + wget or curl

  - will either send nochg updates frequently (your host will get flagged as abusive)
  - or it will be very slow reacting to IP changes
* your self-written not fully standards compliant update client software

  - it looks simple first, but to fully comply is more effort
  - if you're not willing to fully comply, then don't even start
  - there are already enough badly implemented and also "almost compliant" updaters out there
  - rather try to use well-behaved existing update software
  - or try to improve the "almost compliant" existing update software
