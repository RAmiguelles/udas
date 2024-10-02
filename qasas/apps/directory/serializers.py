from rest_framework import serializers

from ..directory.models import Directory, DirectoryGroup, Moderator
from src.models import CollegeDescription, CollegeDescriptionDetail


class DirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Directory
        fields = '__all__'


class DirectoryGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectoryGroup
        fields = '__all__'


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = '__all__'

class CollegeDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeDescription
        fields = '__all__'

class CollegeDescriptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeDescriptionDetail
        fields = '__all__'

