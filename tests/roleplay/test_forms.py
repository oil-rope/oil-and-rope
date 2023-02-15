import os
import random
import tempfile
from datetime import timedelta
from typing import Any, cast

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker
from PIL import Image

from registration import models as registration_models
from roleplay import enums, forms, models
from tests.utils import fake, generate_place


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

    def test_place_and_parent_has_same_owner_ok(self):
        form = self.form_class(data=self.data_ok, files=self.files)
        form.is_valid()
        place = form.save()

        self.assertEqual(place.owner, self.parent_site.owner)


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


class TestCampaignForm(TestCase):
    form_class = forms.CampaignForm
    model = models.Campaign

    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make_recipe('registration.user')
        cls.place = baker.make_recipe('roleplay.world')

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        image_file = self.tmp.name
        Image.new('RGB', (30, 60), color='red').save(image_file)
        with open(image_file, 'rb') as image_content:
            image = SimpleUploadedFile(name=image_file, content=image_content.read(), content_type='image/jpeg')

        self.data_ok = {
            'name': fake.sentence(nb_words=3),
            'description': fake.paragraph(),
            'gm_info': fake.paragraph(),
            'summary': fake.sentence(nb_words=3),
            'system': random.choice(enums.RoleplaySystems.values),
            'is_public': fake.pybool(),
            'place': self.place.pk,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=1),
            'email_invitations': '\n'.join([fake.email() for _ in range(3)]),
        }
        self.files_ok = {
            'cover_image': image,
        }

    def tearDown(self):
        self.tmp.close()
        os.unlink(self.tmp.name)

    def test_data_ok(self):
        form = self.form_class(user=self.user, data=self.data_ok, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_description_ok(self):
        data_without_description = self.data_ok.copy()
        del data_without_description['description']
        form = self.form_class(user=self.user, data=data_without_description, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_gm_info_ok(self):
        data_without_gm_info = self.data_ok.copy()
        del data_without_gm_info['gm_info']
        form = self.form_class(user=self.user, data=data_without_gm_info, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_summary_ok(self):
        data_without_summary = self.data_ok.copy()
        del data_without_summary['summary']
        form = self.form_class(user=self.user, data=data_without_summary, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_cover_image_ok(self):
        form = self.form_class(user=self.user, data=self.data_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_is_public_ok(self):
        data_without_is_public = self.data_ok.copy()
        del data_without_is_public['is_public']
        form = self.form_class(user=self.user, data=data_without_is_public, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_start_date_ok(self):
        data_without_start_date = self.data_ok.copy()
        del data_without_start_date['start_date']
        form = self.form_class(user=self.user, data=data_without_start_date, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_end_date_ok(self):
        data_without_end_date = self.data_ok.copy()
        del data_without_end_date['end_date']
        form = self.form_class(user=self.user, data=data_without_end_date, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_email_invitations_ok(self):
        data_without_email_invitations = self.data_ok.copy()
        del data_without_email_invitations['email_invitations']
        form = self.form_class(user=self.user, data=data_without_email_invitations, files=self.files_ok)

        self.assertTrue(form.is_valid())

    def test_data_without_name_ko(self):
        data_without_name = self.data_ok.copy()
        del data_without_name['name']
        form = self.form_class(user=self.user, data=data_without_name, files=self.files_ok)

        self.assertFalse(form.is_valid())

    def test_data_without_system_ko(self):
        data_without_system = self.data_ok.copy()
        del data_without_system['system']
        form = self.form_class(user=self.user, data=data_without_system, files=self.files_ok)

        self.assertFalse(form.is_valid())

    def test_data_without_place_ko(self):
        data_without_place = self.data_ok.copy()
        del data_without_place['place']
        form = self.form_class(user=self.user, data=data_without_place, files=self.files_ok)

        self.assertFalse(form.is_valid())

    def test_form_email_invitations_is_list_ok(self):
        form = self.form_class(user=self.user, data=self.data_ok, files=self.files_ok)
        # In order to get cleaned_data with call to form.full_clean()
        form.full_clean()

        self.assertEqual(list, type(form.cleaned_data['email_invitations']))

    def test_form_save_assigns_owner_ok(self):
        form = self.form_class(user=self.user, data=self.data_ok, files=self.files_ok)
        instance = form.save()

        self.assertEqual(self.user, instance.owner)


class TestSessionForm(TestCase):
    form_class = forms.SessionForm

    @classmethod
    def setUpTestData(cls):
        cls.campaign = baker.make_recipe('roleplay.campaign')

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode='w', dir='./tests/', suffix='.jpg', delete=False)
        image_file = self.tmp.name
        Image.new('RGB', (30, 60), color='red').save(image_file)
        with open(image_file, 'rb') as image_content:
            image = SimpleUploadedFile(name=image_file, content=image_content.read(), content_type='image/jpeg')

        self.data_ok = {
            'name': fake.sentence(nb_words=3),
            'description': fake.paragraph(),
            'plot': fake.sentence(nb_words=4),
            'gm_info': fake.paragraph(),
            'next_game': fake.future_datetime(),
        }
        self.files = {
            'image': image,
        }

    def tearDown(self):
        self.tmp.close()
        os.unlink(self.tmp.name)

    def test_data_ok(self):
        form = self.form_class(campaign=self.campaign, data=self.data_ok, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_description_ok(self):
        data_without_description = self.data_ok.copy()
        del data_without_description['description']
        form = self.form_class(campaign=self.campaign, data=data_without_description, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_plot_ok(self):
        data_without_plot = self.data_ok.copy()
        del data_without_plot['plot']
        form = self.form_class(campaign=self.campaign, data=data_without_plot, files=self.files)

        self.assertTrue(form.is_valid())

    def test_data_without_gm_info_ok(self):
        data_without_gm_info = self.data_ok.copy()
        del data_without_gm_info['gm_info']
        form = self.form_class(campaign=self.campaign, data=data_without_gm_info, files=self.files)

        self.assertTrue(form.is_valid())

    def test_without_next_game_ok(self):
        data_without_next_game = self.data_ok.copy()
        del data_without_next_game['next_game']
        form = self.form_class(campaign=self.campaign, data=data_without_next_game)

        self.assertTrue(form.is_valid())

    def test_without_image_ok(self):
        form = self.form_class(campaign=self.campaign, data=self.data_ok)

        self.assertTrue(form.is_valid())

    def test_without_name_ko(self):
        data_without_name = self.data_ok.copy()
        del data_without_name['name']
        form = self.form_class(campaign=self.campaign, data=data_without_name, files=self.files)

        self.assertFalse(form.is_valid())

    def test_next_game_before_today_ko(self):
        data_before_today = self.data_ok.copy()
        data_before_today['next_game'] = fake.past_datetime()
        form = self.form_class(campaign=self.campaign, data=data_before_today)

        self.assertFalse(form.is_valid())

    def test_campaign_is_assigned_ok(self):
        form = self.form_class(campaign=self.campaign, data=self.data_ok, files=self.files)
        form.is_valid()
        session = form.save()

        self.assertEqual(self.campaign, session.campaign)


class TestRacePlaceForm(TestCase):
    form_class = forms.RacePlaceForm
    place: models.Place
    user: registration_models.User
    valid_data: dict[str, Any]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')
        cls.place = cast(models.Place, generate_place(owner=cls.user))

    def setUp(self) -> None:
        self.valid_data = {
            'name': fake.word(),
            'description': fake.paragraph(),
            'strength': 0,
            'dexterity': 0,
            'constitution': 0,
            'intelligence': 0,
            'wisdom': 0,
            'charisma': 0,
            'affected_by_armor': fake.pybool(),
        }

    def test_form_with_valid_data_is_valid_ok(self):
        form = self.form_class(user=self.user, place=self.place, data=self.valid_data)

        self.assertTrue(form.is_valid(), repr(form.errors))

    def test_form_data_creates_race_ok(self):
        form = self.form_class(user=self.user, place=self.place, data=self.valid_data)

        self.assertTrue(form.is_valid(), repr(form.errors))
        race: models.Race = form.save()

        self.assertEqual(race.name, self.valid_data['name'])
        self.assertEqual(race.description, self.valid_data['description'])
        self.assertEqual(race.strength, self.valid_data['strength'])
        self.assertEqual(race.dexterity, self.valid_data['dexterity'])
        self.assertEqual(race.constitution, self.valid_data['constitution'])
        self.assertEqual(race.intelligence, self.valid_data['intelligence'])
        self.assertEqual(race.wisdom, self.valid_data['wisdom'])
        self.assertEqual(race.charisma, self.valid_data['charisma'])
        self.assertEqual(race.affected_by_armor, self.valid_data['affected_by_armor'])

    def test_form_data_without_name_ko(self):
        data = self.valid_data.copy()
        del data['name']
        form = self.form_class(user=self.user, place=self.place, data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertListEqual(form.errors['name'], ['This field is required.'])

    def test_form_data_only_required_ok(self):
        required_fields = ('name', )
        data = {field: self.valid_data[field] for field in required_fields}
        form = self.form_class(user=self.user, place=self.place, data=data)

        self.assertTrue(form.is_valid(), repr(form.errors))

    def test_form_data_only_required_creates_race_ok(self):
        required_fields = ('name', )
        data = {field: self.valid_data[field] for field in required_fields}
        form = self.form_class(user=self.user, place=self.place, data=data)

        self.assertTrue(form.is_valid(), repr(form.errors))
        race: models.Race = form.save()

        self.assertEqual(race.name, self.valid_data['name'])
        self.assertEqual(race.description, '')
        self.assertEqual(race.strength, 0)
        self.assertEqual(race.dexterity, 0)
        self.assertEqual(race.constitution, 0)
        self.assertEqual(race.intelligence, 0)
        self.assertEqual(race.wisdom, 0)
        self.assertEqual(race.charisma, 0)
        # NOTE: When a checkbox is not marked/not sent it's false by default
        self.assertFalse(race.affected_by_armor)
