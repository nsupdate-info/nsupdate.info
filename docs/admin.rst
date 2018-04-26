==========================
Administrating the service
==========================

Installation (for development/testing)
======================================

Create and activate a virtualenv for the installation (here with virtualenvwrapper)::

    mkvirtualenv nsupdate
    workon nsupdate


Clone the repo and cd into::

    git clone https://github.com/nsupdate-info/nsupdate.info.git nsupdate
    cd nsupdate


Then install the software with requirements to your virtual env::

    pip install -r requirements.d/dev.txt
    pip install -e .


Configuration
=============

nsupdate.info Service
---------------------

First, please read the nsupdate/settings/*.py files - they contain a lot of
settings you can use to customize your nsupdate.info installation. dev is for
a development setup, prod is for a production setup and base has settings that
are common for both.

But do not change anything in there, but rather create your own
local_settings.py file, import from our settings and override anything you want
to change afterwards.::

    from nsupdate.settings.dev import *
    SECRET_KEY='S3CR3T'

IMPORTANT: you usually need to tell django what settings you want to use.

We won't document this for every single command in this documentation, but
we'll assume that you either set DJANGO_SETTINGS_MODULE environment variable
so it points to your settings module or that you give the --settings parameter
additionally with all commands that need it::

    export DJANGO_SETTINGS_MODULE=local_settings  # this is YOUR settings file
    or
    django-admin.py --settings=local_settings ...
    python manage.py --settings=local_settings ...


Note: if Django can't import your local_settings module, make sure that your
python search path contains the directory that contains local_settings.py::

    # we assume here that local_settings.py is in current directory.
    # alternatively, you could also give a specific path instead of .
    export PYTHONPATH=.:$PYTHONPATH


Initialize the database
-----------------------

To create and initialize the database, use::

    python manage.py migrate


Create the superuser account
----------------------------

To create the user who is administrator of the service, use::

    python manage.py createsuperuser


Start the development server
----------------------------

::

    python manage.py runserver


Nameserver
----------

Now as the server is running, you can log in using the superuser account you
just created and use "admin" from the menu to access Django's admin interface.

You'll need to configure at least 1 nameserver / 1 zone to accept dynamic updates,
see the "Domains" section in the "user" part of the manual.


Installation (for production)
=============================

You usually will use a production webserver like apache or nginx (not Django's
builtin "runserver").

If you want to use a virtualenv: see the hints for development installation.

If you install from repo code, it is sufficient to use the production
requirements file (will install less packages than for development)::

    pip install -r requirements.d/prod.txt
    pip install -e .

Alternatively, you can just install the latest release from pypi::

    pip install nsupdate


Configuration
=============

As described for testing/development, but use nsupdate.settings.prod in your
local_settings.py file.

Also, you will need to review the settings in the nsupdate.settings.prod
module and override everything that is different for your setup into your
local_settings.py file.

Note: if you do not setup ALLOWED_HOSTS correctly, your will just see status
400 errors.

WSGI
----

Module nsupdate.wsgi contains the wsgi "application" object.

Please consult the webserver / django docs how to configure it and how to run
django apps (wsgi apps) with the webserver you use.

Django has nice generic documentation about this, see there:

https://docs.djangoproject.com/en/1.11/howto/deployment/

Even if you do not follow or fully read the deployment guide, make sure that
you at least read the checklist:

https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/


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


Now proceed with manage migrate as shown above.


Customization of the Web UI
===========================

You likely will need to customize the Web UI a bit, here is how.

Overriding the builtin templates
--------------------------------
If you want to add/modify footers or headers or if you need to add stuff
into the HEAD element of the html, you can override some includes we made
to support this usecase.

Create an custom template directory (not within the repository / code
directory) and add it to your settings, e.g.::

    TEMPLATE_DIRS = ('/srv/nsupdate.info/templates', )

Below that template directory, you can override the builtin templates by
just using the same relative name, e.g.:

* includes/base_footer.html (footer of all web UI views)
* main/includes/home_bottom.html (bottom of main view)
* (there are more of these, just look into the code's template dirs)

Best way to start is likely to copy the original file from the template
directories located below the code directory into YOUR custom template
directory and then slightly modify it.

As the templates might be cached in memory, you may need to restart your
wsgi process to have them reloaded.

Note: it is advised that you keep local customizations to a minimum as if you
override builtin templates with your customized copies, you will have to keep
your copies in sync with future changes we make to the builtin ones.

Custom templates
----------------

If you need to add some simple views, just showing some simple templates (like
e.g. if you have some footer links that link to these views to show some site-
specific content, some legalese, ...), do it like that:

* have a footer and a custom template directory like described in previous
  section
* add files like main/custom/foo.html to that directory::

    {% extends "base.html" %}
    {% load bootstrap %}
    {% block content %}
    This is content rendered from template "foo.html".
    {% endblock %}

* link to the view made from that template like this::

    <a href="{% url 'custom' template='foo.html' %}">
        link to custom foo.html view
    </a>


Maintenance
===========

Regular jobs
------------
You need to run some commands regularly, we show how to do that on Linux (or
other POSIX OSes) using user cronjobs (use crontab -e to edit it). Make sure
it runs as the same user as the nsupdate.info wsgi application::

    PYTHONPATH=/srv/nsupdate.info
    DJANGO_SETTINGS_MODULE=local_settings
    # reinitialize the test user:
    50 2 * * * $HOME/env/bin/python $HOME/env/bin/django-admin.py testuser
    # reset the fault counters:
    55 2 * * 6 $HOME/env/bin/python $HOME/env/bin/django-admin.py faults --flag-abuse=150 --reset-client --notify-user
    # clear expired sessions from the database, use your correct settings module:
    0  3 * * * $HOME/env/bin/python $HOME/env/bin/django-admin.py clearsessions
    # clear outdated registrations:
    30 3 * * * $HOME/env/bin/python $HOME/env/bin/django-admin.py cleanupregistration
    # check whether the domain nameservers are reachable / answer queries:
    0  4 * * * $HOME/env/bin/python $HOME/env/bin/django-admin.py domains --check --notify-user


Dealing with abuse
------------------

In the regular jobs example in the previous section,
--flag-abuse=150 means that it'll set the abuse flag if the client fault counter
is over 150 (and, for these cases, it'll also reset the fault counter back to 0).

--reset-client additionally sets all client fault counters back to 0, so all
counts are just "per week".

--notify-user will send an email notification to the creator of the host if we
set the abuse flag for it. The email will contain instructions for the user
about how to fix the problem.

So, if you run this weekly, it means that more than 150 client faults per week are
considered abuse (e.g. if someone runs a stupid cronjob to update the IP instead
of a well-behaved update client).

Hosts with the abuse flag set won't accept updates, but the user will be able to
see the abuse flag (as ABUSE on the web interface and also their update client
should show it somehow), fix the problem on the client side and reset the abuse
flag via the web interface. If the problem was not really fixed, then it will
set the abuse flag again the next week.

This procedure should make sure that users of the service run sane and correctly
working update clients while being able to fix issues on their own without
needing help from service administration.

For really bad cases of intentional or ongoing abuse, there is also a
abuse_blocked flag that can only be set or reset manually by service
administration (using django admin interface).
While abuse_blocked is set, the service won't accept updates for this host.
The user can see the ABUSE-BLOCKED status on the web interface, but can not
change the flag.

Dealing with badly configured domains
-------------------------------------

In the regular jobs example in the previous section,
django-admin.py domains --check --notify-user means that we'll check all
domains that are currently flagged as available.

We query the nameserver configured for the domain and check if it answers a
SOA query for this domain. If we can't reach the nameserver or it does not
answer the query, we flag the domain as not available. We also flag it as
not public (this only is a change if it was public before).
If --notify-user is given, we notify the owner of the domain by email if we
flag the domain as not available. Owner in this context means: the user who
added the domain to our service.

Please note that we can not check whether the nameserver accepts dynamic
updates for the domain. The dns admin could have set arbitrary restrictions
on this and we do not know them. So if you have a domain configured with the
service, please make sure that dynamic updates really work.

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

Maybe you also need the next command (we bundle .mo files, but if you run into
troubles with them, try this)::

    python manage.py compilemessages

Of course, you'll also need to restart the django/wsgi processes, so the new
code gets loaded.


Tuning
------

If you get a lot of requests for /myip, the Python code handling this URL will
be rather busy. If you use nginx, you may optionally tune this and respond to
these requests directly from nginx without invoking any python code::

  location /myip {
    add_header Content-Type text/plain;
    return 200 $remote_addr;
  }

You need to add this to all server blocks (IP v4, v6, both) that are dealing
with requests for the service.

DNSSEC
------

There is no need for special support for DNSSEC in the nsupdate.info software,
it is sufficient to configure your DNS server (e.g. BIND) to support and manage
DNSSEC and it will just work.

See there for more infos and links:

https://github.com/nsupdate-info/nsupdate.info/issues/26
