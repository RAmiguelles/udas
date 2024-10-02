from rest_framework import viewsets, permissions

from ..sharing.models import SharedDirectory, SharedDocument
from ..sharing.serializers import SharedDirectorySerializer, SharedDocumentSerializer


class SharedDirectoryViewSet(viewsets.ModelViewSet):
    queryset = SharedDirectory.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = SharedDirectorySerializer


class SharedDocumentViewSet(viewsets.ModelViewSet):
    queryset = SharedDocument.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = SharedDocumentSerializer
