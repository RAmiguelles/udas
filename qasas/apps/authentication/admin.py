from django.contrib import admin
from django.contrib.auth.models import Group

from ..authentication.models import Log, Profile


class LogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'ip_address', 'country', 'city', 'latitude', 'longitude',
                    'timestamp']
    list_per_page = 25
    list_filter = ['action', 'timestamp', 'country', 'city', ]
    search_fields = ['ip_address', 'user__first_name', 'user__last_name']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', ]
    list_per_page = 100
    list_display_links = ['user']
    search_fields = ['user__first_name', 'user__last_name']


admin.site.unregister(Group)
admin.site.register(Log, LogAdmin)
admin.site.register(Profile, ProfileAdmin)
