==================================
The nsupdate.info software Project
==================================

History
=======

The initial version of the nsupdate.info software was developed in 48h in the DjangoDash 2013 contest by:

* `Arne Schauf <https://github.com/asmaps/>`_
* `Fabian Faessler <https://github.com/Samuirai/>`_
* `Thomas Waldmann <https://github.com/ThomasWaldmann/>`_


Project site
============

Source code repository, issue tracker (bugs, ideas about enhancements, todo,
feedback, ...), link to documentation is all there:

https://github.com/nsupdate-info/nsupdate.info

Translations
============

Translations are done on Transifex - please collaborate there to avoid double work / workflow issues:

https://www.transifex.com/projects/p/nsupdateinfo/

You need the transifex-client package so you have the tx command:

::

    pip install transifex-client


Please make sure to configure your notification settings so that you are
notified when the translation project is updated (so you can react quickly and
keep your translation fresh).

Translations update workflow (start from a clean workdir):

::

    # pull all translations from Transifex:
    tx pull
    # update the translations with changes from the source code:
    django-admin makemessages -a
    # compile the translations to .mo files
    django-admin compilemessages
    # push updated translation files back to Transifex:
    tx push -s -t


Contributing
============

Feedback is welcome.

If you find some issue, have some idea or some patch, please submit them via the issue tracker.

Or even better: if you use git, fork our repo, make your changes and submit a pull request.

For small fixes, you can even just edit the files on GitHub (GitHub will then fork, change and submit a pull request
automatically).


Dependency management
=====================

Get `Pipenv <https://pipenv.pypa.io/en/latest/installation/>`_ and checkout the
`Pipenv Command Reference <https://pipenv.pypa.io/en/latest/commands/>`_.

Install new dependencies
------------------------

See `the pipenv docs <https://pipenv.pypa.io/en/latest/commands/#install>`_.

::

    pipenv install mypkg


Spawn a shell with correct Python paths
---------------------------------------

::

    pipenv shell

Exit the shell with ``exit``.

Dependency maintenance
----------------------

Update requirements.txt files including transitive dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pipenv update

NOTE: This is not done today and only a suggestion.

::

    pipenv requirements --exclude-markers > requirements.d/all.txt
    pipenv requirements --exclude-markers --dev-only > requirements.d/dev.txt

Verify the updated dependencies don't include any security vulnerabilities:

::

    pipenv check


Build locally
=============

1. Install `build` (see `its docs <https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives>`_
   for example), e.g. via ``pacman -S python-build`` on Arch Linux.
2. Afterwards, run the command to generate pip packages in ``dist/``::

    pyproject-build

NOTE: This is also needed before development because the command generates ``./src/nsupdate/_version.py``.

Run locally
===========

#. Install dependencies ``pipenv install --dev``
#. Generate ``src/nsupdate/_version.py`` file by running ``pyproject-build``
#. Create database using ``pipenv run ./manage.py migrate``
#. Create a superuser with ``pipenv run ./manage.py createsuperuser``
#. Run the server with ``pipenv run ./manage.py runserver``

Lint
====

Run `pylint <https://pylint.readthedocs.io/en/stable/>`_ in
error-only mode to check any problems::

    pipenv run pylint src/nsupdate

NOTE: The project does not use pylint for formatting.
      Disabling the ``errors-only`` mode in ``.pylintrc`` will show a lot of warnings.

Run tests
=========

Tests need to run inside Docker because they depend on a ``BIND 9`` nameserver
running a specific configuration on ``127.0.0.1:53``.

#. Build the Docker image once, using: ``docker build -t nsupdate scripts/docker/``
#. Then run tests via ``docker run --dns 127.0.0.1 -v $PWD:/app nsupdate``
