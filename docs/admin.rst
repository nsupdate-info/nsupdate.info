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
