"""
register our models for Django's admin
"""

from django.contrib import admin

from .models import UserProfile


# XXX this is a bit ugly, as there are separate admins for profiles and users:
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "language", )
    search_fields = ("language", "user__username")


# this would be prettier, but could not get it to work with:
# - creating a user in the admin with or without filling in the profile
# - creating a user via user registration
#
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
#
# class UserProfileInline(admin.StackedInline):
#    model = UserProfile
#    can_delete = False
#    verbose_name_plural = 'Profiles'
#
#
# class UserAdmin(UserAdmin):
#    inlines = (UserProfileInline, )
#
#
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
