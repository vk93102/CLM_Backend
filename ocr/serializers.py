from rest_framework import serializers
from .models import OCRJobModel

class OCRJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = OCRJobModel
        fields = '__all__'
