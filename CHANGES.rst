ChangeLog
=========

Release <TBD>
-------------

Fixes:

* status view is for logged-in users only (it was removed from navigation,
  but still accessible by URL in previous releases)

New Features:

* added per-host fault counters for update client and dns server
* customizable footer (use a custom base_footer.html template)
* notfqdn result code supported

Other changes:

* use sane field lengths in the DB
* more help texts, more hints, better docs
* workflow for adding a domain is now similar to adding a host
* improved screen layout, cosmetics
* use travis-ci and coveralls services for the project


Release 0.4.0
-------------

Fixes:

* fix api return value (no "noauth", just "badauth")
* fix invalid /detectip/None URL for fresh session
* make IP detection on the web UI a bit more reliable
* fix KeyErrors in logging (at least for default format)


New Features:

* use REMOTE_ADDR for one of the 2 IP detections
* add a warning on the UI if the user has no javascript enabled
* use real session cookies by default (that get cleared on browser close)
* support "keep me logged in" if user wants a permanent 14d cookie
* use html5 autofocus to put cursor into the right input field
* python manage.py testuser to reinitialize test user (see docs)


Other changes:

* document clearsessions usage
* more tests


Release 0.3.0
-------------

* Fixes security issue
  https://github.com/nsupdate-info/nsupdate.info/issues/81
* improved logging levels, added log output at some places
* dnserr dyndns2 result supported
* more safe bind9 configuration example
* support for single-host update secrets
* make dnstools unit tests work everywhere
* remove beta from version number (but keep general beta state in pypi
  classifier)


Release 0.2.0b0
---------------
First release on PyPi.
