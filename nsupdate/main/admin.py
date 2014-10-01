"""
register our models for Django's admin
"""

from django.contrib import admin

from .models import Host, Domain, BlacklistedHost, ServiceUpdater, ServiceUpdaterHostConfig


class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "public", "available", "created_by")
    list_filter = ("created", "public", "available")
    search_fields = ("name", "created_by__username", "created_by__email")


class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "created_by", "client_faults", "abuse", "abuse_blocked")
    list_filter = ("created", "abuse", "abuse_blocked", "domain")
    search_fields = ("name", "created_by__username", "created_by__email")


class BlacklistedHostAdmin(admin.ModelAdmin):
    list_display = ("name_re", "created_by")
    list_filter = ("created", )


admin.site.register(BlacklistedHost, BlacklistedHostAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(ServiceUpdater)
admin.site.register(ServiceUpdaterHostConfig)
