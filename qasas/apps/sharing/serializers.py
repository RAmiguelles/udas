from rest_framework import serializers

from ..sharing.models import SharedDirectory, SharedDocument


class SharedDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedDirectory
        fields = '__all__'


class SharedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedDocument
        fields = '__all__'
