from rest_framework import serializers
from .models import AIInferenceModel

class AIInferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInferenceModel
        fields = '__all__'
