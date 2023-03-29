from django.test import RequestFactory, TestCase
from django.urls import reverse_lazy
from model_bakery import baker

from common.views.edit import DeletedObjectsView
from registration.models import User


class TestDeletedObjectsView(TestCase):
    BaseView = DeletedObjectsView
    base_template = 'common/layout/base_confirm_delete.html'

    def setUp(self) -> None:
        class DummyView(self.BaseView):
            model = User
            success_url = reverse_lazy('core:index')

        self.View = DummyView
        self.user_to_delete: User = baker.make_recipe('registration.user')
        self.user: User = baker.make_recipe('registration.superuser')
        self.factory = RequestFactory()

    def test_access_with_correct_template_ok(self):
        request = self.factory.get('/users/delete')
        response = self.View.as_view()(request, pk=self.user_to_delete.pk)

        self.assertListEqual(response.template_name, [self.base_template])

    def test_get_deleted_objects_for_given_object_ok(self):
        request = self.factory.get('/users/delete')
        objects_to_delete = self.View(
            request=request, pk=self.user_to_delete.pk
        ).get_deleted_objects(self.user)

        # Since this method returns {ModelClass: [instance1, instance2, ...]} we check for a user and its profile
        self.assertIn(self.user, objects_to_delete)
        self.assertIn([self.user.profile], objects_to_delete)
        self.assertEqual(len(objects_to_delete), 2)
