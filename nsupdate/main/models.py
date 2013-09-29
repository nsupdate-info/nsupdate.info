from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.forms import ModelForm


class Domain(models.Model):
    domain = models.CharField(max_length=256, unique=True)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return u"%s" % (self.domain)


class Host(models.Model):
    """TODO: hash update_secret on save (if not already hashed)"""
    #fqdn = models.CharField(max_length=256, unique=True, verbose_name="Fully qualified domain name")
    subdomain = models.CharField(max_length=256, validators=[
        RegexValidator(regex=r'^(([a-z0-9][a-z0-9\-]*[a-z0-9])|[a-z0-9])$', message='Invalid subdomain: only letters, digits and dashes are allowed')])
    domain = models.ForeignKey(Domain)
    update_secret = models.CharField(max_length=256)
    comment = models.CharField(max_length=256, default='', blank=True, null=True)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return u"%s.%s - %s" % (self.subdomain, self.domain.domain, self.comment)

    class Meta:
        unique_together = (('subdomain', 'domain'),)

