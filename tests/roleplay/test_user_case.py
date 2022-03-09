from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import resolve_url
from django.test import tag
from model_bakery import baker
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from common.utils.faker import create_faker
from roleplay import enums, models

fake = create_faker()


@tag('slow', 'selenium')
class SeleniumPlaceDetail(StaticLiveServerTestCase):
    model = models.Place
    resolver = 'roleplay:place:detail'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        cls.browser = webdriver.Firefox(options=options)
        cls.browser.implicitly_wait(2)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        return super().tearDownClass()

    def setUp(self):
        self.owner = baker.make_recipe('registration.user')
        self.password = fake.password()
        self.owner.set_password(self.password)
        self.owner.save(update_fields=['password'])

        self.public_world = self.model.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            site_type=enums.SiteTypes.WORLD,
            owner=self.owner,
        )
        self.public_world_url = f'{self.live_server_url}{resolve_url(self.public_world)}'

    def selenium_login(self, user=None, password=None):
        if not user:
            user = baker.make_recipe('registration.user')
            password = fake.password() if not password else password
            user.set_password(password)
            user.save(update_fields=['password'])

        login_url = resolve_url('registration:auth:login')
        self.browser.get(f'{self.live_server_url}{login_url}')
        username_input = self.browser.find_element(by=By.NAME, value='username')
        username_input.send_keys(user.username)
        password_input = self.browser.find_element(by=By.NAME, value='password')
        password_input.send_keys(password)
        # NOTE: This button click doesn't seem legible
        submit_button = self.browser.find_element(by=By.NAME, value='login')
        self.browser.execute_script('window.scrollTo(0, 200)')
        submit_button.click()

    def test_not_owner_does_not_see_dangerous_options_ok(self):
        self.selenium_login()
        self.browser.get(self.public_world_url)
        self.browser.find_element(by=By.XPATH, value='//button[normalize-space()="Options"]').click()

        with self.assertRaises(NoSuchElementException):
            self.browser.find_element(by=By.XPATH, value='//[normalize-space()="Edit"]')

    def test_owner_see_all_options_ok(self):
        self.selenium_login(user=self.owner, password=self.password)
        self.browser.get(self.public_world_url)
        self.browser.find_element(by=By.XPATH, value='//button[normalize-space()="Options"]').click()

        self.browser.find_element(by=By.LINK_TEXT, value='Add geography')
        self.browser.find_element(by=By.LINK_TEXT, value='Edit')
        self.browser.find_element(by=By.LINK_TEXT, value='Delete')
