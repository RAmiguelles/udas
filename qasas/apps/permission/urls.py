from rest_framework import routers

from ..permission.api import PermissionViewSet

router = routers.DefaultRouter()
router.register('', PermissionViewSet)

urlpatterns = [
    # path('tree', getDirectoryTree),
]

urlpatterns += router.urls
