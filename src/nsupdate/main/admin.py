"""
Register our models with Django's admin.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Host, RelatedHost, Domain, BlacklistedHost, ServiceUpdater, ServiceUpdaterHostConfig


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "public", "available", "created_by")
    list_filter = ("created", "public", "available")
    search_fields = ("name", "created_by__username", "created_by__email")


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "created_by_link", "client_faults", "api_auth_faults", "abuse", "abuse_blocked")
    list_filter = ("created", "abuse", "abuse_blocked", "domain")
    read_only_fields = ('created_by_link',)

    search_fields = ("name", "created_by__username", "created_by__email")

    def created_by_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:auth_user_change", args=(obj.created_by.pk,)),
            obj.created_by.username
        ))
    created_by_link.short_description = 'created by'


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
