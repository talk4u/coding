from django.apps import apps
from django.test import TestCase

from api.apps import ApiConfig


class ApiConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ApiConfig.name, 'api')
        self.assertEqual(apps.get_app_config('api').name, 'api')
