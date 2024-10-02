from django.contrib import admin

from ..directory.models import Directory, DirectoryGroup, Moderator, Accreditor, Log


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'parent', 'group', 'created_at')
    list_filter = ('created_at',)
    list_per_page = 100
    list_display_links = ('id', 'name',)
    search_fields = ['id', 'name', 'description']
    autocomplete_fields = ['parent','group']

class DirectoryGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields=['id','name']
    list_per_page = 100

class ModeratorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'directory', 'created_at')
    list_filter = ('created_at',)
    list_display_links = ['user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'directory__name']
    autocomplete_fields = ['user','directory']
    list_per_page = 100


class AccreditorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'directory', 'created_at')
    list_filter = ('created_at',)
    list_display_links = ['user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'directory__name']
    list_select_related=['user','directory']
    autocomplete_fields = ['user','directory']
    list_per_page = 100


class SubdirectoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'child', 'is_direct')
    list_filter = ('parent', 'child', 'is_direct')
    list_per_page = 100


class LogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'directory', 'details', 'ip_address', 'country', 'city', 'latitude', 'longitude',
                    'timestamp']
    list_per_page = 800
    list_filter = ['action', 'timestamp', 'country', 'city', ]
    list_display_links = ['user']
    search_fields = ['details', 'ip_address', 'user__first_name', 'user__last_name']


# Register your models here.
admin.site.register(Directory, DirectoryAdmin)
# admin.site.register(Subdirectory, SubdirectoryAdmin)
admin.site.register(DirectoryGroup, DirectoryGroupAdmin)
admin.site.register(Moderator, ModeratorAdmin)
admin.site.register(Accreditor, AccreditorAdmin)
admin.site.register(Log, LogAdmin)
