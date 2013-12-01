==========================
Administrating the service
==========================

Installation (for development/testing)
======================================

Create and activate a virtualenv for the installation (here with virtualenvwrapper)::

    mkvirtualenv nsupdate
    workon nsupdate


Clone the repo and cd into::

    git clone git@github.com:nsupdate-info/nsupdate.info.git nsupdate
    cd nsupdate


Then install the software with requirements to your virtual env::

    pip install -e .

Set SECRET_KEY and create settings_local.py file::

    echo "SECRET_KEY='S3CR3T'" > nsupdate/settings_local.py

To create and initialize the database, use::

    python manage.py syncdb
    python manage.py migrate


To start the development server::

    python manage.py runserver


Installation (for production)
=============================

You usually will use a production webserver like apache or nginx (not the
builtin "runserver"). Please consult the webserver docs how to configure it
and how to run django apps (wsgi apps) with it.

As soon as you switch off DEBUG, Django won't serve static files any more,
thus you need to arrange /static/ file serving by your web server.

We assume here that you configured your web server to serve /static/ URL from
/srv/nsupdate.info/htdocs/static/ directory.

Django helps you to put all the static files into that directory, you just need
to configure STATIC_ROOT for that::

    STATIC_ROOT = '/srv/nsupdate.info/htdocs/static'

And then, run this::

    umask 0022  # make sure group and others keep r and x, but not w
    python manage.py collectstatic

This will copy all the static files into STATIC_ROOT.

Now, you must set DEBUG=False so it doesn't leak information from tracebacks
to the outside world.

Make sure your static files really work.

Since version 1.6, Django has a nice deployment checklist (make sure stuff
applies to the django version YOU use):

https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

Regular jobs
------------
You need to run some commands regularly, we show how to do that on Linux (or
other POSIX OSes) using user cronjobs (use crontab -e to edit it). Make sure
it runs as the same user as the nsupdate.info wsgi application::

    DJANGO_SETTINGS_MODULE=local_settings
    # reinitialize the test user:
    50 2 * * * django-admin.py testuser
    # reset the fault counters:
    55 2 * * * django-admin.py faults --flag-abuse=20 --reset-client
    # clear expired sessions from the database, use your correct settings module:
    0  3 * * 1 django-admin.py clearsessions
    # clear outdated registrations:
    0  3 * * 2 django-admin.py cleanupregistration


Dealing with abuse
------------------

In the regular jobs example in the previous section,
--flag-abuse=20 means that it'll set the abuse flag if the client fault counter
is over 20 (and, for these cases, it'll also reset the fault counter back to 0).

--reset-client additionally sets all client fault counters back to 0, so all
counts are just "per day".

So, if you run this daily, it means that more than 20 client faults per day are
considered abuse (e.g. if someone runs a stupid cronjob to update the IP instead
of a well-behaved update client).

Hosts with the abuse flag set won't accept updates, but the user will be able to
see the abuse flag (as ABUSE on the web interface and also their update client
should show it somehow), fix the problem on the client side and reset the abuse
flag via the web interface. If the problem was not really fixed, then it will
set the abuse flag again the next day.

This procedure should make sure that users of the service run sane and correctly
working update clients while being able to fix issues on their own without
needing help from service administration.

For really bad cases of intentional or ongoing abuse, there is also a
abuse_blocked flag that can only be set or reset manually by service
administration (using django admin interface).
While abuse_blocked is set, the service won't accept updates for this host.
The user can see the ABUSE-BLOCKED status on the web interface, but can not
change the flag.


Configuration
=============

nsupdate.info Service
---------------------

Use a local_settings.py.


Nameserver
----------

You'll need to configure at least 1 nameserver / 1 zone to accept dynamic updates, see the "Domains" section
in the "user" part of the manual.


Maintenance
===========

Database contents
-----------------
Users who are in the "staff" group (like the one initially created when creating the database) can access the
admin interface (see "Admin" in the same menu as "Logout").

But be careful, the Django admin lets you do all sorts of stuff, admins are allowed to shoot themselves.
Only give Django admin access ("staff" group membership) to highly trusted admins of the service.


Software updates / upgrades
===========================

After upgrading the code, you'll usually need to run::

    python manage.py migrate

This fixes your database schema so it is compatible with the new code.
