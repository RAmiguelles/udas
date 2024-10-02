from django.urls import path

from ..app_admin.api import test_connection, staging_log_in,populate_hris_users

urlpatterns = [
    path('net-test', test_connection),
    path('staging-pass', staging_log_in),
    path('populate_hris_users', populate_hris_users),
]
