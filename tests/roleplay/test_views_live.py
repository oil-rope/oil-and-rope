import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox import options as firefox_options

from roleplay import enums, models, views


class TestSessionCreateView(StaticLiveServerTestCase):
    fake = Faker()
    login_url = reverse('registration:login')
    model = models.Session
    resolver = 'roleplay:session:create'
    template = 'roleplay/session/session_create.html'
    view = views.SessionCreateView

    def setUp(self):
        self.world = baker.make(models.Place, site_type=enums.SiteTypes.WORLD)
        self.url = reverse(self.resolver)
        self.url = f'{self.live_server_url}{self.url}'

        self.options = firefox_options.Options()
        self.options.headless = True
        self.browser = webdriver.Firefox(options=self.options)

        # SetUp for logging user
        self.user = baker.make(get_user_model())
        self.client.force_login(self.user)
        self.session_cookie = self.client.cookies['sessionid']
        self.browser.get(self.url)
        self.browser.add_cookie({
            'name': 'sessionid', 'value': self.session_cookie.value,
            'secure': False, 'path': '/'
        })
        self.browser.refresh()

    def tearDown(self):
        self.browser.close()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_user_fills_form_ok(self):
        self.browser.get(self.url)

        # User types name
        name = self.fake.word()
        name_input = self.browser.find_element_by_name('name')
        name_input.send_keys(name)

        # User selects PATHFINDER
        system_select = self.browser.find_element_by_name('system')
        pathfinder_selection = enums.RoleplaySystems.PATHFINDER
        option = system_select.find_element_by_xpath(f'option[@value={pathfinder_selection}]')
        option.click()

        # User selects a World
        world_select = self.browser.find_element_by_name('world')
        option = world_select.find_element_by_xpath(f'option[@value={self.world.pk}]')
        option.click()

        # User types a description
        description = self.fake.paragraph()
        description_input = self.browser.find_element_by_name('description')
        description_input.send_keys(description)

        # User types next game
        next_game_date = timezone.datetime(2020, 10, 11, 21, 30)

        typed_date = next_game_date.strftime('%Y-%m-%d')
        ng_date_input = self.browser.find_element_by_name('next_game_date')
        ng_date_input.click()
        ng_date_input.send_keys(typed_date)

        typed_time = next_game_date.strftime('%H:%M')
        ng_time_input = self.browser.find_element_by_name('next_game_time')
        ng_time_input.click()
        ng_time_input.send_keys(typed_time)

        # Adds email
        email = self.fake.email()
        email_input = self.browser.find_element_by_name('invite_player_input')
        email_input.send_keys(email)
        email_input.send_keys(Keys.ENTER)  # Enters email

        # Submitting form
        submit_button = self.browser.find_element_by_name('submit')
        self.browser.execute_script('arguments[0].click();', submit_button)
        time.sleep(.5)  # Waits for the form to be submitted

        result = self.model.objects.filter(
            name=name, description=description, system=pathfinder_selection
        ).count()

        self.assertEqual(1, result, 'Session is not created')
        time.sleep(.5)  # Email may need some time to be sent
        self.assertEqual(1, len(mail.outbox), 'Users are not being mailed')
