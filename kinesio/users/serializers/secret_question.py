from rest_framework import serializers

from ..models import SecretQuestion


class SecretQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretQuestion
        fields = '__all__'
