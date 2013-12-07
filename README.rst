About nsupdate.info
===================

https://nsupdate.info is a free dynamic dns service.

nsupdate.info is also the name of the software used to implement it.
If you like, you can use it to host the service on your own server.

The software project lives at:
https://github.com/nsupdate-info/nsupdate.info


.. image:: https://travis-ci.org/nsupdate-info/nsupdate.info.png
    :target: https://travis-ci.org/nsupdate-info/nsupdate.info

.. image:: https://coveralls.io/repos/nsupdate-info/nsupdate.info/badge.png
        :target: https://coveralls.io/r/nsupdate-info/nsupdate.info

.. image:: https://badge.fury.io/py/nsupdate.png
    :target: http://badge.fury.io/py/nsupdate

.. image:: https://pypip.in/d/nsupdate/badge.png
        :target: https://crate.io/packages/nsupdate/

Features
========

* Frontend: Dynamic DNS updates via dyndns2 protocol (like supported
  by many DSL/cable routers and client software).
* Backends:

  - Uses DYNAMIC DNS UPDATE protocol (RFC 2136) to update compatible
    nameservers like BIND, PowerDNS and others (the nameserver itself is
    NOT included).
  - Optionally uses dyndns2 protocol to update other services - we can
    send updates to configurable 3rd party services when we receive an
    update from the router / update client.

* Prominently shows visitor's IPs (v4 and v6) on main view,
  shows reverse DNS lookup results (on host overview view).
* Multiple Hosts per user (using separate secrets for security)
* Add own domains / nameservers (public or only for yourself)
* Login with local or remote accounts (google, github, bitbucket, ...
  accounts - everything supported by python-social-auth package)
* Manual IP updates via web interface
* Browser-based update client for temporary/adhoc usage
* Shows time since last update via api, whether it used SSL or not
* Shows v4 and v6 IP addresses (from master nameserver records)
* Shows client / server fault counters, available and abuse flags
* Supports IP v4 and v6, SSL.
* Easy and simple web interface, it tries to actively help to configure
  routers / update clients / nameservers.
* Made with security and privacy in mind
* No nagging, no spamming, no ads - trying not to annoy users
* Free and Open Source Software, made with Python and Django
