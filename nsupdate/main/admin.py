from django.contrib import admin

from .models import Host, Domain, BlacklistedDomain

admin.site.register(BlacklistedDomain)
admin.site.register(Domain)
admin.site.register(Host)
