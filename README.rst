About nsupdate.info
===================

https://nsupdate.info is a free dynamic DNS service.

nsupdate.info is also the name of the software used to implement it.
If you like, you can use it to host the service on your own server.

Documentation: https://nsupdateinfo.readthedocs.io/

Software project: https://github.com/nsupdate-info/nsupdate.info

|doc| |build| |coverage| |package|

.. |doc| image:: https://readthedocs.org/projects/nsupdate/badge/?version=stable
        :alt: Documentation
        :target: https://nsupdateinfo.readthedocs.io/en/stable/

.. |build| image:: https://api.travis-ci.org/nsupdate-info/nsupdate.info.svg
        :alt: Build Status
        :target: https://travis-ci.org/nsupdate-info/nsupdate.info

.. |coverage| image:: https://coveralls.io/repos/nsupdate-info/nsupdate.info/badge.png
        :alt: Test Coverage
        :target: https://coveralls.io/r/nsupdate-info/nsupdate.info

.. |package| image:: https://badge.fury.io/py/nsupdate.png
        :alt: PyPI Package
        :target: http://badge.fury.io/py/nsupdate

(build and coverage are for latest repo code, package and downloads are for PyPI release)

Features
========

* Frontend: Dynamic DNS updates via dyndns2 protocol (like supported
  by many DSL/cable routers and client software).
* Backends:

  - Uses Dynamic DNS UPDATE protocol (RFC 2136) to update compatible
    nameservers like BIND, PowerDNS and others (the nameserver itself is
    **not** included).
  - Optionally uses the dyndns2 protocol to update other services - we can
    send updates to configurable third-party services when we receive an
    update from the router / update client.

* Prominently shows visitor's IP addresses (v4 and v6) on main view,
  shows reverse DNS lookup results (on host overview view).
* Multiple Hosts per user (using separate secrets for security)
* Add own domains / nameservers (public or only for yourself)
* Related Hosts: support updating DNS records of other hosts in same LAN by
  a single updater (e.g. for IPv6 with changing prefix, IPv4 also works)
* Login with local or remote accounts (Google, GitHub, Bitbucket, ...
  accounts - everything supported by the python-social-auth package)
* Manual IP updates via web interface
* Browser-based update client for temporary/adhoc usage
* Shows time since last update via API, whether it used TLS or not
* Shows IP v4 and v6 addresses (from master nameserver records)
* Shows client / server fault counters, available and abuse flags
* Supports IP v4 and v6, TLS.
* Easy and simple web interface, it tries to actively help to configure
  routers / update clients / nameservers.
* Made with security and privacy in mind
* No nagging, no spamming, no ads - trying not to annoy users
* Free and open source software, made with Python and Django
