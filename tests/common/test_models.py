import tempfile

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from model_bakery import baker

from common.models import Image, Track, Vote
from registration.models import User
from roleplay.models import Campaign, Race
from tests.utils import fake


class TestTrack(TestCase):
    model = Track

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')

    def setUp(self):
        tmp_img_file = tempfile.NamedTemporaryFile(mode='wb+', dir='./tests/')
        self.image_file = SimpleUploadedFile(
            name=fake.file_name(extension='jpg'), content=tmp_img_file.read(), content_type='image/jpeg'
        )
        tmp_img_file.close()

    def test_file_extension_not_audio_ko(self):
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


class TestImage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user: User = baker.make_recipe('roleplay.user')
        cls.race: Race = baker.make_recipe('roleplay.race')

    def setUp(self) -> None:
        image = SimpleUploadedFile(name=fake.file_name(extension='jpg'), content=b'', content_type='image/jpeg')
        self.instance = Image(image=image, owner=self.user)

    def test_generic_relation_works_ok(self):
        self.instance.content_type = ContentType.objects.get_for_model(Race)
        self.instance.object_id = self.race.pk
        self.instance.save()

        self.assertIn(self.instance, self.race.images.all())

    def test_str_ok(self):
        expected_str = f'{self.instance.image.name} [{self.user.username}] ({self.instance.pk})'

        self.assertEqual(expected_str, str(self.instance))


class TestVote(TestCase):
    model = Vote

    @classmethod
    def setUpTestData(cls):
        cls.vote_model = ContentType.objects.get_for_model(Campaign)
        cls.model_id = baker.make_recipe('roleplay.campaign').pk

    def setUp(self):
        self.positive_vote = baker.make(
            _model=Vote, user=baker.make_recipe('registration.user'), is_positive=True, content_type=self.vote_model,
            object_id=self.model_id,
        )
        self.negative_vote = baker.make(
            _model=Vote, user=baker.make_recipe('registration.user'), is_positive=False, content_type=self.vote_model,
            object_id=self.model_id,
        )

    def test_str_ok(self):
        expected_positive_str = f'{self.positive_vote.user.username} voted + on roleplay.campaign ({self.model_id})'
        expected_negative_str = f'{self.negative_vote.user.username} voted - on roleplay.campaign ({self.model_id})'

        self.assertEqual(expected_positive_str, str(self.positive_vote))
        self.assertEqual(expected_negative_str, str(self.negative_vote))
