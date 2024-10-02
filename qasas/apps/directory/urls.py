from django.urls import path
from rest_framework import routers

from .suggestions import get_directory_group_suggestion
from ..directory.api import get_directory_tree_by_directory_id, get_directory_tree_by_user_id, get_directory_tree_by_guest, get_directory_details_guest, get_directory_details, get_parents_directory, get_child_directory_by_parent_id, \
    DirectoryViewSet, DirectoryGroupViewSet, ModeratorViewSet, copy_directory, cut_directory, get_descendance_api, \
    link_directory, remove_link_directory, get_department_guests, get_public_documents, get_directory_link_description, update_directory_link, delete_directory_link

router = routers.DefaultRouter()
router.register('group', DirectoryGroupViewSet)
router.register('moderator', ModeratorViewSet)
router.register('', DirectoryViewSet)

urlpatterns = [
    path('dir-tree', get_directory_tree_by_directory_id),
    path('user-tree', get_directory_tree_by_user_id),
    path('details', get_directory_details),
    path('suggestion/group', get_directory_group_suggestion),
    path('copy', copy_directory),
    path('link', link_directory),
    path('link/remove', remove_link_directory),
    path('cut', cut_directory),
    path('descendance', get_descendance_api),

    path('guests/<int:user_id>', get_department_guests),
    path('guest/user-tree', get_directory_tree_by_guest),
    path('guest/details', get_directory_details_guest),
    path('guest/documents', get_public_documents),

    path('parents',get_parents_directory),
    path('directory-description/<int:directory_id>',get_directory_link_description),
    path('children',get_child_directory_by_parent_id),
    path('update_directory_link',update_directory_link),
    path('delete_directory_link',delete_directory_link),
]

urlpatterns += router.urls
