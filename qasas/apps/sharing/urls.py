from rest_framework import routers

from ..sharing.api import SharedDirectoryViewSet, SharedDocumentViewSet

router = routers.DefaultRouter()
router.register('directory', SharedDirectoryViewSet)
router.register('document', SharedDocumentViewSet)

urlpatterns = [
    # path('tree', getDirectoryTree),
]

urlpatterns += router.urls
