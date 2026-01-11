from rest_framework import serializers
from .models import SearchIndexModel

class SearchIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchIndexModel
        fields = '__all__'
