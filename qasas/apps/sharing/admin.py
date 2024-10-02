from django.contrib import admin

from .models import SharedDirectory, SharedDocument, Log


class LogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'details', 'ip_address', 'country', 'city', 'latitude', 'longitude',
                    'timestamp']
    list_per_page = 25
    list_filter = ['action', 'timestamp', 'country', 'city', ]
    search_fields = ['details', 'ip_address', 'user__first_name', 'user__last_name']


# Register your models here.
admin.site.register(SharedDirectory)
admin.site.register(SharedDocument)
admin.site.register(Log, LogAdmin)
