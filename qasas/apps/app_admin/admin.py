from django.contrib import admin

from ..app_admin.models import Setting, Log


class SettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'session_time_limit', 'upload_filesize_limit', 'is_active', 'is_default')
    list_per_page = 25


class LogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'details', 'ip_address', 'country', 'city', 'latitude', 'longitude',
                    'timestamp']
    list_per_page = 25
    list_filter = ['action', 'timestamp', 'country', 'city', ]
    search_fields = ['details', 'ip_address', 'user__first_name', 'user__last_name']


# Register your models here.
admin.site.register(Setting, SettingAdmin)
admin.site.register(Log, LogAdmin)
