from django.contrib import admin

from ..department.models import Department, UserDepartment, Log


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_support']
    search_fields = ['name']
    list_display_links = ['name']
    list_per_page = 25


class UserDepartmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserDepartment._meta.get_fields()]
    list_filter = ('is_head', 'is_active', 'department')
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'department__name']
    list_display_links = ['user']
    list_per_page = 25


class LogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'details', 'ip_address', 'country', 'city', 'latitude', 'longitude',
                    'timestamp']
    list_per_page = 25
    list_filter = ['action', 'timestamp', 'country', 'city', ]
    search_fields = ['details', 'ip_address', 'user__first_name', 'user__last_name']


# Register your models here.
admin.site.register(Department, DepartmentAdmin)
admin.site.register(UserDepartment, UserDepartmentAdmin)
admin.site.register(Log, LogAdmin)
