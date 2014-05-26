"""
register our models for Django's admin
"""

from django.contrib import admin

from .models import Host, Domain, BlacklistedDomain, ServiceUpdater, ServiceUpdaterHostConfig


class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "public", "available", "created_by")
    list_filter = ("public", "available", "created_by")


class HostAdmin(admin.ModelAdmin):
    list_display = ("subdomain", "domain", "created_by", "client_faults", "abuse", "abuse_blocked")
    list_filter = ("abuse", "abuse_blocked", "domain", "created_by")


class BlacklistedDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "created_by")
    list_filter = ("created_by", "created")


admin.site.register(BlacklistedDomain, BlacklistedDomainAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(ServiceUpdater)
admin.site.register(ServiceUpdaterHostConfig)
