from django.shortcuts import reverse
from django.test import Client, TestCase


class AccessRouteTest(TestCase):
    """
    Checks if all routes are accesible with correct permissions.
    """

    def setUp(self):
        self.client = Client()

    def test_access_index(self):
        """
        Checks accesibility for :class:`IndexView`.
        """

        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200, 'IndexView is not visible.')
