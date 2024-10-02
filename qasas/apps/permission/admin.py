from django.contrib import admin

from ..permission.models import Permission, Log


class LogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'details', 'ip_address', 'country', 'city', 'latitude', 'longitude',
                    'timestamp']
    list_per_page = 25
    list_filter = ['action', 'timestamp', 'country', 'city', ]
    search_fields = ['details', 'ip_address', 'user__first_name', 'user__last_name']


# Register your models here.
admin.site.register(Permission)
admin.site.register(Log, LogAdmin)
