from rest_framework import serializers
from .models import MetadataFieldModel

class MetadataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataFieldModel
        fields = '__all__'
