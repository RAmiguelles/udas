from django.urls import path

from ..authentication.api import log_in, log_out, getUsers, getUsersInDepartment,getUsersUserDepartments

urlpatterns = [
    path('login', log_in),
    path('logout', log_out),
    # path('change-password', change_password),

    path('users', getUsers),
    path('department-users', getUsersInDepartment),
    path('users-user-departments', getUsersUserDepartments),
]
