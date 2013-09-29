from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth.hashers import make_password


class Host(models.Model):
    """TODO: hash update_secret"""
    fqdn = models.CharField(max_length=256, unique=True, verbose_name="Fully qualified domain name")
    update_secret = models.CharField(max_length=256)
    comment = models.CharField(max_length=256, default='', blank=True, null=True)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='hosts')

    def __unicode__(self):
        return u"%s - %s" % (self.fqdn, self.comment)