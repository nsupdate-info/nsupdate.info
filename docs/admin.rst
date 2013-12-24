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


Configuration
=============

nsupdate.info Service
---------------------

Use a local_settings.py (do not modify the nsupdate/settings/*.py files directly)::

    from nsupdate.settings.prod import *
    # override whatever you need to override here (read nsupdate/settings/*.py
    # to get an overview over what you might need to customize):
    SECRET_KEY='S3CR3T'

IMPORTANT: you usually need to tell django what settings you want to use.

We won't document this for every single command in this documentation, but
we'll assume that you either set DJANGO_SETTINGS_MODULE environment variable
so it points to your settings module or that you give the --settings parameter
additionally with all commands that need it::

    DJANGO_SETTINGS_MODULE=local_settings  # this is YOUR settings file
    or
    django-admin.py --settings=local_settings ...
    python manage.py --settings=local_settings ...


Initialize the database
-----------------------

To create and initialize the database, use::

    python manage.py syncdb
    python manage.py migrate


Start the development server
----------------------------

::

    python manage.py runserver


Nameserver
----------

Now as the server is running, you can log in using the database administrator
account you created in the syncdb step and use "admin" from the menu to start
Django's admin.

You'll need to configure at least 1 nameserver / 1 zone to accept dynamic updates,
see the "Domains" section in the "user" part of the manual.


Installation (for production)
=============================

You usually will use a production webserver like apache or nginx (not Django's
builtin "runserver").

WSGI
----

Module nsupdate.wsgi contains the wsgi "application" object.

Please consult the webserver / django docs how to configure it and how to run
django apps (wsgi apps) with the webserver you use.

Django has nice generic documentation about this, see there:

https://docs.djangoproject.com/en/1.6/howto/deployment/

Even if you do not follow or fully read the deployment guide, make sure that
you at least read the checklist:

https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/


HTTP Basic Auth
---------------

Additionally, you need to make sure that the "authorization" http header needed
for HTTP Basic Auth gets through to the nsupdate.info wsgi application. Some
web servers may need special settings for this::

    WSGIPassAuthorization On  # use this for apache2/mod-wsgi


Static Files
------------

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


PostgreSQL
----------
For production usage and better scalability, you may rather want to use
PostgreSQL than SQLite database. Django stores its sessions into the
database, so if you get a lot of accesses, sqlite will run into "database
is locked" issues.

Here are some notes I made when installing PostgreSQL using Ubuntu 12.04:

First installing and preparing PostgreSQL::

    apt-get install postgresql  # I used 9.1
    apt-get install libpq-dev  # needed to install psycopg2

    # within the virtual env:
    pip install psycopg2

    sudo -u postgres createdb nsupdate
    sudo -u postgres createuser --no-createrole --no-superuser --no-createdb --pwprompt nsupdate
    # enter reallysecret password, twice
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE nsupdate TO nsupdate;'

    sudo vim /etc/postgresql/9.1/main/pg_hba.conf
    # by default, postgresql on ubuntu uses only "peer" authentication for unix sockets, add "md5"
    # (password hash) authentication, otherwise it might use your login user instead of the configured user:
    # local   all             all                                     md5


To make nsupdate.info (Django) use PostgreSQL, put this into YOUR settings::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'nsupdate',  # database name
            'USER': 'nsupdate',
            'PASSWORD': 'reallysecret',
            'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': ''  # Set to empty string for default.
        }
    }


Now proceed with syncdb / migrate as shown above.


Maintenance
===========

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


Database contents
-----------------
Users who are in the "staff" group (like the one initially created when creating the database) can access the
admin interface (see "Admin" in the same menu as "Logout").

But be careful, the Django admin lets you do all sorts of stuff, admins are allowed to shoot themselves.
Only give Django admin access ("staff" group membership) to highly trusted admins of the service.


Software updates / upgrades
---------------------------

Please read the changelog before doing any upgrades, it might contain
important hints.

After upgrading the code, you'll usually need to run::

    python manage.py migrate

This fixes your database schema so it is compatible with the new code.

Of course, you'll also need to restart the django/wsgi processes, so the new
code gets loaded.
