import os
import random
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from model_bakery import baker
from PIL import Image

from roleplay import enums, forms, models
from tests import fake


class TestPlaceForm(TestCase):
    form_class = forms.PlaceForm

    @classmethod
    def setUpTestData(cls):
        cls.owner = baker.make_recipe('registration.user')
        cls.parent_site = baker.make_recipe('roleplay.place', owner=cls.owner)

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        Image.new('RGB', (30, 60), color='red').save(self.tmp_file.name)
        with open(self.tmp_file.name, 'rb') as img_content:
            image = SimpleUploadedFile(name=self.tmp_file.name, content=img_content.read(), content_type='image/jpeg')

        self.data_ok = {
            'name': fake.country(),
            'description': fake.paragraph(),
            'site_type': random.choice(enums.SiteTypes.values),
            'parent_site': self.parent_site.pk,
        }
        self.files = {
            'image': image,
        }

    def tearDown(self):
        self.tmp_file.close()
        os.unlink(self.tmp_file.name)

    def test_data_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files)

        self.assertTrue(form.is_valid())

    def test_optional_data_ok(self):
        # Without image
        form = self.form_class(data=self.data_ok)
        self.assertTrue(form.is_valid())

        data_without_description = self.data_ok.copy()
        del data_without_description['description']
        form = self.form_class(data=data_without_description)
        self.assertTrue(form.is_valid())

    def test_required_data_ko(self):
        data_without_name = self.data_ok.copy()
        del data_without_name['name']
        form = self.form_class(data=data_without_name)
        self.assertFalse(form.is_valid())

        data_without_site_type = self.data_ok.copy()
        del data_without_site_type['site_type']
        form = self.form_class(data=data_without_site_type)
        self.assertFalse(form.is_valid())

        data_without_parent_site = self.data_ok.copy()
        del data_without_parent_site['parent_site']
        form = self.form_class(data=data_without_parent_site)
        self.assertFalse(form.is_valid())

    def test_place_and_parent_has_same_owner_and_user_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files)
        form.is_valid()
        place = form.save()

        self.assertEqual(place.owner, self.parent_site.owner)
        self.assertEqual(place.user, self.parent_site.user)


class TestWorldForm(TestCase):
    form_class = forms.WorldForm
    model = models.Place

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        image_file = self.tmp.name
        Image.new('RGB', (30, 60), color='red').save(image_file)
        with open(image_file, 'rb') as image_content:
            image = SimpleUploadedFile(name=image_file, content=image_content.read(), content_type='image/jpeg')

        self.data_ok = {
            'name': fake.country(),
            'description': fake.paragraph()
        }

        self.files_ok = {
            'image': image
        }

    def tearDown(self):
        self.tmp.close()
        os.unlink(self.tmp.name)

    def test_data_ok(self):
        form = self.form_class(owner=self.user, data=self.data_ok, files=self.files_ok)

        self.assertTrue(form.is_valid(), 'Errors: {}'.format(form.errors.values()))

    def test_data_without_name_ko(self):
        data_ko = self.data_ok.copy()
        del data_ko['name']
        form = self.form_class(owner=self.user, data=data_ko, files=self.files_ok)

        self.assertFalse(form.is_valid())

    def test_data_without_description_ok(self):
        data_ok = self.data_ok.copy()
        del data_ok['description']
        form = self.form_class(owner=self.user, data=data_ok, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_image_ok(self):
        data_ok = self.data_ok.copy()
        form = self.form_class(owner=self.user, data=data_ok)

        self.assertTrue(form.is_valid())

    def test_save_ok(self):
        form = self.form_class(owner=self.user, data=self.data_ok, files=self.files_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk))
        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertEqual(self.data_ok['description'], instance.description)
        self.assertEqual(enums.SiteTypes.WORLD, instance.site_type)
        self.assertEqual(instance.owner, self.user)
        self.assertIsNone(instance.user)
        self.assertIsNotNone(instance.image)

        os.unlink(instance.image.path)

    def test_save_without_description_ok(self):
        data_without_description = self.data_ok.copy()
        del data_without_description['description']
        form = self.form_class(owner=self.user, data=data_without_description, files=self.files_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk))
        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertEqual(enums.SiteTypes.WORLD, instance.site_type)
        self.assertEqual(instance.owner, self.user)
        self.assertIsNone(instance.user)
        self.assertIsNotNone(instance.image)

        os.unlink(instance.image.path)

    def test_save_without_image_ok(self):
        form = self.form_class(owner=self.user, data=self.data_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk))
        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertEqual(self.data_ok['description'], instance.description)
        self.assertEqual(enums.SiteTypes.WORLD, instance.site_type)
        self.assertEqual(instance.owner, self.user)
        self.assertIsNone(instance.user)

    def test_save_user_world_ok(self):
        form = self.form_class(owner=self.user, user=self.user, data=self.data_ok, files=self.files_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk))
        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertEqual(self.data_ok['description'], instance.description)
        self.assertEqual(enums.SiteTypes.WORLD, instance.site_type)
        self.assertEqual(instance.owner, self.user)
        self.assertEqual(self.user, instance.user)
        self.assertIsNotNone(instance.image)

        os.unlink(instance.image.path)


