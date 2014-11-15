=======================
Security considerations
=======================

Transmission security
=====================

Use https for the web interface as well as for the update client (if possible).

Otherwise, your username / password (FQDN / update secret) will be transmitted
in clear text (unencrypted).

The web interface will warn you if you use it via http. If WE_HAVE_TLS is
set to True, it will suggest you better use the https site and link there.

Additionally, the service administrator can implement a redirect from the
http to the https site within the webserver configuration for the WWW_HOST.
The redirect should **not** be implemented for WWW_IPV4_HOST and WWW_IPV6_HOST
as it is unknown whether all update clients can deal with a redirect (and
support TLS).

For the router / update client configuration examples we show when creating a
update secret, we use update URLs with https: (and we also tell why it might
not work).

On the hosts overview page, we show whether we received the last update via TLS.

Please note that if you like security, you also need to use https (with
certificate verification) if you use the web-based method to query your IP
address. If you use http, a powerful attacker could MITM your request and
tell you a wrong IP, which your updater then would happily write into DNS.


Login with remote vs. local Account
===================================

If you use a already existing remote account to log in into our service, you
don't need to create a local profile (with username, E-Mail and password).

That way, we need to store less information about you - especially no password
hash (and you also don't need to create a new password just for our service).
So, this is a little more safe if you just consider our service.

BUT: If you use some external service to log in, you of course need to trust
them for this purpose as *they* are telling "yes, this is really you".

Also, if you cancel the account on that external service and you don't have
a local profile (login, E-Mail, password) with us, you will be unable to log
in afterwards or recover access to your hosts/domains.

So maybe the best way is to first create a local profile (username, E-Mail,
password), then log in and associate your other remote accounts with that
local profile.


Passwords / Secrets / Keys
==========================

Interactive login password
--------------------------

We recommend that you use a rather strong and not guessable password for this.
Do not re-use passwords, use a password system or a password manager.

The interactive login password for the web site is stored using Django's
default hasher mechanism, which is currently pbkdf2 (a very strong and
intentionally slow password hash). Brute-Force attacks against such hashes are
very slow, much slower than against simple hashes like (s)sha1/sha256 etc.

It is NOT stored in clear text by nsupdate.info.

If you lose the password, you'll have to do a password reset via e-mail.


Automated update secret
-----------------------

The automated update secret for routers or other update clients is a
random and automatically generated secret. We store it using the sha1 hasher
of Django (which in fact is salted-sha1, a not very strong, but fast-to-compute
hash).

Considering that a lot of routers or update clients store this secret in clear
text in their configuration and often transmit it using unencrypted http (and
not https), this secret is not too safe anyway. We also wanted to save some cpu
cycles here and rather not use pbkdf2 for this regularly and automatically used
secret.

It is not stored in clear text by nsupdate.info.

If you lose the secret, you'll have to generate a new one and change it in your
update client also.

We use a random and automatically generated update secret to avoid that users
enter a bad password here (like reusing a password they use somewhere else,
choosing a too simple password) and to avoid disclosure of such user-chosen
passwords in case the hashes ever get stolen and brute forced.


Nameserver Update Secret (backend, RFC 2136)
--------------------------------------------

We currently store this secret (which is basically a base64 encoded shared secret,
one per dynamic zone) "as is" into the database ("Domain" records there).

This is somehow critical, but also hard to do better - encryption would only
help very little here as we would need to decrypt the update secret before using it,
so we would need the unlocked decryption key on the same machine.

Make sure no unauthorized person gets that secret or he/she will be able to update
ANY record in the respective zone / nameserver directly (without going over
nsupdate.info software / service).

We support creating a random update secret, so you don't need an extra tool for this.


Other Services Update Secret (dyndns2 client)
---------------------------------------------

We need to store this secret "as is" into the database for the same reasons as
outlined above.

But: we tell you in the services overview whether we'll use TLS to transmit the
update, so at least if TLS is enabled, it won't go unencrypted over the wire.


CSRF protection
===============

We use Django's CSRF protection middleware.


Clickjacking protection
=======================

We use Django's clickjacking protection middleware.


XSS protection
==============

Django's templating engine html-escapes inputs by default.


Cookies
=======

The software ("as is") uses these cookies:

* "csrftoken" (host-only, for CSRF protection)
* "sessionid" (host-only, to keep the session when you have logged-in to the
  web interface)

If you have set WE_HAVE_TLS to True (because you run the software on a https
site), you should also set *_COOKIE_SECURE to True to avoid the cookies getting
transmitted via http.

We use a session cookie by default (gets cleared when you close the browser).
If you check the "Keep me logged in" checkbox on the login screen, then we'll
set a permanent cookie with a lifetime as configured by the site admin
(SESSION_COOKIE_AGE, default: 14 days).

Be careful with domain cookies
------------------------------

The software ("as is") does not use any domain cookies.

In case you modify the software, please be extremely cautious with domain
cookies and in case of doubt, do rather not use them.

If you use domain cookies (like for ".yourservice.net", the leading dot
makes it a domain cookie), all hosts in that domain would be able to read
and write these cookies. Your site (at e.g. www.yourservice.net), but also
users' sites (like attacker.yourservice.net).

Obviously, this might lead to security issues with stealing, modifying and
faking domain cookies.


Django's SECRET_KEY
===================

Django's SECRET_KEY needs to be a long, random and secret string (it is
usually set up by the administrator of the site).

The builtin default settings will try to read SECRET_KEY from an environment
variable of same name. If there is no such environment variable, the SECRET_KEY
will be undefined.

You can also define the SECRET_KEY in your local_settings.py.

If you do not define a SECRET_KEY by one of these methods, the application
will refuse to start and give you an error, that a SECRET_KEY is required.
