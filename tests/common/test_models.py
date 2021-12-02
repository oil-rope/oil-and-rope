import tempfile

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from model_bakery import baker

from common.constants import models
from common.utils import create_faker

fake = create_faker()


class TestTrack(TestCase):
    model = apps.get_model(models.TRACK_MODEL)

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')

    def setUp(self):
        tmp_img_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/')
        with open(tmp_img_file.name, 'rb') as tmp_content:
            self.image_file = SimpleUploadedFile(
                name=fake.file_name(extension='jpg'), content=tmp_content.read(), content_type='image/jpeg'
            )

    def test_file_extesion_not_audio_ko(self):
        track_instance = self.model(name=fake.word(), owner=self.user, file=self.image_file)

        try:
            track_instance.full_clean()
            self.fail('ValidationError not launched!')
        except ValidationError as ex:
            self.assertIn('File is not an audio.', ex.messages)

    def test_create_instance_without_optionals_ok(self):
        self.model.objects.create(
            name=fake.word(),
            file=fake.file_name(category='audio'),
        )

        self.assertTrue(True)  # Dummy for passing tests

    def test_str_ok(self):
        name = fake.word()
        file = fake.file_name(category='audio')
        track_instance = baker.make(_model=self.model, name=name, file=file)
        expected_str = f'{name} ({file})'

        self.assertEqual(expected_str, str(track_instance))
