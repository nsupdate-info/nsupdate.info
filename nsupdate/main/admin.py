"""
register our models for Django's admin
"""

from django.contrib import admin

from .models import Host, Domain, BlacklistedDomain, ServiceUpdater, ServiceUpdaterHostConfig

admin.site.register(BlacklistedDomain)
admin.site.register(Domain)
admin.site.register(Host)
admin.site.register(ServiceUpdater)
admin.site.register(ServiceUpdaterHostConfig)
