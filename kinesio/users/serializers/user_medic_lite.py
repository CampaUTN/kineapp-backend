from rest_framework import serializers

from ..models import User


class MedicUserLiteSerializer(serializers.ModelSerializer):
    """ This is just another serializers for instances of User class with Medic type.
        However, we need to put it on a special file to avoid circular import problems.
        For the same reason, this class does not inherit from either user.UserSerializer or user.MedicUserSerializer """
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture_url')
