import pytest
from django.shortcuts import reverse
from django.test import Client


@pytest.mark.django_db
def test_access_login(client: Client):
    response = client.get(reverse('registration:login'))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_cannot_access_login_page_when_logged(admin_client: Client):
    response = admin_client.get(reverse('registration:login'))
    assert 302 == response.status_code
