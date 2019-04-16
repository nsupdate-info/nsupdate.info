ChangeLog
=========

Important: when you update and your update crosses the 0.9.x / 0.10 boundary,
you must first upgrade to 0.9.x and your database must be migrated to 0.9.x.
AFTER that, you can upgrade to 0.10.x or any later version (and then run the
migrations for that version). For upgrading and migration help, please see
the docs that match the version you are upgrading to.


Release 0.13.0 (not released yet)
---------------------------------

New Features:

- add BAD_HOSTS setting to lock out nasty clients from the update api
  without causing database accesses.
- django-admin faults: show/reset api auth faults counter
- add api_auth_faults column to django admin's Hosts view

Fixes:

- fixed misc. crashes

Other changes:

- drop support for python 3.4, fixes #406 - you need either 2.7 or 3.5+.
- require django >= 1.11.0, run travis-ci tests on django 2.2
- django compatibility improvements
- translation updates (removed incomplete ones, added complete ones)
- improve logging
- setuptools-scm managing the version and manifest
- src/ based project layout
- Add A Well-Known URL for Changing Passwords
- Add rel="noopener" to target="_blank" links


Release 0.12.0 (2018-11-18)
---------------------------

New Features:

* Related Hosts: leave v4 or v6 interface ID empty to not create a DNS record
* added configuration help for:

  - IPfire, #209
  - EdgeOS, #86
  - Speedport Hybrid, #286
  - dyndnsc
* avoid domains vs. hosts confusion - check dns availability, #168
* add a simple domain name validator, #308
* admin: sort host and domains by name
* validate (domain of) email address in registration form, #284
* implement django-admin domains --stale-check


Fixes:

* exception "IPAddress() does not support netmasks or subnet prefixes", #223
* Traceback on DNS server Timeout, #211
* emails should mention fqdn, #225
* TemplateDoesNotExist exception, #222
* "faults" management command: use atomic transaction PER HOST, #208
* avoid that invalid domains get added, #205
* fix traceback when language in user profile is None, #206
* fix traceback when using a malformed nameserver secret, #213
* upgrade django-registration-redux, fixes pw reset, #250 #251 #252
* check_domain fixes: #246, #249, #253
* test updates when a domain is set to available, #168
* unicode error under python2.7, #242
* fix SameIpError in host add form processing, #267
* fix first param type of loader.select_template, #255
* api basic auth - ignore non-utf8 chars, #282
* fix crash on ShortHeader and other DNSException subclasses, #247
* more clear dns server configuration check error msg, #278
* update DD-WRT config instructions, #300
* update pfSense tab to get IP from Result Match
* avoid invalid IP address crash, #394
* new host creation: set update timestamps to current time, #357
* remove hardcoded db session engine, use SESSION_ENGINE
* Python 3.7 and Django 2.x related fixes/changes

  - use new MIDDLEWARE setting (since Django 1.10) instead of MIDDLEWARE_CLASSES
  - setup.py: don't require a specific Django version, so 1.1 and 2.x works
* add ugly workaround for crash in django-admin users --stale-check
* django-admin.py users: avoid unicode issues by using %r, #350
* django-admin.py users: initialize log_msg
* no exceptions when context processor saves the session, #356
* use a much simpler errorpage.html template, related to #356 #365
* catch exceptions of dns.tsigkeyring.from_text(), #338, #319
* do not strip interface_id_ipv(4|6) if empty/None, #355
* use same cleaning for the secret in (Create|Edit)DomainForm, #338
* django-admin domains --check: catch UnknownTSIGKey, #336
* transform UnknownTSIGKey into DnsUpdateError, #337
* fix placeholders in domains management script
* work around UnknownTSIGKey exception blowing up the overview view


Other changes:

* dropped support for Python 3.3
* added support for Python 3.6 and 3.7
* update django requirement to ~=1.11.0 (LTS), #293
* update django links in admin docs to point to 1.11
* travis:

  - drop: py33, add: py35, py36, py36-dev, py37
  - test on trusty with sudo, against local bind9 dns
  - test always using latest Django 1.11 minor version
* pip: remove --use-mirrors
* use TEMPLATES setting for Django 1.8+, remove outdated TEMPLATE_*
* use www.BASEDOMAIN for WWW_HOST, prepare for #224
* added "nsupdate.info" to publicsuffix.org,
  this is needed to not run into rate limiting with letsencrypt.org.
* zone creation: add hint about public suffix list
* upgrade django-registration-redux, python-social-auth
* upgrade Font Awesome, Bootstrap, jQuery
* add subresource integrity, #23
* use other cdn for Bootstrap
* set SECRET_KEY in development configuration
* add some words about DNSSEC to the docs, #26
* do not use html registration emails
* optimize database query on overview page
* sort hosts and domains by name, #192
* update inadyn configuration to 2.1
* update OpenWrt config example for Chaos Calmer, #259
* update badges, new readthedocs.io url
* use error views without templating, #365
* shorter default session expiry, #381


Release 0.11.0 (2015-02-15)
---------------------------

New Features:

* Hosts: show client authentication error/success on the host view
* Domains: support optional secondary nameserver - if given, prefer it for
  DNS queries
* implement host IP blacklist, fixes #162
* implement host staleness level + management script to check whether host IP
  is being updated
* add language to user profiles
* add registration_closed template

Fixes:

* catching more exceptions
* misc. UI fixes / improvements
* misc. python3 compatibility fixes / improvements
* fix resolving to not add the service server's domain, but just "."
* timeout / retry timings adjusted
* "Login" button at end of user registration does not work #183
* catch IndexError when computing IP of related hosts, fixes #190
* catch socket.error (e.g. "connection refused"), fixes #195

Other changes:

* made form field labels translatable, added translations, added plurals
* added tuning tips section to admin docs (not much yet)
* some internal cleanups / refactorings
* use templated error pages for 400,403,404,500 http status codes
* upgraded CDN links for bootstrap, jquery, font-awesome


Release 0.10.0 (2014-11-17)
---------------------------

New Features:

* if the abuse / abuse_blocked flag is set for a host, it is removed from DNS
* users can delete their accounts, if they want to stop using the service
  (all hosts, domains, etc. created by this user will be deleted)
* added admin UI for Related Hosts
* added "domains" management command to check the domains (reachability of
  nameserver, does nameserver answer queries for the domain?)

Fixes:

* the link in the registration mail is now https if the site runs with https
* avoid sending unneccessary "delete" updates to master nameserver - first
  check if there is something to delete

Other changes:

* support and require Django >= 1.7
* remove Python 2.6 support, require 2.7 or 3.3+
* remove support for "south" migrations (used for 0.9.x and before)
* add support for django 1.7's builtin migrations
* misc. layout / UI improvments
* misc. doc improvements
* improved original strings in translations, use "trimmed" in django templates
* upgraded bootstrap


Release 0.9.1
-------------

Fixes:

* fix security issue with "related hosts" / "service updaters", fixes #177


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
