=======================
Security considerations
=======================

Transmission security
=====================

Use https for the web interface as well as for the update client (if possible).

Otherwise, your username / password (FQDN / update secret) will be transmitted
in clear text (unencrypted).


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


Nameserver Update Key (backend, RFC 2136)
-----------------------------------------

We currently store this key (which is basically a base64 encoded shared secret)
"as is".

This is somehow critical, but also hard to do better - encryption would only
help very little here as we would need to decrypt the update key before using it,
so we would need the unlocked key of that encryption mechanism on the same machine.

Make sure no unauthorized person gets that key or he/she will be able to update
ANY record in the respective zone / nameserver directly (without going over
nsupdate.info software / service).


CSRF protection
===============

We use Django's CSRF protection middleware.


XSS protection
==============

Django's templating engine html-escapes inputs by default.


Cookies
=======

The software ("as is") uses these cookies:

* "csrftoken" (host-only, for CSRF protection)
* "sessionid" (host-only, to keep the session when you have logged-in to the
  web interface)


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

