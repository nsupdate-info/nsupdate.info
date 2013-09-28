About nsupdate.info
===================

www.nsupdate.info is a free dynamic dns service.

nsupdate.info is also the name of the software used to implement it.


Installation
===================

If you haven't already done create and change to a virtualenv for the installation (here with virtualenvwrapper)
```
mkvirtualenv nsupdate
workon nsupdate
```
Clone the repo and cd into
```
git clone git@github.com:asmaps/nsupdate.info.git
cd nsupdate.info
```
Then install requirements (either "dev" or just "all" for production)
```
pip install -r requirements.d/all.txt
#or for dev
pip install -r requirements.d/dev.txt
```
From time to time execute this again to install the newest dependencies.
