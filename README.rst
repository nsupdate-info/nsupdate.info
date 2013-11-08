About nsupdate.info
===================

https://nsupdate.info is a free dynamic dns service.

nsupdate.info is also the name of the software used to implement it.
If you like, you can use it to host the service on your own server.

The software project lives at:
https://github.com/nsupdate-info/nsupdate.info


Features
========

* Frontend: Dynamic DNS updates via dyndns2 protocol (like supported
  by many DSL/cable routers and client software).
* Backend: Uses DYNAMIC DNS UPDATE protocol (RFC 2136) to update compatible
  nameservers like BIND, PowerDNS and others (the nameserver itself is NOT
  included).
* Easy and simple web interface.
* Multiple Hosts per user
* Add own domains / nameservers (public or only for yourself)
* Supports IP v4 and v6, SSL.
* Login with local or remote accounts (google, github, bitbucket, ...
  accounts - everything supported by python-social-auth package)
* Manual IP updates via web interface
* Shows time since last update via api, whether it used SSL or not
* Made with security in mind
* No nagging, no spamming - trying not to annoy users
* Free and Open Source Software
* Made with Python and Django
