from django.contrib import admin

from .models import DirectoryTrash, DocumentTrash


class DirectoryTrashAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'directory', 'user', 'created_at')
    list_filter = ('department',  'created_at',)
    list_per_page = 100
    list_display_links = ('id', 'directory',)
    search_fields = ['department__name', 'directory__name', 'user__first_name', 'user__last_name' ]


class DocumentTrashAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'docdir', 'user', 'created_at')
    list_filter = ('department', 'created_at',)
    list_per_page = 100
    list_display_links = ('id', 'docdir',)
    search_fields = ['department__name', 'docdir__directory__name', 'docdir__document__title', 'user__first_name', 'user__last_name' ]


admin.site.register(DirectoryTrash, DirectoryTrashAdmin)
admin.site.register(DocumentTrash, DocumentTrashAdmin)