from rest_framework import serializers
from .models import RuleModel

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleModel
        fields = '__all__'
