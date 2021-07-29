from django.apps import apps
from django.test import TestCase

from api.apps import ApiConfig
from bot.apps import BotConfig
from chat.apps import ChatConfig
from common.apps import CommonConfig
from core.apps import CoreConfig
from dynamic_menu.apps import DynamicMenuConfig


class TestApps(TestCase):
    def test_api_app_ok(self):
        self.assertEqual(ApiConfig.name, 'api')
        self.assertEqual(apps.get_app_config('api').verbose_name, 'API')

    def test_bot_app_ok(self):
        self.assertEqual(BotConfig.name, 'bot')
        self.assertEqual(apps.get_app_config('bot').verbose_name, 'Bot')

    def test_chat_app_ok(self):
        self.assertEqual(ChatConfig.name, 'chat')
        self.assertEqual(apps.get_app_config('chat').verbose_name, 'Chat')

    def test_common_app_ok(self):
        self.assertEqual(CommonConfig.name, 'common')
        self.assertEqual(apps.get_app_config('common').verbose_name, 'common utils')

    def test_core_app_ok(self):
        self.assertEqual(CoreConfig.name, 'core')
        self.assertEqual(apps.get_app_config('core').verbose_name, 'oil & rope source')

    def test_dynamic_menu_app_ok(self):
        self.assertEqual(DynamicMenuConfig.name, 'dynamic_menu')
        self.assertEqual(apps.get_app_config('dynamic_menu').verbose_name, 'dynamic menu')
