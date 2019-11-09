import subprocess
from django.test import TestCase


class TestPEP8(TestCase):
    def test_pep8(self):
        output = subprocess.check_output(
            ["find", "/kinesio/kinesio/",
             "-type", "f",
             "-name", "*.py",
             "-exec", "pycodestyle",
             "--max-line-length=34000",
             "--ignore=E121,E123,E126,E226,E24,E704,W503,E741,E722,W504",
             "{}", ";"])

        assert len(output.strip()) == 0, f'There should be no pep-8 errors!\n{output.strip()}'
