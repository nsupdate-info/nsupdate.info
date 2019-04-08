"""
register our models for Django's admin
"""

from django.contrib import admin

from .models import Host, RelatedHost, Domain, BlacklistedHost, ServiceUpdater, ServiceUpdaterHostConfig


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "public", "available", "created_by")
    list_filter = ("created", "public", "available")
    search_fields = ("name", "created_by__username", "created_by__email")


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "created_by", "client_faults", "abuse", "abuse_blocked")
    list_filter = ("created", "abuse", "abuse_blocked", "domain")
    search_fields = ("name", "created_by__username", "created_by__email")


@admin.register(RelatedHost)
class RelatedHostAdmin(admin.ModelAdmin):
    list_display = ("name", "main_host", "available", "comment")
    search_fields = ("name", "main_host__created_by__username", "main_host__created_by__email")


@admin.register(BlacklistedHost)
class BlacklistedHostAdmin(admin.ModelAdmin):
    list_display = ("name_re", "created_by")
    list_filter = ("created", )


@admin.register(ServiceUpdater)
class ServiceUpdaterAdmin(admin.ModelAdmin):
    list_display = ("name", "comment", "created_by")
    list_filter = ("created", )


@admin.register(ServiceUpdaterHostConfig)
class ServiceUpdaterHostConfigAdmin(admin.ModelAdmin):
    list_display = ("host", "service", "hostname", "comment", "created_by")
    list_filter = ("created", )
