from django.urls import path, include

urlpatterns = [
    path('directory/', include('apps.directory.urls')),
    path('document/', include('apps.document.urls')),
    path('department/', include('apps.department.urls')),
    # path('permission/', include('apps.permission.urls')),
    # path('sharing/', include('apps.sharing.urls')),
    path('auth/', include('apps.authentication.urls')),
    # path('log/', include('apps.log.urls')),
    path('app/', include('apps.app_admin.urls')),
    path('trash/', include('apps.trash.urls')),
]
