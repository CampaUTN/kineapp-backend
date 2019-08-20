from django.test import TestCase
import os

from ..utils.thumbnail import ThumbnailGenerator


class TestThumbnailGenerator(TestCase):
    def setUp(self) -> None:
        with open('/kinesio/kinesio/kinesioapp/tests/resources/kinesio.jpg', 'rb') as image_file_:
            content = image_file_.read()
        self.thumbnail = ThumbnailGenerator(content).thumbnail

    def test_thumbnail_mime_type(self):
        assert self.thumbnail[:20] == b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'

    def test_thumbail_length(self):
        assert len(self.thumbnail) == 5007

    def test_thumbnail_type_is_byes(self):
        assert type(self.thumbnail) == bytes

    def test_no_remaining_temporary_files(self):
        assert os.listdir('/tmpfs') == []
