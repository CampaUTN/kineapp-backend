from kinesioapp.utils.test_utils import APITestCase
from datetime import datetime

from ..models import User


class TestSharing(APITestCase):
    def setUp(self) -> None:
        self.medic = User.objects.create_user(username='maria22', password='1234', license='matricula #44423',
                                              dni=39203040, birth_date=datetime.now())
        self.another_medic = User.objects.create_user(username='juan55', license='matricula #5343',
                                                      dni=42203088, birth_date=datetime.now())
        self.patient = User.objects.create_user(username='facundo22', first_name='facundo', password='1234',
                                                dni=25000033, birth_date=datetime.now(), current_medic=self.medic)
        User.objects.create_user(username='martin', current_medic=self.medic, dni=15505050, birth_date=datetime.now())
