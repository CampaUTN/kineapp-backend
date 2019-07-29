from kinesioapp.utils.test_utils import APITestCase

from ..models import User
from ..serializers import UserSerializer


class TestObjectsSerializedInADictionary(APITestCase):
    def setUp(self) -> None:
        User.objects.create_user(username='juan', license='matricula #15433')

    def test_serializing_one_medic_returns_a_dictionary(self):
        serialized_objects_data = UserSerializer(User.objects.get(username='juan')).data
        self.assertNotEquals(dict, type(serialized_objects_data))

    def test_serializing_one_medic_does_not_create_data_key(self):
        serialized_objects_data = UserSerializer(User.objects.get(username='juan')).data
        self.assertTrue('data' not in serialized_objects_data)

    def test_serializing_multiple_medics_returns_a_dictionary(self):
        User.objects.create_user(username='maria76', license='matricula #1342')
        serialized_objects_data = UserSerializer(User.objects.medics(), many=True).data
        self.assertNotEquals(dict, type(serialized_objects_data))
