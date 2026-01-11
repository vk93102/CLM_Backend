from rest_framework import serializers
from .models import RedactionJobModel

class RedactionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedactionJobModel
        fields = '__all__'
