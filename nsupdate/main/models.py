from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm


class Host(models.Model):
    """TODO: hash update_secret"""
    fqdn = models.CharField(max_length=256,unique=True)
    update_secret = models.CharField(max_length=256)
    comment = models.CharField(max_length=256,default='',blank=True, null=True)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return u"%s (%s)" % (self.fqdn, self.created_by)



class HostForm(ModelForm):
    class Meta:
        model = Host
        fields = ['fqdn', 'update_secret','comment']