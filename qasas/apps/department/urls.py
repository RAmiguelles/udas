from django.urls import path
from rest_framework import routers

from ..department.api import DepartmentViewSet, UserDepartmentViewSet, get_public_departments, get_user_departments, getDepartments
from ..department.suggestions import get_users, get_department_users

router = routers.DefaultRouter()
router.register('user', UserDepartmentViewSet)
router.register('', DepartmentViewSet)

urlpatterns = [
    path('public', get_public_departments),
    path('user-departments/<int:user_id>', get_user_departments),
    path('', getDepartments),

    path('suggestion/all-users', get_users),
    path('suggestion/users', get_department_users),
]

urlpatterns += router.urls
