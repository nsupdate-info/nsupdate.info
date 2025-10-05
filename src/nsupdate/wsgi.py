"""
WSGI configuration for the nsupdate project.

This module contains the WSGI application used by Django's development server
and by production WSGI deployments. It exposes a module-level variable named
``application``. Django's ``runserver`` and ``runfcgi`` commands discover this
application via the ``WSGI_APPLICATION`` setting.

Usually, you will have the standard Django WSGI application here, but it might
also make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application from another
framework.

"""
import os

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This can break
# when running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or set
# os.environ["DJANGO_SETTINGS_MODULE"] = "nsupdate.settings.dev"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsupdate.settings.dev")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
