from django.db import models
from django.contrib.auth.models import User


class Host(models.Model):
    fqdn = models.CharField(max_length=256)
    update_secret = models.CharField(max_length=256)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return u"%s (%s)" % (self.fqdn, self.created_by)

