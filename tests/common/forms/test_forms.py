from io import BytesIO
from typing import Any, Optional, Type, Union

from django.contrib.contenttypes.forms import BaseGenericInlineFormSet, generic_inlineformset_factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from model_bakery import baker
from PIL import Image

from common import models as common_models
from common.forms import ImageForm
from registration import models as registration_models
from roleplay import models as roleplay_models
from tests.utils import fake


class TestImageForm(TestCase):
    file_data: dict[str, Any]
    form_class = ImageForm
    user: registration_models.User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')

        cls.image_data = BytesIO()
        Image.new('RGB', (30, 60), color='red').save(cls.image_data, 'JPEG')

    def setUp(self) -> None:
        self.file_data = {
            'image': SimpleUploadedFile(fake.file_name('image'), self.image_data.getvalue()),
        }

    def test_data_ok(self):
        form = self.form_class(owner=self.user, data={}, files=self.file_data)

        self.assertTrue(form.is_valid(), repr(form.errors))

    def test_missing_required_data_ko(self):
        del self.file_data['image']
        form = self.form_class(owner=self.user, data={}, files=self.file_data)

        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'image', ['This field is required.'])


class TestImageFormAsGenericInlineFormSet(TestCase):
    """
    We test the generic Image table using :class:`~roleplay.models.Race` as playground.
    """

    file_data: dict[str, Any]
    form_class = ImageForm
    formset_class: Type[BaseGenericInlineFormSet]
    formset_kwargs: dict[str, Any]
    formset_prefix = 'common-image-formset'
    model = common_models.Image
    related_object: roleplay_models.Race
    user: registration_models.User
    valid_data: dict[str, Any]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = baker.make_recipe('registration.user')
        cls.related_object = baker.make_recipe('roleplay.race')

        cls.image_data = BytesIO()
        Image.new('RGB', (30, 60), color='red').save(cls.image_data, 'JPEG')
        cls.formset_class = generic_inlineformset_factory(
            model=cls.model, form=cls.form_class, ct_field='content_type', fk_field='object_id', extra=3,
        )
        cls.formset_kwargs = {
            'form_kwargs': {'owner': cls.user},
            # Instance is the related object to whom these instances are going to be linked
            'instance': cls.related_object,
            # We use prefix to declare what name is going to be use on render
            # https://docs.djangoproject.com/en/4.1/topics/forms/formsets/#customizing-a-formset-s-prefix
            'prefix': cls.formset_prefix,
        }

    def setUp(self) -> None:
        self.file_data = {
            f'{self.formset_prefix}-0-image': self._generate_form_image(),
        }
        self.valid_data = {
            f'{self.formset_prefix}-TOTAL_FORMS': '1',
            f'{self.formset_prefix}-INITIAL_FORMS': '0',
        }

    def _generate_form_image(self, content: Optional[Union[bytes, str]] = None):
        return SimpleUploadedFile(
            name=fake.file_name('image'),
            content=content or self.image_data.getvalue(),
        )

    def test_invalid_data_ko(self):
        self.file_data[f'{self.formset_prefix}-1-image'] = self._generate_form_image(b'random')
        self.valid_data[f'{self.formset_prefix}-TOTAL_FORMS'] = '2'
        formset = self.formset_class(data=self.valid_data, files=self.file_data, **self.formset_kwargs)

        self.assertFalse(formset.is_valid())
        self.assertFormsetError(formset=formset, form_index=1, field='image', errors=[
            'Upload a valid image. The file you uploaded was either not an image or a corrupted image.',
        ])

    def test_valid_data_ok(self):
        formset = self.formset_class(data=self.valid_data, files=self.file_data, **self.formset_kwargs)

        self.assertTrue(formset.is_valid(), repr(formset.errors or formset.non_form_errors()))

    def test_valid_data_creates_images_to_related_object_ok(self):
        self.file_data[f'{self.formset_prefix}-1-image'] = self._generate_form_image()
        self.valid_data[f'{self.formset_prefix}-TOTAL_FORMS'] = '2'
        formset = self.formset_class(data=self.valid_data, files=self.file_data, **self.formset_kwargs)

        self.assertTrue(formset.is_valid(), repr(formset.errors or formset.non_form_errors()))

        images = formset.save()

        # Image order is backwards since it's ordered by new first contrary to what formset returns
        self.assertQuerysetEqual(images[::-1], self.related_object.images.all())
