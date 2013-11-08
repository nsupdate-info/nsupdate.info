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
