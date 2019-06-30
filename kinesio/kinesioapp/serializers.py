from .utils import serializers
from .models import Medic


class MedicSerializer(serializers.ModelToDictionarySerializer):
    class Meta:
        model = Medic
        fields = ('username', 'name', 'last_name', 'license')
