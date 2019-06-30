import subprocess
from django.test import TestCase
from .models import Medic
from .serializers import MedicSerializer


class TestPEP8(TestCase):
    def test_pep8(self):
        output = subprocess.check_output(
            ["find", "/kinesio/kinesio/",
             "-type", "f",
             "-name", "*.py",
             "-exec", "pycodestyle",
             "--max-line-length=34000",
             "--ignore=E121,E123,E126,E226,E24,E704,W503,E741,E722",
             "{}", ";"])
        assert len(output.strip()) == 0, f'There should be no pep-8 errors!\n{output.strip()}'


class TestObjectsSerializedInADictionary(TestCase):
    def setUp(self) -> None:
        Medic.objects.create(username='juan', password='1234', name='juan',
                             last_name='gomez', license='matricula #15433')

    def test_serializing_one_medic_returns_a_dictionary(self):
        serialized_objects_data = MedicSerializer(Medic.objects.get(name='juan')).data
        self.assertNotEquals(dict, type(serialized_objects_data))

    def test_serializing_one_medic_does_not_create_data_key(self):
        serialized_objects_data = MedicSerializer(Medic.objects.get(name='juan')).data
        self.assertTrue('data' not in serialized_objects_data)

    def test_serializing_multiple_medics_returns_a_dictionary(self):
        Medic.objects.create(username='maria76', password='7070', name='maria',
                             last_name='martinez vega', license='matricula #1342')
        serialized_objects_data = MedicSerializer(Medic.objects.all(), many=True).data
        self.assertNotEquals(dict, type(serialized_objects_data))
