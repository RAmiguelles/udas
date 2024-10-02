from django.contrib import admin

from ..document.models import Document, Attachment, Attribute, Keyword, Comment, \
    DocumentDirectory, Type, Log


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_per_page = 50


class DocumentDirectoryAdmin(admin.ModelAdmin):
    list_display = ('directory', 'document', 'is_public', 'is_copy', 'is_link', 'link')
    list_per_page = 25


class LogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'document', 'details', 'ip_address', 'country', 'city', 'latitude', 'longitude',
                    'timestamp']
    list_per_page = 25
    list_filter = ['action', 'timestamp', 'country', 'city', ]
    search_fields = ['details', 'ip_address', 'user__first_name', 'user__last_name']


# Register your models here.
admin.site.register(Document, DocumentAdmin)
admin.site.register(Attachment)
admin.site.register(Attribute)
admin.site.register(Keyword)
admin.site.register(Comment)
admin.site.register(DocumentDirectory, DocumentDirectoryAdmin)
admin.site.register(Type)
admin.site.register(Log, LogAdmin)
