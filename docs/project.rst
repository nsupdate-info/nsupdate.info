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

    # currently only works on python 2.x, transifex-client github repo has 3.3 support
    pip install transifex-client


Please make sure to configure your notification settings so that you are
notified when the translation project is updated (so you can react quickly and
keep your translation fresh).

Translations update workflow (start from a clean workdir):

::

    # pull all translations from transifex:
    tx pull
    # update the translations with changes from the source code:
    django-admin.py makemessages -a
    # compile the translations to .mo files
    django-admin.py compilemessages
    # push updated translation files back to transifex:
    tx push -s -t


Contributing
============

Feedback is welcome.

If you find some issue, have some idea or some patch, please submit them via the issue tracker.

Or even better: if you use git, fork our repo, make your changes and submit a pull request.

For small fixes, you can even just edit the files on github (github will then fork, change and submit a pull request
automatically).
