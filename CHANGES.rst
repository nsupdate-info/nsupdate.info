ChangeLog
=========

Release 0.5.0
-------------

Important note (only for upgrades):

There is an issue if you use "south" and the "sqlite" database - it can't
add BooleanFields and set the default values correctly when using "migrate".

As we added some critical fields, you need to use these commands immediately
after running "django-admin.py migrate" to make sure their initial values are
correct::

    # all hosts will be available, no host will have abuse flags set:
    django-admin.py faults --reset-available --reset-abuse --reset-abuse-blocked

Fixes:

* use python-social-auth exception middleware to catch exceptions
* status view is for logged-in users only (it was removed from navigation,
  but still accessible by URL in previous releases)
* fix session cookie behaviour to be more private for not-logged-in users

New Features:

* "update other services" feature (act as dyndns2 client to update 3rd party
  services when we receive an update)
* added per-host fault counters for update client and dns server
* abuse handling (for clients triggering too many faults) using the "faults"
  management command
* abuse-blocked / abuse / unavailable counts on status view
* notfqdn and abuse dyndns2 api result codes supported
* show reverse DNS of current IPs (only on host overview)
* customizable footer (use a custom base_footer.html template)

Other changes:

* use sane field lengths in the DB
* more help texts, more hints, better docs
* workflow for adding a domain is now similar to adding a host
* improved user interface
* use travis-ci and coveralls services for the project
* updated bootstrap to 3.0.2 (from cdn)


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
