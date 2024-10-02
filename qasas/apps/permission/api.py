from rest_framework import viewsets, permissions

from ..permission.models import Permission
from ..permission.serializers import PermissionSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = PermissionSerializer
