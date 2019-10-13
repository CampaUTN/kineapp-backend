from rest_framework import serializers

from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='key', read_only=True)

    class Meta:
        model = Token
        fields = ('token',)