class TestSessionForm(TestCase):
    form_class = forms.SessionForm

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')

    def setUp(self):
        self.data_ok = {
            'name': fake.sentence(),
            'plot': fake.paragraph(),
            'world': baker.make_recipe('roleplay.world'),
            'system': enums.RoleplaySystems.PATHFINDER,
            'next_game': fake.future_datetime(),
        }

    def test_data_ok(self):
        form = self.form_class(data=self.data_ok)

        self.assertTrue(form.is_valid(), f'Errors: {form.errors.values()}')

    def test_data_without_plot_ok(self):
        data_without_plot = self.data_ok.copy()
        del data_without_plot['plot']
        form = self.form_class(data=data_without_plot)

        self.assertTrue(form.is_valid())

    def test_without_name_ko(self):
        data_without_name = self.data_ok.copy()
        del data_without_name['name']
        form = self.form_class(data_without_name)

        self.assertFalse(form.is_valid())

    def test_without_world_ko(self):
        data_without_world = self.data_ok.copy()
        del data_without_world['world']
        form = self.form_class(data=data_without_world)

        self.assertFalse(form.is_valid())

    def test_without_system_ko(self):
        data_without_system = self.data_ok.copy()
        del data_without_system['system']
        form = self.form_class(data=data_without_system)

        self.assertFalse(form.is_valid())

    def test_without_next_game_ko(self):
        data_without_next_game = self.data_ok.copy()
        del data_without_next_game['next_game']
        form = self.form_class(data=data_without_next_game)

        self.assertFalse(form.is_valid())

    def test_next_game_before_today_ko(self):
        data_before_today = self.data_ok.copy()
        data_before_today['next_game'] = fake.past_datetime()
        form = self.form_class(data=data_before_today)

        self.assertFalse(form.is_valid())

    def test_next_game_is_correct_ok(self):
        form = self.form_class(self.rq, data=self.data_ok)
        expected_date = timezone.datetime.combine(
            date=self.data_ok['next_game_date'],
            time=self.data_ok['next_game_time'],
            tzinfo=timezone.get_current_timezone(),
        )
        instance = form.save()

        self.assertEqual(expected_date, instance.next_game)


class TestRaceForm(TestCase):
    form_class = forms.RaceForm
    model = models.Race

    def setUp(self):
        self.user = baker.make_recipe('registration.user')
        self.faker = fake
        self.data_ok = {
            'name': self.faker.word(),
            'description': self.faker.paragraph(),
            'strength': self.faker.random_int(min=-5, max=5),
            'dexterity': self.faker.random_int(min=-5, max=5),
            'charisma': self.faker.random_int(min=-5, max=5),
            'constitution': self.faker.random_int(min=-5, max=5),
            'intelligence': self.faker.random_int(min=-5, max=5),
            'affected_by_armor': self.faker.boolean(),
            'wisdom': self.faker.random_int(min=-5, max=5),
            'users': [self.user.pk]
        }

        self.tmp = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        image_file = self.tmp.name
        Image.new('RGB', (30, 60), color='red').save(image_file)
        with open(image_file, 'rb') as image_content:
            image = SimpleUploadedFile(name=image_file, content=image_content.read(), content_type='image/jpeg')
        self.files_ok = {
            'image': image
        }

    def tearDown(self):
        self.tmp.close()
        os.unlink(self.tmp.name)

    def test_data_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files_ok)

        self.assertTrue(form.is_valid(), 'Errors: {}'.format(form.errors.values()))

    def test_data_without_name_ko(self):
        data_ko = self.data_ok.copy()
        del data_ko['name']
        form = self.form_class(data=data_ko, files=self.files_ok)

        self.assertFalse(form.is_valid())

    def test_data_without_description_ok(self):
        data_ok = self.data_ok.copy()
        del data_ok['description']
        form = self.form_class(data=data_ok, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_image_ok(self):
        data_ok = self.data_ok.copy()
        form = self.form_class(data=data_ok)

        self.assertTrue(form.is_valid())

    def test_save_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk))
        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertEqual(self.data_ok['description'], instance.description)
        self.assertIsNotNone(instance.users)
        self.assertIsNotNone(instance.image)

        os.unlink(instance.image.path)

    def test_save_without_description_ok(self):
        data_without_description = self.data_ok.copy()
        del data_without_description['description']
        form = self.form_class(data=data_without_description, files=self.files_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk))
        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertIsNotNone(instance.users)
        self.assertIsNotNone(instance.image)

        os.unlink(instance.image.path)

    def test_save_without_image_ok(self):
        form = self.form_class(data=self.data_ok)
        instance = form.save()

        self.assertTrue(self.model.objects.filter(pk=instance.pk))
        self.assertEqual(self.data_ok['name'], instance.name)
        self.assertEqual(self.data_ok['description'], instance.description)
        self.assertIsNotNone(instance.users)
