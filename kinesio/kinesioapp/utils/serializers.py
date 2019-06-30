from rest_framework import serializers


class ModelToDictionarySerializer(serializers.ModelSerializer):
    """
    A class used to always return dictionaries when serializing objects.
    If we are serializing multiple objects, the serialized data would be a dictionary
    with the following format: {'data': <list content>}
    """
    def to_representation(self, data: object) -> dict:
        representation = super().to_representation(data)
        return {'data': representation} if type(data) == list else representation
