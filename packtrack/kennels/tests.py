from django.test import TestCase

from .models import Kennel
from django.contrib.auth.models import User


class KennelTest(TestCase):

    def setUp(self) -> None:
        user1 = User.objects.create(username='user1')
        kennel1 = Kennel.objects.create(name='kennel1',
                                        acronym='1',
                                        city='anchorage ak')
