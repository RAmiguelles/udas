from django.urls import path
from rest_framework import routers

from .api import get_office_trash, restore_directory_trash, restore_document_trash, delete_directory_trash, \
    delete_document_trash, restore_all_trash, delete_all_trash

router = routers.DefaultRouter()
# router.register('', PermissionViewSet)

urlpatterns = [
    path('office/<int:directory_id>', get_office_trash),
    path('office/<int:directory_id>/restore/all', restore_all_trash),
    path('office/<int:directory_id>/delete/all', delete_all_trash),
    path('office/restore/directory/<str:trash_id>', restore_directory_trash),
    path('office/restore/document/<str:trash_id>', restore_document_trash),
    path('office/delete/directory/<str:trash_id>', delete_directory_trash),
    path('office/delete/document/<str:trash_id>', delete_document_trash),
]

urlpatterns += router.urls
