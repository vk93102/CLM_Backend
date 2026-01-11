from rest_framework import serializers
from .models import RepositoryModel, RepositoryFolderModel

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryModel
        fields = '__all__'

class RepositoryFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryFolderModel
        fields = '__all__'
