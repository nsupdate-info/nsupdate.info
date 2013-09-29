About nsupdate.info
===================

nsupdate.info is the idea of a really simple single purpose dynamic dns service.
Unlike other dynamic dns services its intention is that you do not
have to click a link every 30 days to keep your domain enabled or other jokes
like this.

nsupdate.info is is intended to be self hostable, but there will most probably
be a free service on http://www.nsupdate.info/


Installation
============

If you haven't already done create and change to a virtualenv for the
installation (here with virtualenvwrapper)::

    mkvirtualenv nsupdate
    workon nsupdate


Clone the repo and cd into::

    git clone git@github.com:asmaps/nsupdate.info.git nsupdate
    cd nsupdate


Then install the requirements::

    pip install -e .


From time to time execute this again to install the newest dependencies.
Maybe in future there will be a PyPi package to install directly with pip.

