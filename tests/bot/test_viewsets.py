from django.apps import apps
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from common.constants import models

DiscordServer = apps.get_model(models.DISCORD_SERVER_MODEL)
DiscordTextChannel = apps.get_model(models.DISCORD_TEXT_CHANNEL_MODEL)


class TestDiscordServerViewSet(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.client = APIClient()
        self.user = baker.make(get_user_model())
        self.url = reverse('bot:discordserver-list')

    def test_access_ok(self):
        entries = self.faker.random_int(1, 10)
        baker.make(DiscordServer, entries)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, 'User cannot access.')
        self.assertEqual(entries, len(response.data), 'Not all entries are being listed.')

    def test_anonymous_user_ko(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'Anonymous user can access.')

    def test_post_request_ko(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'User can make post request.')
        msg = 'You do not have permission to perform this action.'
        self.assertEqual(msg, response.json()['detail'], 'Message is incorrect.')

    def test_put_request_ko(self):
        discord_server = baker.make(DiscordServer)
        self.client.force_authenticate(user=self.user)
        url = reverse('bot:discordserver-detail', kwargs={'pk': discord_server.pk})
        response = self.client.put(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'User can make delete request.')
        msg = 'You do not have permission to perform this action.'
        self.assertEqual(msg, response.json()['detail'], 'Message is incorrect.')

    def test_delete_request_ko(self):
        discord_server = baker.make(DiscordServer)
        self.client.force_authenticate(user=self.user)
        url = reverse('bot:discordserver-detail', kwargs={'pk': discord_server.pk})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'User can make delete request.')
        msg = 'You do not have permission to perform this action.'
        self.assertEqual(msg, response.json()['detail'], 'Message is incorrect.')


class TestDiscordTextChannelViewSet(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.client = APIClient()
        self.user = baker.make(get_user_model())
        self.url = reverse('bot:discordtextchannel-list')

    def test_access_ok(self):
        entries = self.faker.random_int(1, 10)
        baker.make(DiscordTextChannel, entries)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code, 'User cannot access.')
        self.assertEqual(entries, len(response.data), 'Not all entries are being listed.')

    def test_anonymous_user_ko(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'Anonymous user can access.')

    def test_post_request_ko(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'User can make post request.')
        msg = 'You do not have permission to perform this action.'
        self.assertEqual(msg, response.json()['detail'], 'Message is incorrect.')

    def test_put_request_ko(self):
        discord_server = baker.make(DiscordTextChannel)
        self.client.force_authenticate(user=self.user)
        url = reverse('bot:discordtextchannel-detail', kwargs={'pk': discord_server.pk})
        response = self.client.put(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'User can make delete request.')
        msg = 'You do not have permission to perform this action.'
        self.assertEqual(msg, response.json()['detail'], 'Message is incorrect.')

    def test_delete_request_ko(self):
        discord_server = baker.make(DiscordTextChannel)
        self.client.force_authenticate(user=self.user)
        url = reverse('bot:discordtextchannel-detail', kwargs={'pk': discord_server.pk})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code, 'User can make delete request.')
        msg = 'You do not have permission to perform this action.'
        self.assertEqual(msg, response.json()['detail'], 'Message is incorrect.')
