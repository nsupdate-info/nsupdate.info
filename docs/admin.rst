==========================
Administrating the service
==========================

Installation
============

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


Software updates / upgrades
===========================

After upgrading the code, you'll usually need to run::

    python manage.py migrate

This fixes your database schema so it is compatible with the new code.
