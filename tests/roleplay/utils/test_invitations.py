import random
import time
from typing import cast

from django.core import mail
from django.core.signing import Signer
from django.test import RequestFactory, TestCase
from model_bakery import baker

from common.tools.crypt import get_token
from common.utils import create_faker
from registration.models import User
from roleplay.models import Campaign
from roleplay.utils.invitations import send_campaign_invitations

faker = create_faker()


class TestInvitations(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user: User = baker.make_recipe('registration.user')
        cls.campaign: Campaign = baker.make_recipe('roleplay.campaign')
        cls.factory = RequestFactory()

    def setUp(self) -> None:
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_send_campaign_invitations_without_optional_values_ok(self):
        send_campaign_invitations(
            campaign=self.campaign,
            request=self.request,
            emails=[faker.safe_email() for _ in range(3)],
        )

        # Waiting for emails to be sent
        time.sleep(0.5)
        # Checking the 3 emails have been sent
        self.assertEqual(3, len(mail.outbox))

    def test_send_campaign_invitations_with_subject_ok(self):
        subject = faker.sentence()
        send_campaign_invitations(
            campaign=self.campaign,
            request=self.request,
            emails=[faker.safe_email() for _ in range(3)],
            subject=subject,
        )

        # Waiting for emails to be sent
        time.sleep(0.5)
        # Getting any random email since all of them have the same subject
        email = random.choice(mail.outbox)
        self.assertEqual(subject, email.subject)

    def test_send_campaign_invitations_with_signer_ok(self):
        signer = Signer()
        send_campaign_invitations(
            campaign=self.campaign,
            request=self.request,
            emails=[faker.safe_email() for _ in range(3)],
            signer=signer,
        )

        # Waiting for emails to be sent
        time.sleep(0.5)
        # Since it's HTML what we are looking for it's on alternatives
        email = random.choice(mail.outbox)
        # Format is tuple[HTML, content-type]
        content = cast(tuple[str, str], email.alternatives)[0][0]  # It should be only one item with HTML
        token = get_token(email.to[0])  # Since `signer` is already `Signer()` we don't need to explicitly declare it
        self.assertIn(member=token, container=content)
