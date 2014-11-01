ChangeLog
=========

Release 0.9.0
-------------

Note: 0.9 is the last release with Django 1.6.x support, we'll remove support
for it in 0.10 (because Django 1.7 has some implications that make it hard to
support 1.6 and 1.7).

New Features:

* Related Hosts: support updating DNS records of other hosts in same LAN by
  a single updater (e.g. for IPv6 with changing prefix, IPv4 also works)
* Handle IPv4-mapped IPv6 addresses
  Some reverse proxy configurations pass REMOTE_ADDR as a IPv4-mapped IPv6
  address when listening on a IPv6 socket.
  We now convert such a mapped address into a IPv4 address at all usages.
  Handles both the ::ffff:192.0.2.128 format as well as the deprecated
  ::192.0.2.128 format.
* add "inadyn" dyndns updater to configuration help

Fixes:

* catch Timeout exceptions

Other changes:

* updated / added some translations


Release 0.8.0
-------------

Note: 0.8 is the last release with Django 1.5.x support, we'll remove support
for it in 0.9. Django 1.5 is also EOLed from Django Project, so upgrade your
Django soon.

New Features:

* redesigned UI:

  * unify hosts and domains overview into 1 view
  * move forms to add hosts/domains to own views
  * move reverse DNS display to home view
  * removed some superfluous links and formatting
* host view: give more feedback about client/server results on the web UI,
  so a user can see why updates are not working (even if some stupid update
  client does not tell him).
  But please note: if you fail to configure your credentials correctly in your
  update client, we can NOT show that there as we need them to load your host
  record from the database (and to know it is really YOU who is talking to us).
* add OpenWRT configuration help
* add search field to Host and Domain admin

Fixes:

* fixed Python 3 incompatibility of Basic Auth code (issue #172)
* fix security issue: abuse_blocked flag could be worked around by abuser
* refactored internal api so host/zone boundary is not lost and does not need
  to be discovered (we KNOW it) - fixes issues #122 and #138.
* fixed tests so they behave on travis-ci
* fix unhandled PeerBadTime exception

Other changes:

* form field help texts are translatable now
* admin views: added "created", removed "created_by" filter (does not scale)


Release 0.7.0
-------------

Important notes:

* WE_HAVE_SSL configuration setting name was changed to WE_HAVE_TLS.
  Please update your configuration, if you use it.
* Django 1.6.x required now, if you want to use 1.5.x: see setup.py

New Features:

* i18n support (uses preferred language from UI or browser)
* fr/de/it translations added
* translations are on transifex, you can help there!
  https://www.transifex.com/projects/p/nsupdateinfo/
* add m0n0wall configuration help
* add pfSense configuration help
* implemented host delete API at /nic/delete to remove A or AAAA record in DNS
  (very similar to the dyndns2 update api, which does not offer this)
* host delete functionality on web UI
* custom templates (for legalese, site-specific notes, etc. - see docs for
  details)
* abuse / abuse blocked flags + script support (see docs)
* notification by email if host gets flagged as abusive
* show example zone file for bind9 after adding a new domain
* better display in the admin
* enabled Django's clickjacking protection middleware in settings

Fixes:

* fix some status 500 errors / unhandled exceptions:

  * when domain does not exist
  * on profile view when not logged in
  * DnsUpdateError (e.g. SERVFAIL)
  * NoNameservers exception
  * UnknownTSIGKey exception
  * "Network is unreachable" error
  * empty ?myip=
  * invalid ip address strings in updates (now: "dnserr")

* fix html validation errors
* fix login url generation in activation_complete template, issue #139
* switch off recursion when querying master dns, issue #142
* fix --reset-available cmdline option processing
* updated dd-wrt configuration with verified settings

Other changes:

* also support Python >= 3.3 (experimental, please give feedback)
* improve looks, UI / UX
* improve docs, sample configs
* remove requirements from setup.py that were only for development
* removed view for legalese (please solve locally, according to your law -
  you can use custom templates for this)
* added some ugly logos (if you can do better ones, please help)
  https://github.com/nsupdate-info/nsupdate.info/issues/78
* replaced "SSL" by "TLS" everywhere.      
  SSL is the old/outdated name. Since 1999, it's called TLS.
* updated to latest versions on CDN: jquery, bootstrap, font-awesome


Release 0.6.0
-------------

Important notes:

* importing from nsupdate.settings does not work any more (nor
  does the nsupdate.local_settings hack work any more).
  in your local_settings.py, please do your imports like this::

      from nsupdate.settings.dev import *   # for development
      # alternatively:
      from nsupdate.settings.prod import *  # for production
      # after that, override whatever you need to override.

* if you run Django 1.6.x, you manually need to apply a patch for
  django-registration (until that package is fixed for django 1.6
  compatibility), see the django-registration-dj16-fix.diff in the toplevel
  directory of the repo.

New Features:

* browser/javascript-based update client (the URL you need is shown in the
  "browser" help panel after you add a host or generate a new secret).

Other changes:

* cleaned up how settings work, improved docs about a sane settings setup
* document postgreSQL setup
* also support Python 2.6.x
* also support Django 1.6.x
* for debugging, added django-debug-toolbar


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
