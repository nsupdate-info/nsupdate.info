from main.models import Host, Domain, BlacklistedDomain
from django.contrib import admin

admin.site.register(BlacklistedDomain)
admin.site.register(Domain)
admin.site.register(Host)
